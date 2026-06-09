@echo off
REM One-click launcher (Windows): starts backend + frontend in two windows.
REM Assumes you already ran the one-time setup (venv + pip install + npm install).

start "Climate Backend"  cmd /k "cd /d %~dp0backend && call .venv\Scripts\activate.bat && uvicorn app.main:app --reload"
start "Climate Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo Backend  -> http://localhost:8000/docs
echo Frontend -> http://localhost:5173
