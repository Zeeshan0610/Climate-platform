# One-click launcher (Windows PowerShell): starts backend + frontend in two windows.
# Assumes one-time setup already done (venv + pip install + npm install).
# Run with:  .\start.ps1   (if blocked: powershell -ExecutionPolicy Bypass -File .\start.ps1)

$root = Split-Path -Parent $MyInvocation.MyCommand.Path

Start-Process powershell -ArgumentList @(
  "-NoExit", "-Command",
  "cd '$root\backend'; .\.venv\Scripts\Activate.ps1; uvicorn app.main:app --reload"
)

Start-Process powershell -ArgumentList @(
  "-NoExit", "-Command",
  "cd '$root\frontend'; npm run dev"
)

Write-Host "Backend  -> http://localhost:8000/docs"
Write-Host "Frontend -> http://localhost:5173"
