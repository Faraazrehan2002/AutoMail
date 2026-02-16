import os
import shutil
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import logging

from ..db import get_db
from ..models import Job, Recipient, SendLog
from ..schemas import (
    JobResponse,
    JobDetailResponse,
    SendRequest,
    SendResponse,
    RecipientPreview,
    BatchStatus,
    SendStatus
)
from ..config import settings
from ..services.pdf_extract import extract_text_from_pdf
from ..services.email_extract import extract_emails_from_text
from ..services.mailer import Mailer

logger = logging.getLogger(__name__)

router = APIRouter()
_mailer_instance = None


def get_mailer() -> Mailer:
    """Get or create Mailer instance (lazy initialization)"""
    global _mailer_instance
    if _mailer_instance is None:
        _mailer_instance = Mailer()
    return _mailer_instance


def ensure_storage_dir():
    """Ensure storage directory exists"""
    os.makedirs(settings.storage_dir, exist_ok=True)


@router.post("/upload", response_model=JobResponse, status_code=201)
async def upload_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a PDF file and extract email addresses.
    
    Returns a job ID that can be used to:
    - Get extracted recipients: GET /jobs/{job_id}
    - Send emails: POST /jobs/{job_id}/send
    """
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    ensure_storage_dir()
    
    # Create job record
    job = Job(
        filename=file.filename,
        file_path="",  # Will be set after saving
        status="processing"
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    
    # Save file
    file_path = os.path.join(settings.storage_dir, f"{job.id}.pdf")
    job.file_path = file_path
    
    try:
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Extract text from PDF
        try:
            text = extract_text_from_pdf(file_path)
        except ValueError as e:
            job.status = "failed"
            db.commit()
            raise HTTPException(status_code=400, detail=str(e))
        
        # Extract emails
        recipients_data = extract_emails_from_text(text)
        
        # Save recipients to database
        for recipient_data in recipients_data:
            recipient = Recipient(
                job_id=job.id,
                email=recipient_data['email'],
                name=recipient_data.get('name'),
                company=recipient_data.get('company')
            )
            db.add(recipient)
        
        job.status = "completed"
        db.commit()
        
        return JobResponse(
            id=job.id,
            filename=job.filename,
            file_path=job.file_path,
            status=job.status,
            created_at=job.created_at,
            recipient_count=len(recipients_data)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        job.status = "failed"
        db.commit()
        # Clean up file if it exists
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")


@router.get("/jobs/{job_id}", response_model=JobDetailResponse)
async def get_job(job_id: str, db: Session = Depends(get_db)):
    """Get job details including extracted recipients"""
    job = db.query(Job).filter(Job.id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    recipients = db.query(Recipient).filter(Recipient.job_id == job_id).all()
    
    recipient_previews = [
        RecipientPreview(
            email=rec.email,
            name=rec.name,
            company=rec.company
        )
        for rec in recipients
    ]
    
    return JobDetailResponse(
        id=job.id,
        filename=job.filename,
        file_path=job.file_path,
        status=job.status,
        created_at=job.created_at,
        updated_at=job.updated_at,
        recipient_count=len(recipients),
        recipients=recipient_previews
    )


@router.post("/jobs/{job_id}/send", response_model=SendResponse)
async def send_emails(
    job_id: str,
    send_request: SendRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Send emails to selected recipients.
    
    Validates that recipients exist in the job, then sends emails
    with rate limiting. Supports dry_run mode for testing.
    """
    # Verify job exists
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Validate recipients exist in job
    job_recipients = {rec.email for rec in db.query(Recipient).filter(Recipient.job_id == job_id).all()}
    requested_emails = {email.lower() for email in send_request.recipients}
    
    invalid_emails = requested_emails - job_recipients
    if invalid_emails:
        raise HTTPException(
            status_code=400,
            detail=f"Some recipients not found in job: {', '.join(invalid_emails)}"
        )
    
    # Generate batch ID
    batch_id = str(uuid.uuid4())
    
    # Prepare personalization map
    personalization_map = None
    if send_request.personalization:
        personalization_map = {
            email.lower(): send_request.personalization.get(email, {})
            for email in send_request.recipients
        }
    
    # Send emails (this will run synchronously but with rate limiting)
    mailer = get_mailer()
    result = await mailer.send_batch(
        db=db,
        batch_id=batch_id,
        job_id=job_id,
        recipients=list(requested_emails),
        subject=send_request.subject,
        html_body=send_request.html_body,
        personalization_map=personalization_map,
        dry_run=send_request.dry_run
    )
    
    # Format response
    send_statuses = [
        SendStatus(
            email=r["email"],
            status=r["status"],
            error_message=r.get("error_message"),
            sendgrid_message_id=r.get("sendgrid_message_id")
        )
        for r in result["results"]
    ]
    
    return SendResponse(
        job_id=job_id,
        batch_id=batch_id,
        total_recipients=result["total_recipients"],
        queued=result["queued"],
        sent=result["sent"],
        failed=result["failed"],
        results=send_statuses,
        dry_run=result.get("dry_run", False)
    )


@router.get("/jobs/{job_id}/batches/{batch_id}", response_model=BatchStatus)
async def get_batch_status(
    job_id: str,
    batch_id: str,
    db: Session = Depends(get_db)
):
    """Get batch send status and results"""
    # Verify job exists
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Get all send logs for this batch
    send_logs = db.query(SendLog).filter(
        SendLog.batch_id == batch_id,
        SendLog.job_id == job_id
    ).all()
    
    if not send_logs:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    # Aggregate results
    total = len(send_logs)
    queued = sum(1 for log in send_logs if log.status == "queued")
    sent = sum(1 for log in send_logs if log.status == "sent")
    failed = sum(1 for log in send_logs if log.status == "failed")
    
    # Format results
    results = [
        SendStatus(
            email=log.recipient_email,
            status=log.status,
            error_message=log.error_message,
            sendgrid_message_id=log.sendgrid_message_id
        )
        for log in send_logs
    ]
    
    # Get created_at from first log
    created_at = send_logs[0].created_at if send_logs else None
    
    return BatchStatus(
        batch_id=batch_id,
        job_id=job_id,
        total_recipients=total,
        queued=queued,
        sent=sent,
        failed=failed,
        created_at=created_at,
        results=results
    )
