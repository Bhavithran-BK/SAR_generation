from fastapi import APIRouter, HTTPException
from celery.result import AsyncResult
from app.schemas.requests import GenerateRequest
from app.schemas.responses import GenerateResponse, JobStatusResponse, SARResponse
from workers.tasks import generate_sar_task
from app.core.security import verify_api_key, rate_limit_standard
from fastapi import Depends

router = APIRouter(dependencies=[verify_api_key, rate_limit_standard])

@router.post("/generate", response_model=GenerateResponse)
async def generate_sar(request: GenerateRequest):
    """
    Submit a SAR generation job.
    """
    # Convert Pydantic model to dict -> json string for Celery
    task = generate_sar_task.delay(request.model_dump_json())
    return GenerateResponse(
        job_id=task.id,
        status="SUBMITTED",
        message="SAR generation job has been queued."
    )

@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """
    Poll the status of a specific job.
    """
    task_result = AsyncResult(job_id)
    
    response = JobStatusResponse(
        job_id=job_id,
        status=task_result.status,
        progress=0
    )

    if task_result.state == 'PENDING':
        response.status = "PENDING"
    elif task_result.state == 'PROCESSING':
        response.status = "PROCESSING"
        # Extract progress from meta
        if isinstance(task_result.info, dict):
            response.progress = task_result.info.get('progress', 0)
    elif task_result.state == 'SUCCESS':
        response.status = "COMPLETED"
        response.progress = 100
        # The result of the task is the SAR data
        if task_result.result:
             # Depending on how result is returned (json or dict)
             # task_result.result is whatever the task returned
             response.result = SARResponse(**task_result.result)
    elif task_result.state == 'FAILURE':
        response.status = "FAILED"
        response.error = str(task_result.result)
        
    return response
