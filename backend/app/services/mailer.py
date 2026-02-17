import asyncio
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from sqlalchemy.orm import Session
from ..models import SendLog, Job
from ..config import settings
from .sendgrid_client import SendGridClient

logger = logging.getLogger(__name__)


class Mailer:
    """Service for sending emails with rate limiting"""
    
    def __init__(self):
        # Initialize SendGrid client only when needed (lazy initialization)
        self._sendgrid_client = None
        self.rate_limit_delay = 1.0 / settings.emails_per_second
    
    @property
    def sendgrid_client(self):
        """Lazy initialization of SendGrid client"""
        if self._sendgrid_client is None:
            self._sendgrid_client = SendGridClient()
        return self._sendgrid_client
    
    async def send_batch(
        self,
        db: Session,
        batch_id: str,
        job_id: str,
        recipients: List[str],
        subject: str,
        html_body: str,
        personalization_map: Optional[Dict[str, Dict[str, Any]]] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Send emails to a batch of recipients with rate limiting.
        
        Args:
            db: Database session
            batch_id: Batch ID for tracking
            job_id: Job ID
            recipients: List of recipient email addresses
            subject: Email subject
            html_body: Email HTML body
            personalization_map: Optional dict mapping email -> personalization data
            dry_run: If True, validate but don't actually send
            
        Returns:
            Dictionary with send results
        """
        results = []
        queued_count = 0
        sent_count = 0
        failed_count = 0
        
        if dry_run:
            logger.info(f"DRY RUN mode: Will validate but not send emails for batch {batch_id}")
        
        for recipient_email in recipients:
            # Create log entry with queued status
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
            queued_count += 1
            
            # Get personalization for this recipient
            personalization = None
            if personalization_map and recipient_email in personalization_map:
                personalization = personalization_map[recipient_email]
            
            # Send email (or simulate in dry_run mode)
            if dry_run:
                # In dry run, just mark as would-be-sent
                log_entry.status = "sent"
                log_entry.sendgrid_message_id = f"DRY_RUN_{batch_id}"
                log_entry.sent_at = datetime.utcnow()
                db.commit()
                
                results.append({
                    "email": recipient_email,
                    "status": "sent",
                    "sendgrid_message_id": f"DRY_RUN_{batch_id}",
                    "error_message": None
                })
                sent_count += 1
            else:
                # Actually send email
                try:
                    message_id = await self._send_with_rate_limit(
                        recipient_email,
                        subject,
                        html_body,
                        personalization
                    )
                    
                    # Update log entry
                    log_entry.status = "sent"
                    log_entry.sendgrid_message_id = message_id
                    log_entry.sent_at = datetime.utcnow()
                    db.commit()
                    
                    results.append({
                        "email": recipient_email,
                        "status": "sent",
                        "sendgrid_message_id": message_id,
                        "error_message": None
                    })
                    sent_count += 1
                    
                except Exception as e:
                    error_msg = str(e)
                    logger.error(f"Failed to send email to {recipient_email}: {error_msg}")
                    
                    # Update log entry
                    log_entry.status = "failed"
                    log_entry.error_message = error_msg
                    log_entry.sent_at = datetime.utcnow()
                    db.commit()
                    
                    results.append({
                        "email": recipient_email,
                        "status": "failed",
                        "sendgrid_message_id": None,
                        "error_message": error_msg
                    })
                    failed_count += 1
        
        return {
            "batch_id": batch_id,
            "total_recipients": len(recipients),
            "queued": queued_count,
            "sent": sent_count,
            "failed": failed_count,
            "results": results,
            "dry_run": dry_run
        }
    
    async def _send_with_rate_limit(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        personalization: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Send email with rate limiting.
        
        Args:
            to_email: Recipient email
            subject: Email subject
            html_content: HTML content
            personalization: Optional personalization data
            
        Returns:
            SendGrid message ID
        """
        # Run the synchronous SendGrid call in a thread pool
        loop = asyncio.get_event_loop()
        message_id = await loop.run_in_executor(
            None,
            lambda: self.sendgrid_client.send_email(
                to_email,
                subject,
                html_content,
                personalization
            )
        )
        
        # Rate limiting: wait before next send
        await asyncio.sleep(self.rate_limit_delay)
        
        return message_id
