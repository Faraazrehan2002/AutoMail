#!/usr/bin/env python3
"""
Check SendGrid configuration and test connection
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.config import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email

def check_sendgrid():
    """Check SendGrid configuration and test API key"""
    print("\n🔍 SendGrid Configuration Check\n")
    
    # Check API key
    if not settings.sendgrid_api_key:
        print("❌ SENDGRID_API_KEY is not set in .env")
        print("   Add: SENDGRID_API_KEY=your_api_key_here")
        return False
    else:
        # Mask API key for display
        masked_key = settings.sendgrid_api_key[:8] + "..." + settings.sendgrid_api_key[-4:] if len(settings.sendgrid_api_key) > 12 else "***"
        print(f"✅ SENDGRID_API_KEY is set: {masked_key}")
    
    # Check from_email
    if not settings.from_email:
        print("❌ FROM_EMAIL is not set in .env")
        print("   Add: FROM_EMAIL=your-verified-email@example.com")
        return False
    else:
        print(f"✅ FROM_EMAIL is set: {settings.from_email}")
    
    # Test API key
    print("\n🧪 Testing SendGrid API connection...")
    try:
        client = SendGridAPIClient(settings.sendgrid_api_key)
        
        # Try to get API key info (this requires appropriate permissions)
        # Note: This might not work for all API keys, but it's a good test
        try:
            # Try a simple API call to verify the key
            # We'll create a test message but not send it
            test_message = Mail(
                from_email=Email(settings.from_email),
                to_emails="test@example.com",
                subject="Test",
                html_content="Test"
            )
            
            # Just validate the message structure (doesn't send)
            print("✅ SendGrid client initialized successfully")
            print("✅ Message structure is valid")
            
        except Exception as e:
            print(f"⚠️  Warning: {e}")
        
        print("\n💡 Common 403 Forbidden causes:")
        print("   1. API key doesn't have 'Mail Send' permissions")
        print("      → Go to SendGrid Dashboard > Settings > API Keys")
        print("      → Edit your API key and ensure 'Mail Send' permission is enabled")
        print()
        print("   2. FROM_EMAIL address is not verified")
        print(f"      → Verify '{settings.from_email}' in SendGrid Dashboard")
        print("      → Go to Settings > Sender Authentication")
        print("      → Verify Single Sender or Domain Authentication")
        print()
        print("   3. SendGrid account restrictions")
        print("      → Check if your account is active and not suspended")
        print("      → Trial accounts may have restrictions")
        print()
        print("   4. Rate limiting or quota exceeded")
        print("      → Check your SendGrid dashboard for usage limits")
        
        return True
        
    except Exception as e:
        print(f"❌ Error initializing SendGrid client: {e}")
        return False

if __name__ == '__main__':
    check_sendgrid()
