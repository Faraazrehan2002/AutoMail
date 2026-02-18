"""
Analytics endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from ..db import get_db
from ..models import Job, Batch, SendLog, User, AnalyticsSnapshot
from ..dependencies import get_current_user_optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["analytics"])


class DailyMetrics(BaseModel):
    date: str
    jobs_created: int
    batches_sent: int
    emails_sent: int
    emails_failed: int
    success_rate: float


class OverviewResponse(BaseModel):
    total_jobs: int
    total_batches: int
    total_emails_sent: int
    total_emails_failed: int
    overall_success_rate: float
    daily_metrics: List[DailyMetrics]


class BatchAnalyticsResponse(BaseModel):
    batch_id: str
    job_id: str
    total: int
    sent: int
    failed: int
    success_rate: float
    failure_reasons: dict
    domain_stats: dict
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None


@router.get("/overview", response_model=OverviewResponse)
async def get_overview(
    days: int = Query(30, ge=1, le=365, description="Number of days to include"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Get analytics overview with daily metrics"""
    try:
        # Build base query with user filter
        job_query = db.query(Job)
        batch_query = db.query(Batch)
        
        if current_user:
            job_query = job_query.filter(Job.user_id == current_user.id)
            batch_query = batch_query.join(Job).filter(Job.user_id == current_user.id)
        
        # Overall totals
        total_jobs = job_query.count()
        total_batches = batch_query.count()
        
        # Email totals from send_logs
        send_log_query = db.query(SendLog)
        if current_user:
            send_log_query = send_log_query.join(Job).filter(Job.user_id == current_user.id)
        
        total_sent = send_log_query.filter(SendLog.status == "sent").count()
        total_failed = send_log_query.filter(SendLog.status == "failed").count()
        overall_success_rate = (total_sent / (total_sent + total_failed) * 100) if (total_sent + total_failed) > 0 else 0
    except Exception as e:
        import traceback
        logger.error(f"Error in analytics overview: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Analytics error: {str(e)}")
    
    # Daily metrics - simplified for now (can be enhanced later)
    daily_metrics = []
    
    try:
        from datetime import timezone
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        # Get all jobs and aggregate by date
        job_query = db.query(Job).filter(Job.created_at >= start_date)
        if current_user:
            job_query = job_query.filter(Job.user_id == current_user.id)
        all_jobs = job_query.all()
        
        job_counts = defaultdict(int)
        for job in all_jobs:
            if job.created_at:
                try:
                    date_str = job.created_at.date().isoformat()
                except:
                    date_str = str(job.created_at)[:10]
                job_counts[date_str] += 1
        
        # Get all batches and aggregate by date
        batch_query = db.query(Batch).filter(Batch.created_at >= start_date)
        if current_user:
            batch_query = batch_query.join(Job).filter(Job.user_id == current_user.id)
        all_batches = batch_query.all()
        
        batch_counts = defaultdict(int)
        for batch in all_batches:
            if batch.created_at:
                try:
                    date_str = batch.created_at.date().isoformat()
                except:
                    date_str = str(batch.created_at)[:10]
                batch_counts[date_str] += 1
        
        # Get all send logs and aggregate by date
        log_query = db.query(SendLog).filter(SendLog.created_at >= start_date)
        if current_user:
            log_query = log_query.join(Job).filter(Job.user_id == current_user.id)
        all_logs = log_query.all()
        
        email_stats = defaultdict(lambda: {"sent": 0, "failed": 0})
        for log in all_logs:
            if log.created_at:
                try:
                    date_str = log.created_at.date().isoformat()
                except:
                    date_str = str(log.created_at)[:10]
                if log.status == "sent":
                    email_stats[date_str]["sent"] += 1
                elif log.status == "failed":
                    email_stats[date_str]["failed"] += 1
        
        # Combine into daily metrics
        date_dict = {}
        
        # Add job counts
        for date_str, count in job_counts.items():
            if date_str not in date_dict:
                date_dict[date_str] = {"jobs": 0, "batches": 0, "sent": 0, "failed": 0}
            date_dict[date_str]["jobs"] = count
        
        # Add batch counts
        for date_str, count in batch_counts.items():
            if date_str not in date_dict:
                date_dict[date_str] = {"jobs": 0, "batches": 0, "sent": 0, "failed": 0}
            date_dict[date_str]["batches"] = count
        
        # Add email stats
        for date_str, stats in email_stats.items():
            if date_str not in date_dict:
                date_dict[date_str] = {"jobs": 0, "batches": 0, "sent": 0, "failed": 0}
            date_dict[date_str]["sent"] = stats["sent"]
            date_dict[date_str]["failed"] = stats["failed"]
        
        # Convert to list
        for date_str, metrics in sorted(date_dict.items()):
            total = metrics["sent"] + metrics["failed"]
            success_rate = (metrics["sent"] / total * 100) if total > 0 else 0
            daily_metrics.append(DailyMetrics(
                date=date_str,
                jobs_created=metrics["jobs"],
                batches_sent=metrics["batches"],
                emails_sent=metrics["sent"],
                emails_failed=metrics["failed"],
                success_rate=round(success_rate, 2)
            ))
    except Exception as e:
        logger.warning(f"Error computing daily metrics (non-critical): {e}")
        # Return empty daily metrics if there's an error
        daily_metrics = []
    
    return OverviewResponse(
        total_jobs=total_jobs,
        total_batches=total_batches,
        total_emails_sent=total_sent,
        total_emails_failed=total_failed,
        overall_success_rate=round(overall_success_rate, 2),
        daily_metrics=daily_metrics
    )


@router.get("/batch/{batch_id}", response_model=BatchAnalyticsResponse)
async def get_batch_analytics(
    batch_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Get detailed analytics for a specific batch"""
    # Get batch
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    # Check access
    if current_user:
        job = db.query(Job).filter(Job.id == batch.job_id).first()
        if job and job.user_id and job.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    # Get send logs
    send_logs = db.query(SendLog).filter(SendLog.batch_id == batch_id).all()
    
    # Calculate success rate
    total = batch.total
    sent = batch.sent
    failed = batch.failed
    success_rate = (sent / total * 100) if total > 0 else 0
    
    # Failure reasons
    failure_reasons = {}
    for log in send_logs:
        if log.status == "failed" and log.error_message:
            # Extract error type (first part before colon or first 50 chars)
            error_key = log.error_message.split(":")[0] if ":" in log.error_message else log.error_message[:50]
            failure_reasons[error_key] = failure_reasons.get(error_key, 0) + 1
    
    # Domain stats
    domain_stats = {}
    for log in send_logs:
        if log.recipient_email:
            domain = log.recipient_email.split("@")[-1] if "@" in log.recipient_email else "unknown"
            if domain not in domain_stats:
                domain_stats[domain] = {"sent": 0, "failed": 0, "total": 0}
            domain_stats[domain]["total"] += 1
            if log.status == "sent":
                domain_stats[domain]["sent"] += 1
            elif log.status == "failed":
                domain_stats[domain]["failed"] += 1
    
    # Calculate duration
    duration_seconds = None
    if batch.started_at and batch.finished_at:
        duration_seconds = (batch.finished_at - batch.started_at).total_seconds()
    
    return BatchAnalyticsResponse(
        batch_id=batch_id,
        job_id=batch.job_id,
        total=total,
        sent=sent,
        failed=failed,
        success_rate=round(success_rate, 2),
        failure_reasons=failure_reasons,
        domain_stats=domain_stats,
        started_at=batch.started_at,
        finished_at=batch.finished_at,
        duration_seconds=duration_seconds
    )
