from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, Personalization
from typing import Optional, Dict, Any
import logging
from ..config import settings

logger = logging.getLogger(__name__)


class SendGridClient:
    """Client for interacting with SendGrid API"""
    
    def __init__(self):
        if not settings.sendgrid_api_key:
            raise ValueError("SENDGRID_API_KEY not configured")
        if not settings.from_email:
            raise ValueError("FROM_EMAIL not configured")
        
        self.client = SendGridAPIClient(settings.sendgrid_api_key)
        self.from_email = settings.from_email
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        personalization: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Send an email via SendGrid.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML email body
            personalization: Optional personalization data
            
        Returns:
            SendGrid message ID if successful, None otherwise
            
        Raises:
            Exception: If sending fails
        """
        try:
            message = Mail(
                from_email=Email(self.from_email),
                to_emails=Email(to_email),
                subject=subject,
                html_content=html_content
            )
            
            # Add personalization if provided
            if personalization:
                personalization_obj = Personalization()
                personalization_obj.add_to(Email(to_email))
                
                for key, value in personalization.items():
                    personalization_obj.add_substitution(f"{{{{{key}}}}}", str(value))
                
                message.add_personalization(personalization_obj)
            
            response = self.client.send(message)
            
            if response.status_code in [200, 201, 202]:
                # Extract message ID from response headers
                message_id = response.headers.get('X-Message-Id')
                logger.info(f"Email sent successfully to {to_email}, message_id: {message_id}")
                return message_id
            else:
                error_body = response.body.decode('utf-8') if response.body else "Unknown error"
                logger.error(f"SendGrid API error: {response.status_code} - {error_body}")
                raise Exception(f"SendGrid API error: {response.status_code} - {error_body}")
                
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            raise
