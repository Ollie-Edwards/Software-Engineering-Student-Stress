@echo off
echo Starting Frontend tests...

cd /d "%~dp0Frontend"

echo Installing dependencies...
call npm install

echo Running tests with coverage...
call npx vitest run --coverage --reporter=html --outputFile=./html/index.html

echo Starting preview server...
start cmd /k "npx vite preview --outDir coverage --port 4173"
start cmd /k "npx vite preview --outDir html --port 4174"

timeout /t 3 /nobreak

start "" "http://localhost:4173"
start "" "http://localhost:4174"

pause