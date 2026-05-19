# 🔍 Codebase Issues Report

## Critical Issues

### 1. **Backend: Missing Streaming Endpoint** 
**File:** [backend/app/api/main.py](backend/app/api/main.py)  
**Severity:** CRITICAL
- The frontend subscribes to `GET /api/stream/{id}` but this endpoint is **not defined** in the API
- This will cause 404 errors and break the entire real-time event streaming
- **Fix needed:** Add SSE streaming endpoint

```python
@app.get("/api/stream/{task_id}")
async def stream_task(task_id: str):
    # SSE implementation missing
```
 
Status: RESOLVED — `/api/stream/{task_id}` implemented in `backend/app/api/main.py` and returns SSE events. Frontend successfully connects to this endpoint.
---

### 2. **Frontend: Unsafe Type Casting**
**File:** [frontend/src/context/orchestration-context.tsx](frontend/src/context/orchestration-context.tsx) (line ~70)  
**Severity:** HIGH
```typescript
const data = JSON.parse(ev.data) as Record<string, unknown>;
// Then accessing properties without type validation
const event: StreamEvent = {
  event: String(data.event || "agent_thought"),  // Will create invalid EventType
  agent_name: String(data.agent || "System"),
  timestamp: String(data.timestamp || new Date().toISOString()),
  data: String(data.message || ""),
};
```
- No validation that `data.event` is a valid `EventType`
- `String()` coercion can hide bugs
- **Fix:** Validate against `EventType` enum

Status: RESOLVED — `orchestration-context.tsx` now validates incoming SSE events against a known `EVENT_TYPES` list, performs type checks, and assigns `id` values. Coercion issues have been addressed.
---

### 3. **Backend: Memory Leak - Unbounded Task Storage**
**File:** [backend/app/api/main.py](backend/app/api/main.py) (line 33)  
**Severity:** HIGH
```python
_tasks: TaskStore = {}  # Never cleaned up
```
- Tasks accumulate indefinitely in memory
- No garbage collection or TTL mechanism
- Production deployments will crash with memory exhaustion
- **Fix:** Implement task expiration (e.g., 1 hour TTL) and cleanup background job
 
Status: PARTIALLY RESOLVED — A `cleanup_expired_tasks()` function and `TASK_TTL_SECONDS` constant have been added; `run_task` calls cleanup on start. Recommendation: schedule `cleanup_expired_tasks` as a periodic background task on startup to guarantee regular cleanup.
---

### 4. **Backend: CORS Hardcoded to Localhost**
**File:** [backend/app/api/main.py](backend/app/api/main.py) (lines 19-27)  
**Severity:** MEDIUM
```python
allow_origins=[
    "http://localhost:3000", 
    "http://127.0.0.1:3000",
    "http://localhost:8080",   
    "http://127.0.0.1:8080",   
    "http://localhost:5173"    
],
```
- Won't work in production/deployed environments
- Missing env-based configuration
- **Fix:** Use environment variable for allowed origins
 
Status: RESOLVED — CORS origins are now configurable via `CORS_ALLOW_ORIGINS` environment variable with sensible defaults.
---

### 5. **Python Code Execution Without Sandboxing**
**File:** [backend/app/tools/code/python_repl_tool.py](backend/app/tools/code/python_repl_tool.py)  
**Severity:** CRITICAL SECURITY
```python
python_repl=PythonREPL()

@tool
def code_tool(code: str)-> str:
    """Executes Python commands."""
    try:
        results=python_repl.run(code)  # No sandboxing!
        return results
    except Exception as e:
        return f"Error in repl tool: {str(e)}"
```
- **Anyone can execute arbitrary Python code** on the server
- No validation, no sandboxing, no resource limits
- Can delete files, access environment variables, etc.
- **Fix:** Implement sandboxing (Docker/RestrictedPython/etc.)
 
Status: PARTIALLY RESOLVED — `python_repl_tool.py` now performs AST-based static checks to block imports, file/system calls, and other risky constructs. This is a useful mitigation but not a full sandbox. Strong recommendation: run user code inside a container or use a hardened sandbox (e.g., RestrictedPython or an isolated Docker runner) for production.
---

## High Priority Issues

### 6. **Brittle JSON Parsing from LLM Response**
**File:** [backend/app/agents/superviser.py](backend/app/agents/superviser.py) (lines 100-115)  
**Severity:** HIGH
```python
if "{" in response_text and "}" in response_text:
    json_str = response_text[response_text.find("{"):response_text.rfind("}")+1]
    decision = json.loads(json_str)
```
- Simple substring search can break on multi-line JSON or nested objects
- No validation of parsed structure
- Falls back silently to "end" agent on any error
- **Fix:** Use proper JSON extraction library or structured output format (e.g., Pydantic)
 
Status: RESOLVED — `superviser.py` now uses a Pydantic `RouteDecision` model and `model_validate_json` to parse and validate the LLM response JSON, improving robustness.
---

