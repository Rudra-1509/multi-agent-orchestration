import asyncio
import json
import threading
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.agents.superviser import (
    aggregate_node,
    analyst_node,
    executor_node,
    researcher_node,
    supervisor_node,
    writer_node,
)
from app.graph.state import AgentState

app = FastAPI(title="Multi-Agent Orchestration API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "http://localhost:8080",   
        "http://127.0.0.1:8080",   
        "http://localhost:5173"    
                   ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

TaskStore = Dict[str, Any]
_tasks: TaskStore = {}
_tasks_lock = threading.Lock()


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
    task["event_log"].append(build_event(agent, event, message))
    task["last_updated"] = now_iso()


def run_task(task_id: str) -> None:
    task = get_task(task_id)
    task["status"] = "running"
    append_task_event(task, "supervisor", "started", "Starting supervisor routing")

    state: AgentState = {
        "query": task["query"],
        "messages": task["messages"],
        "event_log": [],
    }

    supervisor_output = supervisor_node(state)
    state.update(supervisor_output)

    task["selected_agent"] = state.get("selected_agent")
    task["supervisor_reasoning"] = state.get("supervisor_reasoning")
    append_task_event(
        task,
        "supervisor",
        "routing",
        f"Selected '{task['selected_agent']}' because: {task['supervisor_reasoning']}",
    )

    worker_agent = task["selected_agent"]
    if worker_agent in {
        "researcher",
        "executor",
        "writer",
        "analyst",
    }:
        append_task_event(task, worker_agent, "started", f"Invoking {worker_agent} agent")
        worker_fn = {
            "researcher": researcher_node,
            "executor": executor_node,
            "writer": writer_node,
            "analyst": analyst_node,
        }.get(worker_agent)

        try:
            worker_output = worker_fn(state)
            state.update(worker_output)
            append_task_event(
                task,
                worker_agent,
                "completed",
                f"{worker_agent.capitalize()} finished with status: {state.get('status', 'completed')}",
            )
        except Exception as exc:
            append_task_event(
                task,
                worker_agent,
                "error",
                f"{worker_agent.capitalize()} failed: {str(exc)}",
            )
            state["status"] = f"{worker_agent} error: {str(exc)}"
    else:
        append_task_event(
            task,
            "supervisor",
            "skipped",
            f"No worker invocation required for selected agent '{worker_agent}'",
        )

    append_task_event(task, "aggregate", "started", "Beginning aggregation of worker outputs")
    aggregation_output = aggregate_node(state)
    state.update(aggregation_output)
    task["final_response"] = state.get("final_response")
    append_task_event(task, "aggregate", "completed", "Aggregation complete")
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
