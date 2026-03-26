@echo off
echo Starting backend tests...

REM === Install dependencies and run tests ===
echo Installing dependencies and running tests...
start cmd /k "cd /d Backend && python -m pip install --upgrade pip && pip install pytest pytest-cov httpx && pip install -r requirements.txt && pytest --cov=app --cov-report=term-missing --cov-report=html:htmlcov --cov-fail-under=95 && start htmlcov\index.html"

echo Test process launched.
pause