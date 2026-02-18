"""
Attachment upload routes for email attachments (resume, cover letter, etc.)
"""
import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import logging
from ..db import get_db
from ..dependencies import get_current_user
from ..models import User
from ..config import settings
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/attachments", tags=["attachments"])

# Allowed file types for attachments
ALLOWED_EXTENSIONS = {'.pdf', '.doc', '.docx'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


class AttachmentResponse(BaseModel):
    file_path: str
    filename: str
    size: int


def ensure_attachments_dir():
    """Ensure attachments directory exists"""
    attachments_dir = os.path.join(settings.storage_dir, "attachments")
    os.makedirs(attachments_dir, exist_ok=True)
    return attachments_dir


@router.post("/upload", response_model=AttachmentResponse)
async def upload_attachment(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload an attachment file (resume, cover letter, etc.)
    
    Returns the file path that can be used in the attachments array when sending emails.
    """
    # Validate file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Read file to check size
    file_content = await file.read()
    file_size = len(file_content)
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / (1024 * 1024)} MB"
        )
    
    # Ensure attachments directory exists
    attachments_dir = ensure_attachments_dir()
    
    # Generate unique filename
    file_id = str(uuid.uuid4())
    safe_filename = f"{file_id}{file_ext}"
    file_path = os.path.join(attachments_dir, safe_filename)
    
    try:
        # Save file
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)
        
        logger.info(f"Attachment uploaded: {file.filename} -> {file_path} (user: {current_user.email})")
        
        # Return absolute path for use in SendGrid
        absolute_path = os.path.abspath(file_path)
        
        return AttachmentResponse(
            file_path=absolute_path,
            filename=file.filename,
            size=file_size
        )
        
    except Exception as e:
        logger.error(f"Error saving attachment: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save attachment: {str(e)}"
        )


@router.post("/upload-multiple", response_model=List[AttachmentResponse])
async def upload_multiple_attachments(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload multiple attachment files at once.
    
    Returns a list of file paths that can be used in the attachments array.
    """
    if len(files) > 10:  # Limit to 10 files at once
        raise HTTPException(
            status_code=400,
            detail="Maximum 10 files allowed per upload"
        )
    
    attachments_dir = ensure_attachments_dir()
    results = []
    
    for file in files:
        # Validate file extension
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            logger.warning(f"Skipping invalid file type: {file.filename}")
            continue
        
        # Read file to check size
        file_content = await file.read()
        file_size = len(file_content)
        
        if file_size > MAX_FILE_SIZE:
            logger.warning(f"Skipping file too large: {file.filename}")
            continue
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        safe_filename = f"{file_id}{file_ext}"
        file_path = os.path.join(attachments_dir, safe_filename)
        
        try:
            # Save file
            with open(file_path, "wb") as buffer:
                buffer.write(file_content)
            
            absolute_path = os.path.abspath(file_path)
            results.append(AttachmentResponse(
                file_path=absolute_path,
                filename=file.filename,
                size=file_size
            ))
            
        except Exception as e:
            logger.error(f"Error saving attachment {file.filename}: {str(e)}")
            # Continue with other files
    
    if not results:
        raise HTTPException(
            status_code=400,
            detail="No valid files were uploaded"
        )
    
    logger.info(f"Uploaded {len(results)} attachments (user: {current_user.email})")
    return results
