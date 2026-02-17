from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .db import Base
import uuid


def generate_job_id():
    """Generate a unique job ID"""
    return str(uuid.uuid4())


class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(String, primary_key=True, default=generate_job_id)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    status = Column(String, default="processing")  # processing, completed, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    last_batch_id = Column(String, nullable=True)  # Track last batch sent
    
    # Relationships
    recipients = relationship("Recipient", back_populates="job", cascade="all, delete-orphan")
    send_logs = relationship("SendLog", back_populates="job", cascade="all, delete-orphan")


class Recipient(Base):
    __tablename__ = "recipients"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False)
    email = Column(String, nullable=False, index=True)
    name = Column(String, nullable=True)
    company = Column(String, nullable=True)
    extracted_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    job = relationship("Job", back_populates="recipients")


class SendLog(Base):
    __tablename__ = "send_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(String, nullable=False, index=True)  # UUID for batch tracking
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False, index=True)
    recipient_email = Column(String, nullable=False, index=True)
    status = Column(String, nullable=False, default="queued")  # queued, sending, sent, failed
    error_message = Column(Text, nullable=True)
    sendgrid_message_id = Column(String, nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    personalization = Column(JSON, nullable=True)  # Store personalization data
    progress_index = Column(Integer, nullable=True)  # Optional: track order in batch
    
    # Relationships
    job = relationship("Job", back_populates="send_logs")
