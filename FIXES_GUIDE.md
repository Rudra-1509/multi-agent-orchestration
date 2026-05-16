# Quick Reference: Critical Issues to Fix

## 🔴 BLOCKING ISSUES (Fix First)

### Issue #1: Missing Streaming Endpoint
**Impact:** Frontend cannot connect to real-time events  
**File:** `backend/app/api/main.py`

**Current:** No endpoint defined for `/api/stream/{task_id}`

**Solution:**
```python
from fastapi.responses import StreamingResponse

@app.get("/api/stream/{task_id}")
async def stream_task(task_id: str):
    """Server-Sent Events stream for a task"""
    task = get_task(task_id)
    
    async def event_generator():
        last_idx = 0
        while True:
            with _tasks_lock:
                current_events = task.get("event_log", [])[last_idx:]
            
            for event in current_events:
                yield f"data: {json.dumps(event)}\n\n"
                last_idx += 1
            
            if task.get("status") in ["completed", "failed"]:
                break
            
            await asyncio.sleep(0.5)
        
        yield "event: done\ndata: {}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"}
    )
```

---

### Issue #2: Python Code Execution Security
**Impact:** Arbitrary code execution vulnerability  
**File:** `backend/app/tools/code/python_repl_tool.py`

**Current:**
```python
@tool
def code_tool(code: str)-> str:
    results=python_repl.run(code)  # No restrictions!
    return results
```

**Solution Options:**
1. **Use RestrictedPython** (lightweight):
```python
from restricted_exec import safe_globals, guarded_inplacebinary_op
from restrictedpython import compile_restricted

@tool
def code_tool(code: str) -> str:
    try:
        byte_code = compile_restricted(code, '<string>', 'exec')
        if byte_code.errors:
            return f"Syntax errors: {byte_code.errors}"
        
        safe_dict = {"__builtins__": safe_globals}
        exec(byte_code, safe_dict)
        return str(safe_dict.get("result", "Success"))
    except Exception as e:
        return f"Error: {str(e)}"
```

2. **Use Docker container** (most secure):
```python
import docker

def safe_execute_code(code: str) -> str:
    client = docker.from_env()
    try:
        result = client.containers.run(
            "python:3.11-slim",
            f"python -c '{code}'",
            timeout=5,
            memory_limit='256m'
        )
        return result
    except Exception as e:
        return f"Error: {str(e)}"
```

---

### Issue #3: Task Memory Leak
**Impact:** Memory exhaustion in production  
**File:** `backend/app/api/main.py`

**Current:**
```python
_tasks: TaskStore = {}  # Never cleaned up
```

**Solution:**
```python
import time
from datetime import datetime, timedelta

TASK_RETENTION_HOURS = 1  # Keep tasks for 1 hour

async def cleanup_old_tasks():
    """Background task to clean up old tasks"""
    while True:
        try:
            with _tasks_lock:
                now = datetime.utcnow()
                to_delete = []
                
                for task_id, task in _tasks.items():
                    created = datetime.fromisoformat(task["created_at"].replace("Z", ""))
                    if now - created > timedelta(hours=TASK_RETENTION_HOURS):
                        to_delete.append(task_id)
                
                for task_id in to_delete:
                    del _tasks[task_id]
            
            await asyncio.sleep(300)  # Check every 5 minutes
        except Exception as e:
            print(f"Cleanup error: {e}")
            await asyncio.sleep(60)

# Start cleanup on app startup
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(cleanup_old_tasks())
```

---

### Issue #4: EventSource Missing ID Field
**Impact:** React key warnings, list items not properly tracked  
**File:** `frontend/src/context/orchestration-context.tsx`

**Current:**
```typescript
const event: StreamEvent = {
  event: String(data.event || "agent_thought"),
  agent_name: String(data.agent || "System"),
  timestamp: String(data.timestamp || new Date().toISOString()),
  data: String(data.message || ""),
  // MISSING id field
};
```

**Solution:**
```typescript
import { v4 as uuidv4 } from 'uuid'; // Add uuid package

const event: StreamEvent = {
  id: uuidv4(),  // Add this
  event: String(data.event || "agent_thought"),
  agent_name: String(data.agent || "System"),
  timestamp: String(data.timestamp || new Date().toISOString()),
  data: String(data.message || ""),
};
```

---

