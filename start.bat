@echo off
echo Starting frontend and backend servers...

REM === Start Frontend ===
echo Launching React (Vite) frontend...
start cmd /k "cd /d Frontend && npm install && npm run dev"

REM === Start Backend via Docker ===
echo Launching FastAPI backend with Docker...
start cmd /k "cd /d Backend && docker compose up --build"

echo Both servers are now running.
pause
