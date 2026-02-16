from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime


class RecipientPreview(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    company: Optional[str] = None


class JobCreate(BaseModel):
    filename: str
    file_path: str


class JobResponse(BaseModel):
    id: str
    filename: str
    file_path: str
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    recipient_count: int = 0
    
    class Config:
        from_attributes = True


class JobDetailResponse(JobResponse):
    recipients: List[RecipientPreview] = []


class SendRequest(BaseModel):
    subject: str = Field(..., min_length=1, description="Email subject")
    html_body: str = Field(..., min_length=1, description="Email HTML body")
    recipients: List[EmailStr] = Field(..., min_items=1, description="List of recipient email addresses")
    personalization: Optional[dict] = Field(
        None,
        description="Optional personalization data keyed by email address"
    )
    dry_run: bool = Field(False, description="If true, validate but don't send emails")
    
    @field_validator('recipients')
    @classmethod
    def validate_recipients_count(cls, v):
        from .config import settings
        if len(v) > settings.max_recipients_per_request:
            raise ValueError(f"Maximum {settings.max_recipients_per_request} recipients allowed per request")
        return v


class SendStatus(BaseModel):
    email: EmailStr
    status: str  # queued, sent, failed
    error_message: Optional[str] = None
    sendgrid_message_id: Optional[str] = None


class SendResponse(BaseModel):
    job_id: str
    batch_id: str
    total_recipients: int
    queued: int
    sent: int
    failed: int
    results: List[SendStatus]
    dry_run: bool = False


class BatchStatus(BaseModel):
    batch_id: str
    job_id: str
    total_recipients: int
    queued: int
    sent: int
    failed: int
    created_at: datetime
    results: List[SendStatus]


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
