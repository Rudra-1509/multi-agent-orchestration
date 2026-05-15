# Hierarchical Multi-Agent Orchestration Architecture

This document outlines the architecture for a decoupled, full-stack multi-agent system.

## User Review Required
Please review the proposed frontend and backend technology stack. We have chosen FastAPI for the backend to easily integrate with LangGraph (both Python), and Next.js (TypeScript) for the frontend for a robust UI. 
- Are you comfortable with FastAPI and Next.js?
- For the LLM, we will default to OpenAI (or Anthropic if you prefer, please confirm). We will use Langchain so swapping models is easy.

## Proposed Changes

We will separate the project into two distinct directories: `backend` and `frontend` inside your workspace `c:\Users\RUDRANIL MONDAL\Documents\AIML\Projects\multi-agent-orchestration`.

### Backend (Python + FastAPI + LangGraph)
The backend manages the stateful agent graphs, executes tools securely, and streams events to the frontend.

#### Directory Structure
- **[NEW]** `backend/app/api/`: FastAPI routers and WebSocket endpoints for real-time streaming.
- **[NEW]** `backend/app/graph/`: The core LangGraph state machine compiling the Supervisor and Worker agents.
- **[NEW]** `backend/app/agents/`: System prompts and LLM initializations for the Supervisor, Researcher, Engineer, and QA agents.
- **[NEW]** `backend/app/tools/`: Domain-specific tools (Web Search, File System operations, Code Execution).
- **[NEW]** `backend/workspace/`: A sandboxed directory where the Engineer agent can read/write files.

### Frontend (TypeScript + React/Next.js)
The frontend provides a rich interface to interact with the multi-agent system.

#### Directory Structure
- **[NEW]** `frontend/app/components/chat/`: Real-time chat interface showing messages from agents.
- **[NEW]** `frontend/app/components/workspace/`: A file explorer view to see what the Engineer agent is building.
- **[NEW]** `frontend/app/hooks/`: Custom hooks to manage WebSocket connections from the backend.

## Verification Plan

### Automated Tests
- We will write unit tests using `pytest` for the Python backend (`pytest backend/tests/`) to ensure tools (like File I/O) behave securely and predictably.

### Manual Verification
- Start the FastAPI server (`cd backend && fastapi dev app/main.py`) and Next.js frontend (`cd frontend && npm run dev`).
- Submit a complex research and coding task via the Chat UI and observe the Supervisor delegating work to the Researcher and Engineer.
- Verify that the Engineer's artifacts show up in the Workspace file explorer view.
