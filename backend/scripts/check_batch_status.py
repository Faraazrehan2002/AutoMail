#!/usr/bin/env python3
"""
Check batch status and diagnose email sending issues
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.db import SessionLocal
from app.models import SendLog, Job
from app.config import settings

def check_batch_status(batch_id: str):
    """Check status of a batch"""
    db = SessionLocal()
    try:
        # Get all send logs for this batch
        send_logs = db.query(SendLog).filter(SendLog.batch_id == batch_id).all()
        
        if not send_logs:
            print(f"❌ No logs found for batch: {batch_id}")
            return
        
        print(f"\n📊 Batch Status: {batch_id}\n")
        print(f"Total recipients: {len(send_logs)}")
        
        status_counts = {}
        for log in send_logs:
            status = log.status
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print(f"\nStatus breakdown:")
        for status, count in status_counts.items():
            print(f"  {status}: {count}")
        
        print(f"\n📧 Recipient Details:")
        for log in send_logs:
            print(f"\n  Email: {log.recipient_email}")
            print(f"  Status: {log.status}")
            if log.sendgrid_message_id:
                print(f"  Message ID: {log.sendgrid_message_id}")
            if log.error_message:
                print(f"  ❌ Error: {log.error_message}")
            if log.sent_at:
                print(f"  Sent at: {log.sent_at}")
        
        # Check SendGrid config
        print(f"\n⚙️  SendGrid Configuration:")
        print(f"  API Key configured: {'✅' if settings.sendgrid_api_key else '❌ NOT SET'}")
        print(f"  From Email: {settings.from_email if settings.from_email else '❌ NOT SET'}")
        
    finally:
        db.close()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python check_batch_status.py <batch_id>")
        print("\nTo find batch IDs, check the database or use:")
        print("  python -c \"from app.db import SessionLocal; from app.models import SendLog; db = SessionLocal(); batches = db.query(SendLog.batch_id).distinct().all(); [print(b[0]) for b in batches]; db.close()\"")
        sys.exit(1)
    
    batch_id = sys.argv[1]
    check_batch_status(batch_id)
