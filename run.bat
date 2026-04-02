@echo off

cd /d "%~dp0"

echo Starting backend...
start "Backend" cmd /c "cd backend && venv\Scripts\activate && uvicorn app.main:app --reload --port 8000"

echo Starting frontend...
start "Frontend" cmd /c "cd frontend && npm run dev"

echo Both servers started. Close the terminal windows to stop them.
