@echo off
echo Starting Frontend linting and formatting...

cd /d "%~dp0Frontend"

echo Installing dependencies...
call npm install

echo Running Prettier on all JSX files...
call npx prettier --write "src/**/*.{js,jsx,ts,tsx,css}"

echo Running ESLint auto-fix on all JSX files...
call npx eslint --fix "src/**/*.{js,jsx,ts,tsx}"

echo Done! All formatting and linting fixes applied.

pause