### 7. **EventSource Never Explicitly Closed in Error Cases**
**File:** [frontend/src/context/orchestration-context.tsx](frontend/src/context/orchestration-context.tsx) (line ~130+)  
**Severity:** HIGH
```typescript
source.onerror = () => {
  setError("Connection lost while streaming task events.");
  setIsStreaming(false);
  source.close();  // Only closed here
};
```
- EventSource could remain open on network errors
- Component unmount calls `stop()` but may not always execute properly
- **Fix:** Add try-finally or cleanup effect guards
 
Status: RESOLVED — `orchestration-context.tsx` now closes the `EventSource` and clears the ref in both `onerror` and the `done` listener; `stop()` uses the ref to ensure the source is closed on unmount/restart.
---

### 8. **Missing Tool Existence Checks (Partial)**
**File:** [backend/app/agents/subagents/executor.py](backend/app/agents/subagents/executor.py) (line 12)  
**Severity:** MEDIUM
```python
output_tool = next((tool for tool in file_tools["output"] if "write_file" in tool.name), None)
```
- Returns `None` if tool not found (good)
- But this pattern is only used for `output_tool`, not consistently across all subagents
- `input_read_tool` has same issue in [writer.py](backend/app/agents/subagents/writer.py)
 
Status: RESOLVED — subagents now defensively check for existence of file tools before invoking them (e.g., `input_read_tool`, `output_write_tool`). Existing code paths include fallbacks and skip behavior when tools are absent.
---

### 9. **Frontend: No Retry Logic for API Calls**
**File:** [frontend/src/context/orchestration-context.tsx](frontend/src/context/orchestration-context.tsx) (line ~155)  
**Severity:** MEDIUM
```typescript
const response = await fetch(`${API_BASE}/api/task`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    query: prompt,
    messages: [{ role: "user", content: prompt }],
  }),
});
```
- Single attempt, no retries
- Network failures will immediately show error to user
- No exponential backoff
 
Status: RESOLVED — `createTaskWithRetry` implements retry with exponential backoff for `/api/task` creation.
---

### 10. **Backend: No Task Timeout Mechanism**
**File:** [backend/app/api/main.py](backend/app/api/main.py)  
**Severity:** HIGH
```python
def run_task(task_id: str) -> None:
    task = get_task(task_id)
    # No timeout check - if graph hangs, thread stays alive forever
    graph_output = _supervisor_graph.invoke(...)
```
- Long-running tasks can hang indefinitely
- Thread pool exhaustion possible
- No way to cancel stuck tasks
 
Status: PARTIALLY RESOLVED — `run_task` now uses a `ThreadPoolExecutor` with `future.result(timeout=TASK_TIMEOUT_SECONDS)` to limit graph execution time. NOTE: there is a duplicate call to `_supervisor_graph.invoke(...)` after the threaded call which should be removed to avoid running the graph twice; remove the second direct invoke to complete this fix.
---

## Medium Priority Issues

### 11. **Unvalidated Environment Variables**
**File:** [backend/app/agents/superviser.py](backend/app/agents/superviser.py) (lines 14-21)  
**Severity:** MEDIUM
```python
def get_llm() -> ChatGroq:
    groq_token = os.getenv("GROQ_API_TOKEN") or os.getenv("GROQ_API_KEY")
    if not groq_token:
        raise RuntimeError(...)  # Fails at runtime, not startup
```
- Error only occurs when LLM is first invoked, not at app startup
- **Fix:** Validate all required env vars in `app.main()` at startup

Status: PARTIALLY RESOLVED — `superviser.py` uses `load_dotenv()` and `get_llm()` now raises if the GROQ token is missing. Recommend validating required environment variables at application startup to fail fast.

---

### 12. **Mock Data in Production Code**
**File:** [backend/app/agents/subagents/analyst.py](backend/app/agents/subagents/analyst.py) (lines 20-23)  
**Severity:** MEDIUM
```python
def extract_node(state: AgentState) -> AgentState:
    insights = [
        "Insight 1: Primary data trends correlate with ...",  # Hardcoded!
        "Insight 2: Identified significant volume of abstract values.",
        "Insight 3: The data context establishes clear action points."
    ]
```
- Returns fake insights regardless of input
- Not actually performing analysis
- **Fix:** Implement actual LLM-based analysis or remove mock

Status: OPEN — `analyst.py` still contains mocked insight strings; a real analysis implementation or LLM call should replace these stubs.

---

### 13. **Unused Import & Incomplete Cleanup**
**File:** [backend/app/agents/superviser.py](backend/app/agents/superviser.py)  
**Severity:** LOW
```python
def supervisor_node(state: AgentState) -> AgentState:
    routing_prompt = f"""..."""
    
    try:
        response = get_llm().invoke([HumanMessage(content=routing_prompt)])
        import json  # Should be at module level
```
- `json` imported inside function instead of at module level

Status: RESOLVED — `json` is now imported at module level in `superviser.py` and parsing uses Pydantic validation.

---

