@echo off
echo Starting frontend and backend servers...

REM === Start Frontend ===
echo Launching React (Vite) frontend...
start cmd /k "cd /d Frontend && npm install && npm run dev"

REM === Start Backend ===
echo Launching FastAPI backend...
start cmd /k "cd /d Backend && uvicorn main:app --reload"

echo Both servers are now running.
pause