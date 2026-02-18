from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, Personalization, Attachment, FileContent, FileName, FileType, Disposition
from typing import Optional, Dict, Any, List
import logging
import base64
import os
import mimetypes
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
        personalization: Optional[Dict[str, Any]] = None,
        attachments: Optional[List[str]] = None
    ) -> Optional[str]:
        """
        Send an email via SendGrid.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML email body
            personalization: Optional personalization data
            attachments: Optional list of file paths for attachments
            
        Returns:
            SendGrid message ID if successful, None otherwise
            
        Raises:
            Exception: If sending fails
        """
        try:
            # Create Mail object - when using personalization, don't set to_emails in constructor
            if personalization:
                # Use personalization for custom substitutions
                message = Mail(
                    from_email=Email(self.from_email),
                    subject=subject,
                    html_content=html_content
                )
                personalization_obj = Personalization()
                personalization_obj.add_to(Email(to_email))
                
                for key, value in personalization.items():
                    personalization_obj.add_substitution(f"{{{{{key}}}}}", str(value))
                
                message.add_personalization(personalization_obj)
            else:
                # Simple case: no personalization, set to_emails in constructor
                message = Mail(
                    from_email=Email(self.from_email),
                    to_emails=to_email,  # String works fine
                    subject=subject,
                    html_content=html_content
                )
            
            # Add attachments if provided
            if attachments:
                for file_path in attachments:
                    try:
                        if os.path.exists(file_path):
                            with open(file_path, 'rb') as f:
                                file_data = f.read()
                                encoded_file = base64.b64encode(file_data).decode()
                                
                                # Detect MIME type
                                mime_type, _ = mimetypes.guess_type(file_path)
                                if not mime_type:
                                    mime_type = 'application/octet-stream'
                                
                                attachment = Attachment()
                                attachment.file_content = FileContent(encoded_file)
                                attachment.file_name = FileName(os.path.basename(file_path))
                                attachment.file_type = FileType(mime_type)
                                attachment.disposition = Disposition('attachment')
                                
                                message.add_attachment(attachment)
                                logger.info(f"Added attachment: {os.path.basename(file_path)}")
                    except Exception as e:
                        logger.warning(f"Failed to add attachment {file_path}: {e}")
            
            response = self.client.send(message)
            
            if response.status_code in [200, 201, 202]:
                # Extract message ID from response headers
                message_id = response.headers.get('X-Message-Id')
                logger.info(f"Email sent successfully to {to_email}, message_id: {message_id}")
                return message_id
            else:
                # Get detailed error information
                try:
                    error_body = response.body.decode('utf-8') if response.body else "Unknown error"
                except:
                    error_body = str(response.body) if response.body else "Unknown error"
                
                error_headers = dict(response.headers) if response.headers else {}
                
                # Log detailed error information
                logger.error(f"SendGrid API error: {response.status_code}")
                logger.error(f"From email: {self.from_email}")
                logger.error(f"To email: {to_email}")
                logger.error(f"Error body: {error_body}")
                logger.error(f"Error headers: {error_headers}")
                
                # Provide helpful error message based on status code
                if response.status_code == 403:
                    error_msg = (
                        f"SendGrid API returned 403 Forbidden.\n"
                        f"FROM_EMAIL: {self.from_email}\n"
                        f"This usually means:\n"
                        f"1. The 'from_email' address ({self.from_email}) is NOT verified in SendGrid\n"
                        f"   → Go to SendGrid Dashboard → Settings → Sender Authentication\n"
                        f"   → Verify 'Single Sender' or authenticate your domain\n"
                        f"2. Your API key doesn't have 'Mail Send' permissions\n"
                        f"   → Go to Settings → API Keys → Edit your key → Enable 'Mail Send'\n"
                        f"3. Your SendGrid account has restrictions\n"
                        f"\nSendGrid Response: {error_body}"
                    )
                else:
                    error_msg = f"SendGrid API error: {response.status_code} - {error_body}"
                
                raise Exception(error_msg)
                
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            raise
