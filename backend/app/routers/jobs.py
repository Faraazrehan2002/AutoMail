import os
import shutil
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import logging

from ..db import get_db
from ..models import Job, Recipient, SendLog
from ..schemas import (
    JobResponse,
    JobDetailResponse,
    JobListResponse,
    SendRequest,
    SendResponse,
    RecipientPreview,
    BatchStatus,
    SendStatus
)
from fastapi import Query
from ..config import settings
from ..services.pdf_extract import extract_text_from_pdf
from ..services.email_extract import extract_emails_from_text
from ..services.mailer import Mailer
from ..services.queue import get_email_queue
from ..services.worker_tasks import send_batch_emails

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


@router.get("/jobs", response_model=JobListResponse)
async def list_jobs(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """List recent jobs with pagination"""
    skip = (page - 1) * page_size
    
    # Get total count
    total = db.query(Job).count()
    
    # Get jobs ordered by created_at descending
    jobs = db.query(Job).order_by(Job.created_at.desc()).offset(skip).limit(page_size).all()
    
    # Get recipient counts for each job
    job_responses = []
    for job in jobs:
        recipient_count = db.query(Recipient).filter(Recipient.job_id == job.id).count()
        job_responses.append(JobResponse(
            id=job.id,
            filename=job.filename,
            file_path=job.file_path,
            status=job.status,
            created_at=job.created_at,
            updated_at=job.updated_at,
            recipient_count=recipient_count
        ))
    
    return JobListResponse(
        jobs=job_responses,
        total=total,
        page=page,
        page_size=page_size
    )


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
    db: Session = Depends(get_db)
):
    """
    Queue emails for background sending.
    
    Validates that recipients exist in the job, creates send_log entries,
    and enqueues a background task to send emails. Returns immediately with
    batch_id and queued status.
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
    
    # Create send_log entries with "queued" status
    send_statuses = []
    for recipient_email in requested_emails:
        personalization_data = None
        if personalization_map:
            personalization_data = personalization_map.get(recipient_email)
        
        log_entry = SendLog(
            batch_id=batch_id,
            job_id=job_id,
            recipient_email=recipient_email,
            status="queued",
            personalization=personalization_data
        )
        db.add(log_entry)
        send_statuses.append(SendStatus(
            email=recipient_email,
            status="queued",
            error_message=None,
            sendgrid_message_id=None
        ))
    
    db.commit()
    
    # Enqueue background task
    try:
        queue = get_email_queue()
        queue.enqueue(
            send_batch_emails,
            batch_id=batch_id,
            job_id=job_id,
            recipients=list(requested_emails),
            subject=send_request.subject,
            html_body=send_request.html_body,
            personalization_map=personalization_map,
            dry_run=send_request.dry_run,
            job_timeout='30m'  # Allow up to 30 minutes for large batches
        )
        logger.info(f"Enqueued batch {batch_id} for job {job_id} with {len(requested_emails)} recipients")
    except Exception as e:
        logger.error(f"Failed to enqueue batch {batch_id}: {e}")
        # Mark all as failed
        for log_entry in db.query(SendLog).filter(SendLog.batch_id == batch_id).all():
            log_entry.status = "failed"
            log_entry.error_message = f"Failed to enqueue: {str(e)}"
        db.commit()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to queue emails: {str(e)}"
        )
    
    # Return immediate response
    return SendResponse(
        job_id=job_id,
        batch_id=batch_id,
        total_recipients=len(requested_emails),
        queued=len(requested_emails),
        sent=0,
        failed=0,
        results=send_statuses,
        dry_run=send_request.dry_run
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
    sending = sum(1 for log in send_logs if log.status == "sending")
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
        queued=queued + sending,  # Include "sending" in queued for backward compatibility
        sent=sent,
        failed=failed,
        created_at=created_at,
        results=results
    )


@router.get("/jobs/{job_id}/batches/{batch_id}/progress")
async def get_batch_progress(
    job_id: str,
    batch_id: str,
    db: Session = Depends(get_db)
):
    """Get batch progress information for polling"""
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
    sending = sum(1 for log in send_logs if log.status == "sending")
    sent = sum(1 for log in send_logs if log.status == "sent")
    failed = sum(1 for log in send_logs if log.status == "failed")
    
    # Calculate progress
    completed = sent + failed
    remaining = queued + sending
    percent_complete = (completed / total * 100) if total > 0 else 0
    
    # Determine overall status
    if queued > 0 or sending > 0:
        status = "processing" if sending > 0 else "queued"
    else:
        status = "completed"
    
    return {
        "total": total,
        "sent": sent,
        "failed": failed,
        "remaining": remaining,
        "percent_complete": round(percent_complete, 2),
        "status": status
    }


@router.delete("/jobs/{job_id}", status_code=204)
async def delete_job(
    job_id: str,
    db: Session = Depends(get_db)
):
    """Delete a job and all associated data"""
    job = db.query(Job).filter(Job.id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Delete associated file if it exists
    if job.file_path and os.path.exists(job.file_path):
        try:
            os.remove(job.file_path)
        except Exception as e:
            logger.warning(f"Failed to delete file {job.file_path}: {str(e)}")
    
    # Delete job (cascade will handle recipients and send_logs)
    db.delete(job)
    db.commit()
    
    return None


@router.delete("/jobs", status_code=204)
async def delete_all_jobs(
    db: Session = Depends(get_db)
):
    """Delete all jobs and associated data"""
    jobs = db.query(Job).all()
    
    # Delete all associated files
    for job in jobs:
        if job.file_path and os.path.exists(job.file_path):
            try:
                os.remove(job.file_path)
            except Exception as e:
                logger.warning(f"Failed to delete file {job.file_path}: {str(e)}")
    
    # Delete all jobs (cascade will handle recipients and send_logs)
    db.query(Job).delete()
    db.commit()
    
    return None
