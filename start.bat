@echo off
title GradeLens-AI Launcher
echo Starting GradeLens-AI (Backend + Frontend)...

start "GradeLens Backend (FastAPI :8000)" cmd /k "cd /d %~dp0backend && .\venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"
start "GradeLens Frontend (Next.js :3000)" cmd /k "cd /d %~dp0frontend && npm run dev"

echo Backend started on http://127.0.0.1:8000
echo Frontend started on http://localhost:3000
