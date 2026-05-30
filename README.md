# 🤖 Multi-Agent Orchestration System

A complete **live multi-agent system** with real-time visualization. Watch supervisor, researcher, executor, writer, and analyst agents collaborate to solve complex tasks.

## ✨ Features

- **Real-time Agent Visualization**: Watch agents work live on a beautiful timeline UI
- **Supervisor Routing**: Intelligent LLM-based routing to specialist workers
- **Streaming Architecture**: Server-Sent Events (SSE) for live progress updates
- **Multi-Agent Workers**:
  - 🔍 **Researcher**: Web search, content scraping, knowledge storage
  - ⚙️ **Executor**: Python code execution, file management
  - ✍️ **Writer**: Document generation and formatting
  - 📊 **Analyst**: Data analysis and insights extraction
- **FastAPI Backend**: Robust REST API with async task management
- **TanStack Start Frontend**: Modern React UI with real-time updates

---

## 🏗️ Architecture

For the full project diagram, runtime sequence, and component map, see [docs/architecture.md](./docs/architecture.md).

```mermaid
flowchart LR
  user([User]) --> ui[Frontend: TanStack Start UI]
  ui -->|POST /api/task| api[FastAPI Backend]
  ui <-->|SSE /api/stream/{task_id}| api
  api --> runner[Background Task Runner]
  runner --> graph[LangGraph Supervisor]
  graph --> researcher[Researcher]
  graph --> executor[Executor]
  graph --> writer[Writer]
  graph --> analyst[Analyst]
  researcher --> aggregate[Aggregate Response]
  executor --> aggregate
  writer --> aggregate
  analyst --> aggregate
  aggregate --> artifacts[(Markdown Artifacts)]
  api --> events[(Task Event Log)]
```

---

## 🚀 Quick Start

### 1️⃣ Prerequisites

- Python 3.11+
- Node.js 18+
- npm or bun

### 2️⃣ One-Command Startup (Windows)

```powershell
# Run the startup script
.\startup.ps1
```

Or with batch file:

```cmd
startup.bat
```

This launches both services in separate windows.

### 3️⃣ Manual Startup

**Terminal 1 - Backend:**

```bash
cd backend
./venv/Scripts/Activate.ps1  # Windows
source ./venv/bin/activate   # Mac/Linux

python -m fastapi dev app/api/main.py
```

**Terminal 2 - Frontend:**

```bash
cd frontend
npm run dev      # or `bun run dev`
```

### 4️⃣ Access the Application

- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

Note: the frontend dev server normally uses port **8080**, but some dev environments or proxies may expose it on **8080**. If you see the UI at http://localhost:8080, that's expected in those setups.

To explicitly force the frontend dev port, set `PORT` or pass `--port` to Vite. Examples (Windows PowerShell / cmd):

```powershell
# PowerShell
$env:PORT=8080; npm run dev
```

```cmd
:: cmd.exe
set PORT=8080&& npm run dev
```

Or run directly with Vite flags:

```bash
npm run dev -- --port 8080
```

---

## 📋 How to Use

1. **Open** the frontend at http://localhost:8080
2. **Enter** a task prompt (e.g., "Research quantum computing trends")
3. **Click** "Launch Task" / "Start"
4. **Watch** the live agent timeline as:
   - Supervisor analyzes and routes
   - Workers execute their tasks
   - Progress streams in real-time
   - Final response appears in the panel

---

## 🔧 Configuration

### Backend Environment (`.env`)

Create `backend/.env`:

```
GROQ_API_TOKEN=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
```

### Frontend API URL

Edit `frontend/src/context/orchestration-context.tsx`:

```typescript
const API_BASE = "http://localhost:8000";
```

---

## 📁 Project Structure

