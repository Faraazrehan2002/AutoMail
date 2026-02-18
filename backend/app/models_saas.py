"""
SaaS-grade models for AutoMail
Extends existing models with users, templates, batches, and analytics
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, JSON, Float, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .db import Base
import uuid
import hashlib


def generate_id():
    """Generate a unique ID"""
    return str(uuid.uuid4())


class User(Base):
    """User accounts for multi-tenant support"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=generate_id)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    
    # Relationships
    jobs = relationship("Job", back_populates="user", cascade="all, delete-orphan")
    templates = relationship("Template", back_populates="user", cascade="all, delete-orphan")


class Job(Base):
    """Extended Job model with user_id and recipient_count"""
    __tablename__ = "jobs"
    
    id = Column(String, primary_key=True, default=generate_id)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    status = Column(String, default="processing")  # processing, completed, failed
    recipient_count = Column(Integer, default=0)  # Cached count
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    last_batch_id = Column(String, nullable=True)  # Track last batch sent
    
    # Relationships
    user = relationship("User", back_populates="jobs")
    recipients = relationship("Recipient", back_populates="job", cascade="all, delete-orphan")
    send_logs = relationship("SendLog", back_populates="job", cascade="all, delete-orphan")
    batches = relationship("Batch", back_populates="job", cascade="all, delete-orphan")


class Recipient(Base):
    """Recipient model - already exists, just ensuring it has all fields"""
    __tablename__ = "recipients"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False, index=True)
    email = Column(String, nullable=False, index=True)
    name = Column(String, nullable=True)
    company = Column(String, nullable=True)
    title = Column(String, nullable=True)  # New field
    extracted_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    job = relationship("Job", back_populates="recipients")


class Batch(Base):
    """Batch tracking for email sends"""
    __tablename__ = "batches"
    
    id = Column(String, primary_key=True, default=generate_id)  # batch_id UUID
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False, index=True)
    status = Column(String, nullable=False, default="queued", index=True)  # queued, processing, completed, failed, canceled
    total = Column(Integer, nullable=False, default=0)
    sent = Column(Integer, nullable=False, default=0)
    failed = Column(Integer, nullable=False, default=0)
    subject = Column(String, nullable=False)
    body_hash = Column(String, nullable=True, index=True)  # Hash of html_body for deduplication
    dry_run = Column(Boolean, default=False)
    scheduled_for = Column(DateTime(timezone=True), nullable=True, index=True)  # For scheduled sends
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    job = relationship("Job", back_populates="batches")
    send_logs = relationship("SendLog", back_populates="batch", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_batch_job_status', 'job_id', 'status'),
        Index('idx_batch_scheduled', 'scheduled_for', 'status'),
    )


class SendLog(Base):
    """Extended SendLog with batch relationship"""
    __tablename__ = "send_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(String, ForeignKey("batches.id"), nullable=False, index=True)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False, index=True)
    recipient_email = Column(String, nullable=False, index=True)
    status = Column(String, nullable=False, default="queued", index=True)  # queued, sending, sent, failed
    error_message = Column(Text, nullable=True)
    sendgrid_message_id = Column(String, nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    personalization = Column(JSON, nullable=True)
    progress_index = Column(Integer, nullable=True)
    
    # Relationships
    job = relationship("Job", back_populates="send_logs")
    batch = relationship("Batch", back_populates="send_logs")
    
    __table_args__ = (
        Index('idx_sendlog_batch_status', 'batch_id', 'status'),
    )


class Template(Base):
    """Email templates with variable support"""
    __tablename__ = "templates"
    
    id = Column(String, primary_key=True, default=generate_id)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    html_body = Column(Text, nullable=False)
    variables = Column(JSON, nullable=True)  # List of available variables like ["first_name", "company"]
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="templates")


class AnalyticsSnapshot(Base):
    """Pre-computed analytics for performance"""
    __tablename__ = "analytics_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=True, index=True)  # NULL for global
    jobs_created = Column(Integer, default=0)
    batches_sent = Column(Integer, default=0)
    emails_sent = Column(Integer, default=0)
    emails_failed = Column(Integer, default=0)
    success_rate = Column(Float, nullable=True)  # Calculated: sent / (sent + failed)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('idx_analytics_date_user', 'date', 'user_id'),
    )