### 14. **Type Issues in TypedDict**
**File:** [backend/app/graph/state.py](backend/app/graph/state.py)  
**Severity:** MEDIUM
```python
class AgentState(TypedDict, total=False):
    query: str
    selected_agent: str
    messages: List[Dict[str, Any]]  # Very loose type
    event_log: List[Dict[str, Any]]  # Should be typed as Event
```
- Too loose `Dict[str, Any]` types
- **Fix:** Create proper Pydantic models and use them instead

Status: OPEN — `AgentState` remains a loose `TypedDict`. Consider migrating to Pydantic models for stronger validation and clearer schemas.

---

### 15. **Frontend: Missing ID Field in StreamEvent**
**File:** [frontend/src/context/orchestration-context.tsx](frontend/src/context/orchestration-context.tsx)  
**Severity:** MEDIUM
```typescript
const event: StreamEvent = {
  event: String(data.event || "agent_thought"),
  agent_name: String(data.agent || "System"),
  timestamp: String(data.timestamp || new Date().toISOString()),
  data: String(data.message || ""),
  // Missing: id field (used in map keys later)
};
```
- `StreamEvent.id` is required (used as React key in [AgentTimeline.tsx](frontend/src/components/orchestration/AgentTimeline.tsx))
- Will cause missing key warnings

Status: RESOLVED — the frontend now attaches stable `id` values (e.g., `crypto.randomUUID()`) to `StreamEvent` entries.

---

### 16. **Frontend: Missing Error Boundary**
**File:** [frontend/src/routes/index.tsx](frontend/src/routes/index.tsx)  
**Severity:** MEDIUM
- No error boundary wrapper
- Components can crash without graceful recovery
- User sees blank page instead of error message

Status: OPEN — no global React error boundary detected; consider adding one around the app root to catch rendering errors.

---

### 17. **Incomplete SessionStorage/History**
**File:** [frontend/src/context/orchestration-context.tsx](frontend/src/context/orchestration-context.tsx) (line ~43)  
**Severity:** LOW
```typescript
const INITIAL_SESSIONS: Session[] = [
  { id: "s_now", title: "Live Agent Session", ... },
];
```
- Sessions never actually created/stored
- UI shows session history but doesn't persist or manage them
- **Fix:** Implement localStorage persistence

Status: OPEN — sessions are still in-memory only (`INITIAL_SESSIONS`). Implement localStorage or server-side session persistence if needed.

---

## Low Priority Issues

### 18. **SpellCheck Issues**
**File:** [backend/app/agents/superviser.py](backend/app/agents/superviser.py)  
**Severity:** LOW
- Comment typo: "FIX: Increased truncation limit to 4000 to preserve **agent insights**"
  - Should reference agent insights more clearly in context

  Status: RESOLVED — minor comment cleaned up as part of supervisor refactor.

---

### 19. **Inconsistent Error Messaging**
**File:** Multiple files  
**Severity:** LOW
- Error messages vary in format and detail
- Some include full stack traces, others are generic
- **Fix:** Create error response formatter utility

Status: OPEN — error messages are still inconsistent across modules; consider centralizing error formatting/logging.

---

### 20. **Frontend: API_BASE Hardcoded**
**File:** [frontend/src/context/orchestration-context.tsx](frontend/src/context/orchestration-context.tsx) (line 8)  
**Severity:** MEDIUM
```typescript
const API_BASE = "http://localhost:8000";
```
- Won't work outside localhost
- **Fix:** Use `import.meta.env.VITE_API_URL` or similar

Status: RESOLVED — `API_BASE` now reads from `import.meta.env.VITE_API_URL` with a localhost fallback.

---

### 21. **Duplicate Code**
**Files:** [frontend/package.json](frontend/package.json) and [agent-hub/package.json](agent-hub/package.json)  
**Severity:** LOW
- Both have identical package.json structure (same dependencies)
- Likely a duplicate frontend setup
- **Fix:** Determine which is active; remove redundant one

Status: OPEN — duplicate front-end manifests exist (`frontend/` vs `agent-hub/`); verify intended active directory and consolidate.

---

## Summary by Category

| Category | Count | Severity |
|----------|-------|----------|
| Security | 1 | 🔴 Critical |
| Architecture | 3 | 🔴 Critical |
| Type Safety | 3 | 🟠 High |
| API/Integration | 3 | 🟠 High |
| Configuration | 3 | 🟡 Medium |
| Performance | 2 | 🟡 Medium |
| Quality | 3 | 🟢 Low |

---

## Quick Fix Priority List

1. **Add `/api/stream/{task_id}` endpoint** (blocks entire app)
2. **Sandbox Python REPL execution** (security risk)
3. **Implement task cleanup mechanism** (memory leak)
4. **Fix missing StreamEvent.id field** (UI crashes)
5. **Add environment variable validation** (startup fails)
6. **Implement task timeouts** (resource exhaustion)
7. **Add retry logic to API calls** (UX improvement)
8. **Validate EventType in SSE handler** (data corruption)
9. **Use env-based CORS/API_BASE** (deployment blocker)
10. **Improve JSON parsing from LLM** (reliability)

