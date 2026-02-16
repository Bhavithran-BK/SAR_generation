from fastapi import APIRouter
from celery.result import AsyncResult
from typing import List
import uuid
import json

from app.schemas.requests import BatchRequest
from app.schemas.responses import GenerateResponse, BatchStatusResponse
from workers.tasks import generate_sar_task
from app.core.redis_client import redis_client

router = APIRouter()

@router.post("/generate", response_model=GenerateResponse)
async def submit_batch(request: BatchRequest):
    """
    Submit a batch of SAR generation requests.
    """
    batch_id = str(uuid.uuid4())
    job_ids = []
    
    for req in request.requests:
        # Pass the batch_id to the task if we want the task to update batch progress (advanced)
        # For now, we just track job IDs here
        task = generate_sar_task.delay(req.model_dump_json())
        job_ids.append(task.id)
    
    # Store batch metadata in Redis
    # Allow 24h expiry
    redis_client.set(f"batch:{batch_id}:total", len(job_ids), ex=86400)
    redis_client.rpush(f"batch:{batch_id}:jobs", *job_ids)
    redis_client.expire(f"batch:{batch_id}:jobs", 86400)

    return GenerateResponse(
        job_id=batch_id,
        status="SUBMITTED",
        message=f"Batch of {len(job_ids)} jobs submitted."
    )

@router.get("/status/{batch_id}", response_model=BatchStatusResponse)
async def get_batch_status(batch_id: str):
    """
    Get aggregate status of a batch.
    """
    total_str = redis_client.get(f"batch:{batch_id}:total")
    if not total_str:
        return {"status": "NOT_FOUND", "message": "Batch ID not found or expired"}
        
    total = int(total_str)
    job_ids = redis_client.lrange(f"batch:{batch_id}:jobs", 0, -1)
    
    completed = 0
    failed = 0
    in_progress = 0
    
    for jid in job_ids:
        res = AsyncResult(jid)
        if res.state == 'SUCCESS':
            completed += 1
        elif res.state == 'FAILURE':
            failed += 1
        else:
            in_progress += 1
            
    # Calculate overall percentage
    # If tasks report granular progress, we could average it. 
    # For now, simplistic: (completed + failed) / total
    
    percent = int(((completed + failed) / total) * 100) if total > 0 else 0
    
    status = "PROCESSING"
    if completed + failed == total:
        status = "COMPLETED"
        if failed == total:
             status = "FAILED"
    
    return {
        "batch_id": batch_id,
        "status": status,
        "progress": percent,
        "details": {
            "total": total,
            "completed": completed,
            "failed": failed,
            "in_progress": in_progress
        }
    }