```
multi-agent-orchestration/
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   ├── superviser.py       # Main orchestration
│   │   │   └── subagents/          # Specialist workers
│   │   ├── api/
│   │   │   └── main.py             # FastAPI server
│   │   ├── graph/
│   │   │   └── state.py            # Shared state schema
│   │   └── tools/                  # Web scraper, REPL, file manager
│   ├── venv/                       # Python virtual environment
│   └── .env
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── orchestration/
│   │   │   └── ui/
│   │   ├── context/
│   │   ├── hooks/
│   │   ├── lib/
│   │   ├── routes/                 # TanStack Router routes
│   │   ├── types/                  # TypeScript definitions
│   │   ├── router.tsx              # Router configuration
│   │   ├── routeTree.gen.ts        # Generated TanStack route tree
│   │   ├── server.ts
│   │   ├── start.ts
│   │   └── styles.css
│   │
│   ├── .gitignore
│   ├── .prettierignore
│   ├── .prettierrc
│   ├── bun.lock                    # Bun lockfile
│   ├── package.json
│   └── vite.config.ts
│
├── docs/
│   └── architecture.md              # Detailed architecture diagrams
├── INTEGRATION_GUIDE.md             # Detailed integration docs
├── startup.ps1                      # PowerShell startup script
└── startup.bat                      # Batch startup script
```

---

## 🔌 API Endpoints

### Create Task

**POST** `/api/task`

```json
{
  "query": "Find the latest AI trends",
  "messages": []
}
```

### Poll Status

**GET** `/api/status/{task_id}`

### Get Results

**GET** `/api/results/{task_id}`

### Stream Events (SSE)

**GET** `/api/stream/{task_id}`

See [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md) for full details.

---

## 🎯 Workflow Example

```
User: "Research quantum computing"
    ↓
Supervisor: "Routing to Researcher agent"
    ↓
Researcher:
  - "Searching for 'quantum computing trends'"
  - "Scraping top 3 results"
  - "Storing knowledge in Chroma DB"
    ↓
Aggregate:
  - "Combining research with market analysis"
  - "Generating final report"
    ↓
Result: Comprehensive quantum computing overview
```

---

## 🛠️ Development

### Backend Development

```bash
cd backend
source venv/bin/activate  # or venv\Scripts\Activate.ps1

# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black app/

# Type check
mypy app/
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Run dev server with HMR
npm run dev

# Build for production
npm run build

# Format code
npm run format

# Lint
npm run lint
```

---

## 📚 Key Technologies

### Backend

- **FastAPI**: Modern Python web framework
- **LangGraph**: Agent orchestration and state management
- **LangChain**: LLM integrations and tools
- **Groq/OpenAI**: LLM providers
- **Tavily**: Web search integration
- **Chroma**: Vector database for knowledge storage

### Frontend

- **TanStack Start**: Full-stack React framework
- **React 19**: Latest React features
- **Vite**: Lightning-fast build tool
- **Radix UI**: Accessible component library
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first styling

---

## 🚢 Deployment

### Docker (Coming Soon)

```bash
docker-compose up
```

### Cloud Deployment

See [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md#-deployment) for cloud options.

---

## 🐛 Troubleshooting

| Issue                  | Solution                                           |
| ---------------------- | -------------------------------------------------- |
| Backend won't start    | Check Python 3.11+, activate venv, install FastAPI |
| Frontend can't connect | Ensure backend runs on port 8000, check CORS       |
| Events not streaming   | Verify EventSource in browser console              |
| Agent doesn't execute  | Check API keys in `.env` file                      |

---

## 📖 Documentation

- **[docs/architecture.md](./docs/architecture.md)**: Architecture diagrams, runtime sequence, and component map
- **[INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md)**: Comprehensive integration docs
- **[plan.md](./plan.md)**: Original project plan
- **[task.md](./task.md)**: Development tasks
- **API Docs**: http://localhost:8000/docs (auto-generated)

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📝 License

This project is part of an AI/ML learning initiative.

---

## 🎓 Learning Objectives

- ✅ Multi-agent system orchestration
- ✅ Real-time streaming architecture
- ✅ LLM-based routing and decision-making
- ✅ Full-stack Python + TypeScript development
- ✅ Production-grade API design

---

## 🔗 Quick Links

| Resource | URL                        |
| -------- | -------------------------- |
| Frontend | http://localhost:8080      |
| Backend  | http://localhost:8000      |
| API Docs | http://localhost:8000/docs |

---

## 🎉 Next Steps

1. **Start the services** using `startup.ps1`
2. **Submit a test query** to see agents in action
3. **Explore the codebase** to understand the flow
4. **Customize** workers for your use cases
5. **Deploy** to production

Happy orchestrating! 🚀
