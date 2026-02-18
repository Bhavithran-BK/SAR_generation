import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

from app.core.celery_app import celery_app

if __name__ == "__main__":
    print("Starting Celery worker (Stable Wrapper)...")
    celery_app.worker_main(argv=['worker', '--loglevel=info', '--pool=solo'])
