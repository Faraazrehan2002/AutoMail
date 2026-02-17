#!/usr/bin/env python3
"""
Smoke test script for AutoMail API.

This script tests the full workflow:
1. Upload a PDF
2. Fetch job details
3. Send emails to extracted recipients

Usage:
    python scripts/smoke_test.py [path_to_pdf]
    
Environment variables:
    API_BASE_URL: Base URL for the API (default: http://localhost:8000)
    API_KEY: API key for authentication (required)
    TEST_TO_EMAIL: Override recipient email (optional)
"""

import os
import sys
import requests
import json
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_KEY = os.getenv("API_KEY", "")
TEST_TO_EMAIL = os.getenv("TEST_TO_EMAIL", "")


def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def upload_pdf(pdf_path: str) -> dict:
    """Upload a PDF file"""
    print(f"Uploading PDF: {pdf_path}")
    
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    headers = {}
    if API_KEY:
        headers["X-APP-KEY"] = API_KEY
    
    with open(pdf_path, "rb") as f:
        files = {"file": (os.path.basename(pdf_path), f, "application/pdf")}
        response = requests.post(
            f"{API_BASE_URL}/upload",
            files=files,
            headers=headers
        )
    
    response.raise_for_status()
    job_data = response.json()
    print(f"✓ Upload successful")
    print(f"  Job ID: {job_data['id']}")
    print(f"  Status: {job_data['status']}")
    print(f"  Recipients found: {job_data['recipient_count']}")
    
    return job_data


def fetch_job_details(job_id: str) -> dict:
    """Fetch job details and recipients"""
    print(f"\nFetching job details for: {job_id}")
    
    headers = {}
    if API_KEY:
        headers["X-APP-KEY"] = API_KEY
    
    response = requests.get(
        f"{API_BASE_URL}/jobs/{job_id}",
        headers=headers
    )
    response.raise_for_status()
    job_data = response.json()
    
    print(f"✓ Job details retrieved")
    print(f"  Status: {job_data['status']}")
    print(f"  Total recipients: {job_data['recipient_count']}")
    
    if job_data.get('recipients'):
        print(f"\n  Sample recipients:")
        for i, recipient in enumerate(job_data['recipients'][:5], 1):
            print(f"    {i}. {recipient['email']}")
            if recipient.get('name'):
                print(f"       Name: {recipient['name']}")
            if recipient.get('company'):
                print(f"       Company: {recipient['company']}")
    
    return job_data


def send_emails(job_id: str, recipients: list, test_email: Optional[str] = None) -> dict:
    """Send emails to recipients"""
    # Select recipients
    if test_email:
        selected_recipients = [test_email]
        print(f"\nUsing test email: {test_email}")
    else:
        # Select first 1-3 recipients
        selected_recipients = [r['email'] for r in recipients[:3]]
        print(f"\nSelected {len(selected_recipients)} recipients for testing")
    
    print(f"Recipients: {', '.join(selected_recipients)}")
    
    # Prepare send request
    send_data = {
        "subject": "AutoMail Smoke Test",
        "html_body": """
        <html>
        <body>
            <h1>AutoMail Smoke Test</h1>
            <p>This is a test email sent from the AutoMail smoke test script.</p>
            <p>If you received this, the email sending functionality is working correctly!</p>
        </body>
        </html>
        """,
        "recipients": selected_recipients,
        "dry_run": False
    }
    
    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["X-APP-KEY"] = API_KEY
    
    print(f"\nSending emails...")
    response = requests.post(
        f"{API_BASE_URL}/jobs/{job_id}/send",
        json=send_data,
        headers=headers
    )
    response.raise_for_status()
    result = response.json()
    
    print(f"✓ Send request completed")
    print(f"  Batch ID: {result.get('batch_id', 'N/A')}")
    print(f"  Total recipients: {result['total_recipients']}")
    print(f"  Queued: {result['queued']}")
    print(f"  Sent: {result['sent']}")
    print(f"  Failed: {result['failed']}")
    
    if result.get('results'):
        print(f"\n  Results:")
        for r in result['results']:
            status_icon = "✓" if r['status'] == 'sent' else "✗"
            print(f"    {status_icon} {r['email']}: {r['status']}")
            if r.get('error_message'):
                print(f"      Error: {r['error_message']}")
            if r.get('sendgrid_message_id'):
                print(f"      Message ID: {r['sendgrid_message_id']}")
    
    return result


def main():
    """Main smoke test function"""
    print_section("AutoMail API Smoke Test")
    
    # Check API key
    if not API_KEY:
        print("⚠ Warning: API_KEY not set. Some endpoints may fail.")
        print("  Set API_KEY environment variable or configure APP_API_KEY in .env")
    
    # Get PDF path
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        # Try to find a sample PDF
        sample_pdfs = [
            "sample.pdf",
            "test.pdf",
            "example.pdf"
        ]
        pdf_path = None
        for pdf in sample_pdfs:
            if os.path.exists(pdf):
                pdf_path = pdf
                break
        
        if not pdf_path:
            print("Error: No PDF file provided and no sample PDF found.")
            print("Usage: python scripts/smoke_test.py [path_to_pdf]")
            sys.exit(1)
    
    try:
        # Step 1: Upload PDF
        print_section("Step 1: Upload PDF")
        job_data = upload_pdf(pdf_path)
        job_id = job_data['id']
        
        # Step 2: Fetch job details
        print_section("Step 2: Fetch Job Details")
        job_details = fetch_job_details(job_id)
        
        # Check if we have recipients
        recipients = job_details.get('recipients', [])
        if not recipients:
            print("\n⚠ No recipients found in PDF. Cannot proceed with email sending.")
            print("  You can provide TEST_TO_EMAIL environment variable to test with a specific email.")
            if TEST_TO_EMAIL:
                recipients = [{'email': TEST_TO_EMAIL}]
            else:
                print("\n✓ Smoke test completed (upload and extraction only)")
                return
        
        # Step 3: Send emails
        print_section("Step 3: Send Emails")
        send_result = send_emails(job_id, recipients, TEST_TO_EMAIL)
        
        # Summary
        print_section("Smoke Test Summary")
        print(f"✓ All steps completed successfully!")
        print(f"  Job ID: {job_id}")
        print(f"  Emails sent: {send_result['sent']}/{send_result['total_recipients']}")
        print(f"  Failed: {send_result['failed']}")
        
        if send_result['failed'] > 0:
            print(f"\n⚠ Some emails failed. Check the results above for details.")
            sys.exit(1)
        else:
            print(f"\n✓ All emails sent successfully!")
            sys.exit(0)
            
    except requests.exceptions.HTTPError as e:
        print(f"\n✗ HTTP Error: {e}")
        if e.response is not None:
            try:
                error_detail = e.response.json()
                print(f"  Details: {json.dumps(error_detail, indent=2)}")
            except:
                print(f"  Response: {e.response.text}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
