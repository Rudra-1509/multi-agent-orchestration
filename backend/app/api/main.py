import asyncio
import json
import os
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.agents.superviser import build_graph
from app.graph.state import AgentState

app = FastAPI(title="Multi-Agent Orchestration API")

DEFAULT_CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:5173",
]
cors_origins_env = os.getenv("CORS_ALLOW_ORIGINS", "")
ALLOW_ORIGINS = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()] or DEFAULT_CORS_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

TaskStore = Dict[str, Any]
_tasks: TaskStore = {}
_tasks_lock = threading.Lock()
_supervisor_graph = build_graph()
TASK_TTL_SECONDS = int(os.getenv("TASK_TTL_SECONDS", "3600"))
TASK_TIMEOUT_SECONDS = int(os.getenv("TASK_TIMEOUT_SECONDS", "120"))
_cleanup_thread_started = False


class TaskCreate(BaseModel):
    query: str = Field(..., description="The user task prompt or question")
    messages: Optional[List[Dict[str, str]]] = Field(
        default_factory=list,
        description="Optional conversation history to seed the task",
    )


class Event(BaseModel):
    agent: str
    event: str
    message: str
    timestamp: str


class TaskStatusResponse(BaseModel):
    task_id: str
    query: str
    status: str
    selected_agent: Optional[str] = None
    supervisor_reasoning: Optional[str] = None
    final_response: Optional[str] = None
    event_log: List[Event] = Field(default_factory=list)


class TaskResultResponse(BaseModel):
    task_id: str
    final_response: Optional[str] = None
    status: str
    event_log: List[Event] = Field(default_factory=list)


def now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


def build_event(agent: str, event: str, message: str) -> Dict[str, str]:
    return {
        "agent": agent,
        "event": event,
        "message": message,
        "timestamp": now_iso(),
    }


def get_task(task_id: str) -> TaskStore:
    with _tasks_lock:
        task = _tasks.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return task


def append_task_event(task: TaskStore, agent: str, event: str, message: str) -> None:
    with _tasks_lock:
        task["event_log"].append(build_event(agent, event, message))
        task["last_updated"] = now_iso()


def cleanup_expired_tasks() -> None:
    cutoff = datetime.utcnow() - timedelta(seconds=TASK_TTL_SECONDS)
    with _tasks_lock:
        expired = [
            task_id
            for task_id, task in _tasks.items()
            if datetime.fromisoformat(task.get("last_updated", task["created_at"]).replace("Z", "")) < cutoff
        ]
        for task_id in expired:
            _tasks.pop(task_id, None)


def _cleanup_loop() -> None:
    while True:
        try:
            cleanup_expired_tasks()
        except Exception:
            # Keep cleanup loop resilient; task expiration is best-effort housekeeping.
            pass
        time.sleep(60)


def validate_required_env() -> None:
    if not (os.getenv("GROQ_API_TOKEN") or os.getenv("GROQ_API_KEY")):
        raise RuntimeError("Missing required environment variable: GROQ_API_TOKEN (or GROQ_API_KEY)")


@app.on_event("startup")
def startup_tasks() -> None:
    global _cleanup_thread_started
    validate_required_env()
    if not _cleanup_thread_started:
        cleanup_thread = threading.Thread(target=_cleanup_loop, daemon=True)
        cleanup_thread.start()
        _cleanup_thread_started = True


