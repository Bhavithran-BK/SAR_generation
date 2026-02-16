# Start Celery Worker (Windows requires pool=solo for reload validation usually, but threads/processes work too. Solo is safest for dev)
start "Celery Worker" cmd /k ".\venv\Scripts\celery -A workers.celery_worker.celery_app worker --loglevel=info --pool=solo"

# Start Flower
start "Flower Monitor" cmd /k ".\venv\Scripts\celery -A workers.celery_worker.celery_app flower"
