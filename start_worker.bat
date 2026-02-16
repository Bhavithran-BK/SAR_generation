@echo off
:: Set PYTHONPATH to current directory so 'app' module is found
set PYTHONPATH=.

:: Start Celery Worker
:: Using solo pool for reliable Windows development behavior
start "Celery Worker" cmd /k ".\venv\Scripts\celery -A app.core.celery_app worker --loglevel=info --pool=solo -n worker1@barclays"

:: Start Flower (Optional Monitoring)
start "Celery Flower" cmd /k ".\venv\Scripts\celery -A app.core.celery_app flower --port=5555"
