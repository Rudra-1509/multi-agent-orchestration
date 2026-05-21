# Multi-Agent Orchestration Startup Script (PowerShell)
# Usage: .\startup.ps1

Write-Host "`n" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Multi-Agent Orchestration Startup" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "`n"

Write-Host "[1/2] Starting Backend (FastAPI on port 8000)..." -ForegroundColor Green
Start-Process PowerShell -ArgumentList {
    Set-Location $PSScriptRoot
    cd backend
    & "./venv/Scripts/Activate.ps1"
    python -m fastapi dev app/api/main.py
} -WindowStyle Normal

Start-Sleep -Seconds 3

Write-Host "[2/2] Starting Frontend (Vite on port 8080)..." -ForegroundColor Green
Start-Process PowerShell -ArgumentList {
    Set-Location $PSScriptRoot
    cd frontend
    # Ensure Vite uses port 8080 for local dev
    $env:PORT = "8080"
    npm run dev
} -WindowStyle Normal

Write-Host "`n"
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Services Starting..." -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "`n"
Write-Host "Backend API:  http://localhost:8000" -ForegroundColor Yellow
Write-Host "Frontend UI:  http://localhost:8080" -ForegroundColor Yellow
Write-Host "API Docs:     http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "`n"
Write-Host "Both windows will open in new terminals." -ForegroundColor Cyan
Write-Host "Close either window to stop that service." -ForegroundColor Cyan
Write-Host "`n"
