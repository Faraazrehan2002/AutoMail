"""
Background worker tasks for sending emails
"""
import time
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from ..db import SessionLocal
from ..models import SendLog, Job, Batch
from ..config import settings
from .sendgrid_client import SendGridClient
from .websocket_manager import manager
import hashlib
import json

logger = logging.getLogger(__name__)


def _publish_progress(batch_id: str, job_id: str, batch: Batch):
    """Helper to publish progress updates via Redis"""
    try:
        channel = f"{job_id}:{batch_id}"
        data = {
            "type": "progress",
            "batch_id": batch_id,
            "job_id": job_id,
            "status": batch.status,
            "total": batch.total,
            "sent": batch.sent,
            "failed": batch.failed,
            "remaining": batch.total - batch.sent - batch.failed,
            "percent_complete": round(((batch.sent + batch.failed) / batch.total * 100) if batch.total > 0 else 0, 2),
            "started_at": batch.started_at.isoformat() if batch.started_at else None,
            "finished_at": batch.finished_at.isoformat() if batch.finished_at else None
        }
        manager.publish_progress(channel, data)
    except Exception as e:
        logger.debug(f"Failed to publish progress (non-critical): {e}")


def send_batch_emails(
    batch_id: str,
    job_id: str,
    recipients: List[str],
    subject: str,
    html_body: str,
    personalization_map: Optional[Dict[str, Dict[str, Any]]] = None,
    attachments: Optional[List[str]] = None,
    dry_run: bool = False
):
    """
    Background task to send emails to a batch of recipients.
    
    This function runs in a worker process and processes emails sequentially
    with rate limiting, updating the database as it goes.
    
    Args:
        batch_id: Batch ID for tracking
        job_id: Job ID
        recipients: List of recipient email addresses
        subject: Email subject
        html_body: Email HTML body
        personalization_map: Optional dict mapping email -> personalization data
        dry_run: If True, validate but don't actually send
    """
    db: Session = SessionLocal()
    rate_limit_delay = 1.0 / settings.emails_per_second
    
    try:
        logger.info(f"Starting batch {batch_id} for job {job_id} with {len(recipients)} recipients")
        
        # Get or create Batch record
        batch = db.query(Batch).filter(Batch.id == batch_id).first()
        if not batch:
            # Calculate body hash
            body_hash = hashlib.sha256(html_body.encode()).hexdigest()[:16]
            batch = Batch(
                id=batch_id,
                job_id=job_id,
                status="processing",
                total=len(recipients),
                sent=0,
                failed=0,
                subject=subject,
                body_hash=body_hash,
                dry_run=dry_run,
                started_at=datetime.utcnow()
            )
            db.add(batch)
            db.commit()
        else:
            # Update batch status
            batch.status = "processing"
            batch.started_at = datetime.utcnow()
            batch.total = len(recipients)
            db.commit()
        
        # Initialize SendGrid client if not dry run
        sendgrid_client = None
        if not dry_run:
            try:
                sendgrid_client = SendGridClient()
            except ValueError as e:
                logger.error(f"SendGrid not configured: {e}")
                # Mark all as failed
                for i, recipient_email in enumerate(recipients):
                    log_entry = db.query(SendLog).filter(
                        SendLog.batch_id == batch_id,
                        SendLog.recipient_email == recipient_email
                    ).first()
                    if log_entry:
                        log_entry.status = "failed"
                        log_entry.error_message = f"SendGrid not configured: {e}"
                        log_entry.sent_at = datetime.utcnow()
                        log_entry.progress_index = i
                db.commit()
                return
        
        # Process each recipient
        for i, recipient_email in enumerate(recipients):
            try:
                # Get log entry
                log_entry = db.query(SendLog).filter(
                    SendLog.batch_id == batch_id,
                    SendLog.recipient_email == recipient_email
                ).first()
                
                if not log_entry:
                    logger.warning(f"Log entry not found for {recipient_email} in batch {batch_id}")
                    continue
                
                # Update status to "sending"
                log_entry.status = "sending"
                log_entry.progress_index = i
                db.commit()
                
                # Get personalization for this recipient
                personalization = None
                if personalization_map and recipient_email in personalization_map:
                    personalization = personalization_map[recipient_email]
                
                # Send email (or simulate in dry_run mode)
                if dry_run:
                    # In dry run, just mark as sent
                    log_entry.status = "sent"
                    log_entry.sendgrid_message_id = f"DRY_RUN_{batch_id}"
                    log_entry.sent_at = datetime.utcnow()
                    db.commit()
                    
                    # Update batch counters
                    batch.sent += 1
                    db.commit()
                    
                    # Publish progress update
                    _publish_progress(batch_id, job_id, batch)
                    
                    logger.info(f"[DRY RUN] Would send to {recipient_email}")
                else:
                    # Actually send email
                    try:
                        message_id = sendgrid_client.send_email(
                            recipient_email,
                            subject,
                            html_body,
                            personalization,
                            attachments=attachments or []
                        )
                        
                        # Update log entry
                        log_entry.status = "sent"
                        log_entry.sendgrid_message_id = message_id
                        log_entry.sent_at = datetime.utcnow()
                        db.commit()
                        
                        # Update batch counters
                        batch.sent += 1
                        db.commit()
                        
                        # Publish progress update
                        _publish_progress(batch_id, job_id, batch)
                        
                        logger.info(f"Sent email to {recipient_email} (message_id: {message_id})")
                        
                    except Exception as e:
                        error_msg = str(e)
                        logger.error(f"Failed to send email to {recipient_email}: {error_msg}")
                        
                        # Update log entry
                        log_entry.status = "failed"
                        log_entry.error_message = error_msg
                        log_entry.sent_at = datetime.utcnow()
                        db.commit()
                        
                        # Update batch counters
                        batch.failed += 1
                        db.commit()
                        
                        # Publish progress update
                        _publish_progress(batch_id, job_id, batch)
                
                # Rate limiting: wait before next send
                if i < len(recipients) - 1:  # Don't wait after last email
                    time.sleep(rate_limit_delay)
                    
            except Exception as e:
                logger.error(f"Error processing recipient {recipient_email}: {e}")
                # Try to update log entry
                try:
                    log_entry = db.query(SendLog).filter(
                        SendLog.batch_id == batch_id,
                        SendLog.recipient_email == recipient_email
                    ).first()
                    if log_entry:
                        log_entry.status = "failed"
                        log_entry.error_message = f"Processing error: {str(e)}"
                        log_entry.sent_at = datetime.utcnow()
                        db.commit()
                except Exception as db_error:
                    logger.error(f"Failed to update log entry: {db_error}")
                continue
        
        # Update batch status to completed
        try:
            batch.status = "completed"
            batch.finished_at = datetime.utcnow()
            db.commit()
            
            # Publish final progress update
            _publish_progress(batch_id, job_id, batch)
        except Exception as e:
            logger.error(f"Failed to update batch status: {e}")
        
        # Update job's last_batch_id and updated_at
        try:
            job = db.query(Job).filter(Job.id == job_id).first()
            if job:
                job.last_batch_id = batch_id
                job.updated_at = datetime.utcnow()
                db.commit()
        except Exception as e:
            logger.error(f"Failed to update job: {e}")
        
        logger.info(f"Completed batch {batch_id} for job {job_id}")
        
    except Exception as e:
        logger.error(f"Fatal error in batch {batch_id}: {e}", exc_info=True)
        # Mark batch as failed
        try:
            batch = db.query(Batch).filter(Batch.id == batch_id).first()
            if batch:
                batch.status = "failed"
                batch.finished_at = datetime.utcnow()
                db.commit()
        except Exception as batch_error:
            logger.error(f"Failed to update batch status: {batch_error}")
        
        # Mark remaining queued recipients as failed
        try:
            queued_logs = db.query(SendLog).filter(
                SendLog.batch_id == batch_id,
                SendLog.status.in_(["queued", "sending"])
            ).all()
            for log_entry in queued_logs:
                log_entry.status = "failed"
                log_entry.error_message = f"Batch processing error: {str(e)}"
                log_entry.sent_at = datetime.utcnow()
            db.commit()
            
            # Update batch counters
            if batch:
                batch.failed = len(queued_logs)
                db.commit()
        except Exception as db_error:
            logger.error(f"Failed to update failed logs: {db_error}")
    finally:
        db.close()
