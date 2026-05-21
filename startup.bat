@echo off
REM Multi-Agent Orchestration Startup Script (Windows)
REM Starts both backend API and frontend dev server

setlocal enabledelayedexpansion

echo.
echo =====================================
echo Multi-Agent Orchestration Startup
echo =====================================
echo.

REM Check if running as admin for terminal configuration
echo Starting Backend and Frontend...
echo.

REM Start Backend in a new window
echo [1/2] Starting Backend (FastAPI on port 8000)...
start "Backend API" cmd /k "cd backend && venv\Scripts\activate && python -m fastapi dev app/api/main.py"

REM Wait a moment for backend to start
timeout /t 3 /nobreak

REM Start Frontend in a new window (force PORT=8080)
echo [2/2] Starting Frontend (Vite on port 8080)...
start "Frontend UI" cmd /k "cd frontend && set PORT=8080&& npm run dev"

echo.
echo =====================================
echo Services Starting...
echo =====================================
echo.
echo Backend API:  http://localhost:8000
echo Frontend UI:  http://localhost:8080
echo API Docs:     http://localhost:8000/docs
echo.
echo Both windows will open. Close either window to stop that service.
echo Ctrl+C in each window to stop.
echo.
pause
