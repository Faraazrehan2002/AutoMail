"""
WebSocket endpoints for real-time progress updates
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import Batch, Job
from ..services.websocket_manager import manager
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/jobs/{job_id}/batches/{batch_id}")
async def websocket_batch_progress(
    websocket: WebSocket,
    job_id: str,
    batch_id: str
):
    """
    WebSocket endpoint for real-time batch progress updates.
    
    Client connects to receive progress updates as emails are sent.
    Falls back to polling if WebSocket is unavailable.
    """
    # Verify job and batch exist
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            await websocket.close(code=1008, reason="Job not found")
            return
        
        batch = db.query(Batch).filter(Batch.id == batch_id, Batch.job_id == job_id).first()
        if not batch:
            await websocket.close(code=1008, reason="Batch not found")
            return
    finally:
        db.close()
    
    channel = f"{job_id}:{batch_id}"
    await manager.connect(websocket, channel)
    
    try:
        # Send initial progress snapshot
        initial_data = {
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
        await manager.send_personal_message(initial_data, websocket)
        
        # Keep connection alive and listen for updates
        while True:
            # Wait for any message from client (ping/pong or close)
            try:
                data = await websocket.receive_text()
                # Echo back for keepalive
                if data == "ping":
                    await websocket.send_text("pong")
            except WebSocketDisconnect:
                break
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for batch {batch_id}")
    except Exception as e:
        logger.error(f"WebSocket error for batch {batch_id}: {e}")
    finally:
        manager.disconnect(websocket, channel)
