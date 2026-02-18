from app.core.celery_app import celery_app
from app.schemas.requests import GenerateRequest
from app.services.generation_service import generation_service
import asyncio
import json
from datetime import datetime

@celery_app.task(bind=True, acks_late=True)
def generate_sar_task(self, request_json: str):
    """
    Celery task to generate SAR asynchronously.
    """
    # Parse request
    request_data = json.loads(request_json)
    request = GenerateRequest(**request_data)
    
    # Update state: PROCESSING
    self.update_state(state='PROCESSING', meta={'progress': 10, 'message': 'Initializing generation...'})
    
    # Simulate steps for progress tracking
    self.update_state(state='PROCESSING', meta={'progress': 30, 'message': 'Analyzing transactions...'})
    print(f"Starting SAR generation for customer: {request.customer.customer_id}", flush=True)
    
    print("Sending request to LLM Engine (via asyncio.run)...", flush=True)
    start_time = datetime.now()
    
    # asyncio.run is more robust for standalone tasks
    result = asyncio.run(generation_service.generate_sar(request))
    
    end_time = datetime.now()
    print(f"LLM Engine responded in { (end_time - start_time).total_seconds() } seconds", flush=True)
    
    self.update_state(state='PROCESSING', meta={'progress': 90, 'message': 'Finalizing report...'})
    
    return result.model_dump(mode='json')
