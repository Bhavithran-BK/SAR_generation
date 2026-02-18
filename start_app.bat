@echo off
echo Starting SAR Generation System...

:: 1. Backend API
start "Backend API" cmd /k "venv\Scripts\activate & uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

:: 2. Celery Worker (Pool Solo for Windows compatibility)
start "Celery Worker" cmd /k "venv\Scripts\activate & celery -A app.core.celery_app worker --loglevel=info --pool=solo"

:: 3. Frontend Server
start "Frontend" cmd /k "cd frontend & python -m http.server 3000"

echo.
echo Services Started!
echo API: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Ensure Redis and Ollama are running separately.
echo.
pause
