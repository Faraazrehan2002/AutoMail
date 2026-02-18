"""
Scheduler service to process scheduled batches
Runs as a background task or separate process
"""
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from ..db import SessionLocal
from ..models import Batch
from ..services.queue import get_email_queue
from ..services.worker_tasks import send_batch_emails
import time

logger = logging.getLogger(__name__)


def process_scheduled_batches():
    """Check for scheduled batches that are due and enqueue them"""
    db: Session = SessionLocal()
    try:
        now = datetime.utcnow()
        
        # Find batches that are scheduled and due
        due_batches = db.query(Batch).filter(
            Batch.status == "queued",
            Batch.scheduled_for <= now,
            Batch.scheduled_for.isnot(None)
        ).all()
        
        if not due_batches:
            return
        
        logger.info(f"Found {len(due_batches)} scheduled batches due for processing")
        
        queue = get_email_queue()
        
        for batch in due_batches:
            try:
                # Get recipients from send_logs
                from ..models import SendLog
                send_logs = db.query(SendLog).filter(
                    SendLog.batch_id == batch.id
                ).all()
                
                if not send_logs:
                    logger.warning(f"Batch {batch.id} has no send_logs, skipping")
                    batch.status = "failed"
                    db.commit()
                    continue
                
                recipients = [log.recipient_email for log in send_logs]
                
                # Build personalization map
                personalization_map = {}
                for log in send_logs:
                    if log.personalization:
                        personalization_map[log.recipient_email] = log.personalization
                
                # Enqueue the batch
                queue.enqueue(
                    send_batch_emails,
                    batch.id,
                    batch.job_id,
                    recipients,
                    batch.subject,
                    "",  # Note: html_body not stored in batch, would need to retrieve from template or store
                    personalization_map=personalization_map if personalization_map else None,
                    dry_run=batch.dry_run,
                    job_timeout='30m'
                )
                
                logger.info(f"Enqueued scheduled batch {batch.id} for job {batch.job_id}")
                
            except Exception as e:
                logger.error(f"Failed to enqueue scheduled batch {batch.id}: {e}")
                batch.status = "failed"
                db.commit()
        
    except Exception as e:
        logger.error(f"Error processing scheduled batches: {e}", exc_info=True)
    finally:
        db.close()


def run_scheduler_loop(interval_seconds: int = 60):
    """Run scheduler in a loop (for standalone process)"""
    logger.info(f"Starting scheduler loop (checking every {interval_seconds} seconds)")
    while True:
        try:
            process_scheduled_batches()
        except Exception as e:
            logger.error(f"Scheduler loop error: {e}", exc_info=True)
        
        time.sleep(interval_seconds)
