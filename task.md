# Multi-Agent Orchestration Project Tasks

## Phase 1: Project Setup & Core Tooling [x]
- [x] Initialize project directories (`backend` and `frontend`) in `c:\Users\RUDRANIL MONDAL\Documents\AIML\Projects\multi-agent-orchestration`
- [x] Backend: Set up Python virtual environment and install FastAPI, LangGraph, and Langchain dependencies
- [x] Frontend: Set up Next.js (TypeScript + TailwindCSS)

## Phase 2: Backend - Agents & Graph [x]
- [x] Define the graph State schema (`TypedDict`)
- [x] Implement custom tools (Web Search, File I/O, secure Python REPL)
- [x] Create Worker Agent nodes (Researcher, Engineer, QA Reviewer)
- [x] Create Supervisor Agent node with conditional routing
- [x] Compile the `StateGraph` and implement a memory checkpointer

## Phase 3: Backend - API [ ]
- [ ] Create REST endpoints for creating/managing agent threads
- [ ] Implement Server-Sent Events (SSE) or WebSockets to stream graph events to the client
- [ ] Implement a Human-in-the-Loop endpoint to approve actions

## Phase 4: Frontend Development [ ]
- [ ] Create the main layout and chat interface
- [ ] Implement API client to communicate with the backend
- [ ] Build a Workspace view to display files created/modified by agents
- [ ] Add visual indicators for which agent is active

## Phase 5: Testing & Refinement [ ]
- [ ] Test the full end-to-end flow with a complex prompt
- [ ] Refine system prompts to reduce hallucinations