def run_task(task_id: str) -> None:
    cleanup_expired_tasks()
    task = get_task(task_id)
    with _tasks_lock:
        task["status"] = "running"
    append_task_event(task, "supervisor", "started", "Starting supervisor routing")

    state: AgentState = {
        "query": task["query"],
        "messages": task["messages"],
        "event_log": [],
    }

    append_task_event(task, "supervisor", "routing", "Evaluating worker route")
    try:
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(
                _supervisor_graph.invoke,
                {"query": task["query"], "messages": task["messages"], "event_log": []},
            )
            graph_output = future.result(timeout=TASK_TIMEOUT_SECONDS)
        graph_output = _supervisor_graph.invoke(
            {"query": task["query"], "messages": task["messages"], "event_log": []}
        )
        state.update(graph_output)
        selected_agent = state.get("selected_agent")
        if selected_agent:
            with _tasks_lock:
                task["selected_agent"] = selected_agent
                task["supervisor_reasoning"] = state.get("supervisor_reasoning")
            append_task_event(
                task,
                "supervisor",
                "routing",
                f"Selected '{selected_agent}' because: {state.get('supervisor_reasoning', 'no reason provided')}",
            )
            if selected_agent != "end":
                append_task_event(task, selected_agent, "completed", f"{selected_agent.capitalize()} finished execution")
        append_task_event(task, "aggregate", "completed", "Aggregation complete")
    except FuturesTimeoutError:
        with _tasks_lock:
            task["status"] = "failed"
            task["finished_at"] = now_iso()
        append_task_event(task, "supervisor", "error", f"Task timed out after {TASK_TIMEOUT_SECONDS} seconds")
        return
    except Exception as exc:
        with _tasks_lock:
            task["status"] = "failed"
            task["finished_at"] = now_iso()
        append_task_event(task, "supervisor", "error", f"Graph invoke failed: {str(exc)}")
        return

    with _tasks_lock:
        task["final_response"] = state.get("final_response")
    with _tasks_lock:
        task["state"] = state
        task["status"] = "completed"
        task["finished_at"] = now_iso()


@app.post("/api/task", response_model=TaskStatusResponse)
def create_task(
    payload: TaskCreate,
    background_tasks: BackgroundTasks,
) -> TaskStatusResponse:
    task_id = uuid.uuid4().hex
    task: TaskStore = {
        "task_id": task_id,
        "query": payload.query,
        "messages": payload.messages or [],
        "status": "pending",
        "selected_agent": None,
        "supervisor_reasoning": None,
        "final_response": None,
        "event_log": [],
        "created_at": now_iso(),
    }

    with _tasks_lock:
        _tasks[task_id] = task
    cleanup_expired_tasks()

    background_tasks.add_task(run_task, task_id)
    append_task_event(task, "system", "queued", "Task created and queued for execution")

    return TaskStatusResponse(
        task_id=task_id,
        query=task["query"],
        status=task["status"],
        selected_agent=task["selected_agent"],
        supervisor_reasoning=task["supervisor_reasoning"],
        final_response=task["final_response"],
        event_log=task["event_log"],
    )


@app.get("/api/status/{task_id}", response_model=TaskStatusResponse)
def get_status(task_id: str) -> TaskStatusResponse:
    task = get_task(task_id)
    return TaskStatusResponse(
        task_id=task_id,
        query=task["query"],
        status=task["status"],
        selected_agent=task.get("selected_agent"),
        supervisor_reasoning=task.get("supervisor_reasoning"),
        final_response=task.get("final_response"),
        event_log=task["event_log"],
    )


@app.get("/api/results/{task_id}", response_model=TaskResultResponse)
def get_result(task_id: str) -> TaskResultResponse:
    task = get_task(task_id)
    return TaskResultResponse(
        task_id=task_id,
        final_response=task.get("final_response"),
        status=task["status"],
        event_log=task["event_log"],
    )


@app.get("/api/stream/{task_id}")
def stream_task(task_id: str) -> StreamingResponse:
    task = get_task(task_id)

    async def event_generator():
        sent = 0
        while True:
            current_task = get_task(task_id)
            events = current_task["event_log"]
            while sent < len(events):
                event = events[sent]
                sent += 1
                yield f"data: {json.dumps(event)}\n\n"

            if current_task["status"] in {"completed", "failed"}:
                yield "event: done\ndata: done\n\n"
                break

            await asyncio.sleep(0.5)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
