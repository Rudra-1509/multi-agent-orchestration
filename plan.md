# Live Agent Simulation and API Plan

## Current state of the codebase

- `backend/app/agents/superviser.py` is the main orchestration layer.
- The architecture uses a `StateGraph` with:
  - `supervisor` node: routes the task to a specialist worker via an LLM decision.
  - `researcher`, `executor`, `writer`, `analyst` nodes: each invokes a dedicated worker graph.
  - `aggregate` node: combines worker outputs into a final response.
- Worker graph responsibilities:
  - `researcher`: search, clean, scrape, and store data in Chroma.
  - `executor`: retrieve memory, run Python code, save results, store execution output.
  - `writer`: read context, draft content, save a draft file.
  - `analyst`: plan analysis, extract insights, compile a report.
- `backend/app/graph/state.py` defines shared `AgentState`, including routing fields and worker-specific fields.

## What is missing for live simulations and API management

### Missing live simulation features
- No incremental agent progress or conversation stream.
- The current workflow is synchronous and linear:
  1. supervisor decides
  2. one worker runs
  3. aggregation returns a final response
- There is no user-visible event log or chat-style exchange showing which agent is active.
- The supervisor only uses the last few messages for routing context, not a full multi-agent dialogue.

### Missing API management features
- `backend/app/api/` is empty.
- There is no backend API server implemented yet.
- The frontend has no code calling a backend API or websocket.
- Therefore the UI is not currently connected to the orchestration logic.

## Recommended plan to add live agent simulations

### 1. Add a backend API layer
- Create a backend API server, for example using FastAPI.
- Add endpoints such as:
  - `POST /api/task` to start a task with `{ query, messages }`.
  - `GET /api/status/{task_id}` to poll progress.
  - `GET /api/results/{task_id}` to fetch the final result.
  - `GET /api/stream/{task_id}` or a websocket endpoint for live streaming.
- This will be the missing glue between frontend and the agent graphs.

### 2. Add structured event/message logging to the state
- Enhance `AgentState` with event history fields like:
  - `messages`
  - `conversation_log`
  - `event_log`
- Each node should append meaningful progress entries, for example:
  - `supervisor`: "Selected researcher to gather evidence."
  - `researcher`: "Search completed, scraped 3 URLs."
  - `executor`: "Executed Python code successfully."
  - `writer`: "Draft saved to file."
- This allows the frontend to display an agent-by-agent trace.

### 3. Add streaming or websocket support for live updates
- Use a websocket for chat-like sessions or SSE for one-way progress.
- Send progress events as agents run, for example:
  - `{ "agent": "supervisor", "event": "routing", "message": "Selected researcher to gather evidence." }`
  - `{ "agent": "researcher", "event": "progress", "message": "Scraped top URLs, collected data." }`
  - `{ "agent": "executor", "event": "progress", "message": "Executed code and captured output." }`
  - `{ "agent": "writer", "event": "progress", "message": "Draft generated and saved." }`

### 4. Make supervisor and workers chat-aware
- Keep a richer `messages` array in shared state.
- Have each agent append structured messages to the shared state.
- Use prompts that treat each worker as an agent voice, not just a pipeline step.
- This allows the system to simulate agent-to-agent conversation and show a live narrative to the user.

### 5. Build a minimal UI integration path
- Add frontend support for the backend API or websocket.
- Display:
  - current task status
  - agent progress messages
  - final aggregated response
- If the frontend is not yet built for this, start with a simple static page or client that consumes the streaming endpoint.

## Summary

- The repository already contains the key orchestration design: supervisor routing and worker graphs.
- What is missing is the API layer and live progress streaming.
- The next incremental step is to implement a backend API, wire events into `AgentState`, and expose them to the frontend.
- Once that is in place, the system can evolve from a synchronous pipeline into a live multi-agent simulation.
