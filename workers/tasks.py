from app.core.celery_app import celery_app
from app.schemas.requests import GenerateRequest
from app.services.generation_service import generation_service
import asyncio
import json

@celery_app.task(bind=True, acks_late=True)
def generate_sar_task(self, request_json: str):
    """
    Celery task to generate SAR asynchronously.
    """
    try:
        # Parse request
        request_data = json.loads(request_json)
        request = GenerateRequest(**request_data)
        
        # Update state: PROCESSING
        self.update_state(state='PROCESSING', meta={'progress': 10, 'message': 'Initializing generation...'})
        
        # Run async service in sync task
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        # Simulate steps for progress tracking
        self.update_state(state='PROCESSING', meta={'progress': 30, 'message': 'Analyzing transactions...'})
        # Actual call (mocked latency inside)
        result = loop.run_until_complete(generation_service.generate_sar(request))
        
        self.update_state(state='PROCESSING', meta={'progress': 90, 'message': 'Finalizing report...'})
        
        return result.model_dump(mode='json')
        
    except Exception as e:
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise e