### Issue #5: Hardcoded API_BASE and CORS
**Impact:** Breaks in production/deployment  
**Files:** 
- `frontend/src/context/orchestration-context.tsx` (line 8)
- `backend/app/api/main.py` (line 19)

**Frontend Solution:**
```typescript
// frontend/src/context/orchestration-context.tsx
const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";
```

Create `.env` file:
```
VITE_API_URL=http://your-backend-url:8000
```

**Backend Solution:**
```python
# backend/app/api/main.py
import os

ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:5173"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)
```

Create `.env` file:
```
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,https://your-frontend-url.com
```

---

## 🟠 HIGH PRIORITY

### Issue #6: Environment Variable Validation
**File:** `backend/app/agents/superviser.py`

**Current:** Fails at runtime when LLM is invoked

**Solution:**
```python
# Create new file: backend/app/config.py
from dotenv import load_dotenv
import os

load_dotenv()

def validate_env_vars():
    required = ["GROQ_API_TOKEN", "TAVILY_API_KEY"]
    missing = [var for var in required if not os.getenv(var)]
    
    if missing:
        raise RuntimeError(
            f"Missing environment variables: {', '.join(missing)}\n"
            f"Please set them in .env file"
        )

# Call at startup in main.py
from app.config import validate_env_vars

@app.on_event("startup")
def startup():
    validate_env_vars()
```

---

### Issue #7: Task Timeout Mechanism
**File:** `backend/app/api/main.py`

**Problem:** Long-running tasks hang forever

**Solution:**
```python
import signal
from contextlib import contextmanager

class TimeoutException(Exception):
    pass

@contextmanager
def timeout(seconds):
    def timeout_handler(signum, frame):
        raise TimeoutException(f"Task timed out after {seconds}s")
    
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)

def run_task(task_id: str) -> None:
    task = get_task(task_id)
    with _tasks_lock:
        task["status"] = "running"
    
    try:
        with timeout(300):  # 5 minute timeout
            graph_output = _supervisor_graph.invoke(...)
            # ... rest of logic
    except TimeoutException as e:
        with _tasks_lock:
            task["status"] = "failed"
            task["finished_at"] = now_iso()
        append_task_event(task, "system", "error", str(e))
```

---

### Issue #8: JSON Parsing Robustness
**File:** `backend/app/agents/superviser.py`

**Current:** Brittle string searching

**Solution:**
```python
import json
import re

def extract_json_from_text(text: str) -> dict:
    """Extract JSON object from potentially malformed text"""
    # Try direct parsing first
    try:
        return json.loads(text)
    except:
        pass
    
    # Try finding JSON object patterns
    json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text)
    if json_match:
        try:
            return json.loads(json_match.group())
        except:
            pass
    
    # Fallback
    return {"agent": "end", "reasoning": "Failed to parse LLM response"}

# In supervisor_node:
decision = extract_json_from_text(response_text)
selected_agent = decision.get("agent", "end")
reasoning = decision.get("reasoning", "No reasoning provided")
```

---

## 🟡 MEDIUM PRIORITY

### Issue #9: Add Retry Logic
**File:** `frontend/src/context/orchestration-context.tsx`

```typescript
async function fetchWithRetry(
  url: string,
  options: RequestInit,
  maxRetries = 3
): Promise<Response> {
  let lastError;
  
  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await fetch(url, options);
      if (response.ok) return response;
      lastError = response;
    } catch (err) {
      lastError = err;
      if (i < maxRetries - 1) {
        await new Promise(r => setTimeout(r, 1000 * Math.pow(2, i)));
      }
    }
  }
  
  throw lastError;
}

// Usage in start():
const response = await fetchWithRetry(`${API_BASE}/api/task`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ query: prompt, messages: [...] }),
});
```

---

### Issue #10: Type Safety for StreamEvent
**File:** `frontend/src/context/orchestration-context.tsx`

```typescript
// Validate event types
function isValidEventType(value: unknown): value is EventType {
  const validTypes: EventType[] = [
    "agent_start",
    "agent_thought",
    "tool_start",
    "tool_end",
    "agent_output",
    "require_approval",
    "artifact",
    "agent_complete",
  ];
  return typeof value === "string" && validTypes.includes(value as EventType);
}

// In SSE handler:
const eventType = data.event || "agent_thought";
if (!isValidEventType(eventType)) {
  console.warn(`Invalid event type: ${eventType}`);
  return;
}

const event: StreamEvent = {
  id: uuidv4(),
  event: eventType,
  // ...rest
};
```

