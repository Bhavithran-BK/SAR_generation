from fastapi import APIRouter, HTTPException
from celery.result import AsyncResult
from app.schemas.requests import GenerateRequest
from app.schemas.responses import GenerateResponse, JobStatusResponse, SARResponse
from app.db.base import get_db
from app.models.sql import SAR, Alert, AuditBlock
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, select
import uuid
from workers.tasks import generate_sar_task
from app.core.security import verify_api_key, rate_limit_standard
from fastapi import Depends
from datetime import datetime

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
             # Safely handle result parsing
             try:
                 if isinstance(task_result.result, dict):
                    response.result = SARResponse(**task_result.result)
                 else:
                    # In case it's a string or other
                    response.status = "FAILED"
                    response.error = "Invalid result format from worker."
             except Exception as e:
                 response.status = "FAILED"
                 response.error = f"Result Parsing Error: {str(e)}"
    elif task_result.state == 'FAILURE':
        response.status = "FAILED"
        response.error = str(task_result.result)
        
    return response

from pydantic import BaseModel

class SaveDraftRequest(BaseModel):
    edited_content: str

@router.post("/save/{sar_id}")
async def save_sar_draft(sar_id: str, request: SaveDraftRequest, db: AsyncSession = Depends(get_db)):
    """
    Officer edits the AI narrative. Status: GENERATED -> REVIEWED.
    """
    await db.execute(
        update(SAR).where(SAR.sar_id == sar_id).values(
            edited_content=request.edited_content,
            status="REVIEWED"
        )
    )
    await db.commit()
    return {"status": "SUCCESS", "message": "Draft updated."}

@router.post("/verify/{sar_id}")
async def verify_sar(sar_id: str, officer_id: str, db: AsyncSession = Depends(get_db)):
    """
    Officer verifies the report. Status: REVIEWED -> VERIFIED.
    Handoff to Auditor.
    """
    await db.execute(
        update(SAR).where(SAR.sar_id == sar_id).values(
            status="VERIFIED",
            officer_id=officer_id,
            verified_at=datetime.utcnow()
        )
    )
    await db.commit()
    return {"status": "SUCCESS", "message": "Report verified and sent to Auditor."}

@router.post("/finalize/{sar_id}")
async def finalize_sar(sar_id: str, auditor_id: str, db: AsyncSession = Depends(get_db)):
    """
    Auditor finalizes the report. Status: VERIFIED -> FINALIZED.
    """
    query = select(SAR).where(SAR.sar_id == sar_id)
    result = await db.execute(query)
    sar = result.scalar_one_or_none()
    
    if not sar:
        raise HTTPException(status_code=404, detail="SAR not found")

    if sar.status != "VERIFIED":
         raise HTTPException(status_code=400, detail="Only verified reports can be finalized.")

    sar.status = "FINALIZED"
    sar.auditor_id = auditor_id
    sar.finalized_at = datetime.utcnow()
    
    # Simple audit log entry
    audit = AuditBlock(
        block_id=str(uuid.uuid4()),
        previous_hash="0", 
        action=f"SAR_FINALIZED:{sar_id}",
        user_id=auditor_id,
        data_hash=str(hash(sar.edited_content or sar.content))
    )
    db.add(audit)
    
    await db.commit()
    return {"status": "SUCCESS", "message": "SAR Finalized and Archived for Submission."}
