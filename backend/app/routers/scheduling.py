"""
Scheduling endpoints for delayed email sends
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from ..db import get_db
from ..models import Job, Batch, User, Recipient
from ..dependencies import get_current_user_optional
from ..schemas import SendRequest
from ..services.queue import get_email_queue
from ..services.worker_tasks import send_batch_emails
import uuid
import hashlib
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/jobs", tags=["scheduling"])


class ScheduleRequest(SendRequest):
    scheduled_for: datetime  # When to send the emails


@router.post("/{job_id}/schedule", response_model=dict)
async def schedule_send(
    job_id: str,
    schedule_request: ScheduleRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Schedule a batch of emails to be sent at a future time.
    
    The worker will pick up scheduled batches when they're due.
    """
    # Verify job exists and user has access
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if current_user and job.user_id and job.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Validate scheduled_for is in the future
    if schedule_request.scheduled_for <= datetime.utcnow():
        raise HTTPException(status_code=400, detail="scheduled_for must be in the future")
    
    # Validate recipients exist in job
    job_recipients = {rec.email for rec in db.query(Recipient).filter(Recipient.job_id == job_id).all()}
    requested_emails = {email.lower() for email in schedule_request.recipients}
    
    invalid_emails = requested_emails - job_recipients
    if invalid_emails:
        raise HTTPException(
            status_code=400,
            detail=f"Some recipients not found in job: {', '.join(invalid_emails)}"
        )
    
    # Generate batch ID
    batch_id = str(uuid.uuid4())
    
    # Calculate body hash
    body_hash = hashlib.sha256(schedule_request.html_body.encode()).hexdigest()[:16]
    
    # Create Batch record with scheduled_for
    batch = Batch(
        id=batch_id,
        job_id=job_id,
        status="queued",
        total=len(requested_emails),
        sent=0,
        failed=0,
        subject=schedule_request.subject,
        body_hash=body_hash,
        dry_run=schedule_request.dry_run,
        scheduled_for=schedule_request.scheduled_for
    )
    db.add(batch)
    
    # Create send_log entries
    from ..models import SendLog
    personalization_map = None
    if schedule_request.personalization:
        personalization_map = {
            email.lower(): schedule_request.personalization.get(email, {})
            for email in schedule_request.recipients
        }
    
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
    
    db.commit()
    
    logger.info(f"Scheduled batch {batch_id} for job {job_id} to send at {schedule_request.scheduled_for}")
    
    return {
        "batch_id": batch_id,
        "job_id": job_id,
        "scheduled_for": schedule_request.scheduled_for.isoformat(),
        "status": "scheduled",
        "total_recipients": len(requested_emails)
    }
