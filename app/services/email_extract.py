import re
from typing import List, Dict, Optional
from email_validator import validate_email, EmailNotValidError
import logging

logger = logging.getLogger(__name__)

# Enhanced regex pattern for email extraction (captures potential punctuation)
EMAIL_PATTERN = re.compile(
    r'[\(\{\[\s]*([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})[\)\}\],;:\s]*',
    re.IGNORECASE
)

# Patterns for extracting name and company (heuristic-based)
NAME_PATTERNS = [
    re.compile(r'(?:^|\n)([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\s*<?[A-Za-z0-9._%+-]+@', re.MULTILINE),
    re.compile(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\s*<?[A-Za-z0-9._%+-]+@', re.MULTILINE),
]

COMPANY_PATTERNS = [
    re.compile(r'@([A-Za-z0-9.-]+)\.(?:com|org|net|edu|gov|io|co)', re.IGNORECASE),
    re.compile(r'(?:Company|Corp|Inc|LLC|Ltd)[:\s]+([A-Za-z0-9\s&]+)', re.IGNORECASE),
]


def validate_email_address(email: str) -> bool:
    """
    Validate an email address using email-validator with stricter checks.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid, False otherwise
    """
    # Strip any remaining punctuation
    email = email.strip('(),[]{};:')
    
    # Check TLD length (must be at least 2 characters)
    if '.' in email:
        tld = email.split('.')[-1]
        if len(tld) < 2:
            return False
    
    try:
        validate_email(email, check_deliverability=False)
        return True
    except EmailNotValidError:
        return False


def extract_emails_from_text(text: str) -> List[Dict[str, Optional[str]]]:
    """
    Extract email addresses from text with optional name/company extraction.
    
    Args:
        text: Text content to extract emails from
        
    Returns:
        List of dictionaries with 'email', 'name', and 'company' keys,
        sorted by domain then email
    """
    # Find all potential email addresses (pattern captures email without punctuation)
    email_matches = EMAIL_PATTERN.findall(text)
    
    # Deduplicate case-insensitively and validate
    seen_emails = set()
    recipients = []
    
    for email in email_matches:
        # Strip punctuation around email
        email_clean = email.strip('(),[]{};:').strip()
        email_lower = email_clean.lower()
        
        # Skip if already seen
        if email_lower in seen_emails:
            continue
        
        # Validate email (includes TLD length check)
        if not validate_email_address(email_lower):
            logger.debug(f"Invalid email format: {email_clean}")
            continue
        
        seen_emails.add(email_lower)
        
        # Try to extract name and company (heuristic-based)
        name = extract_name_near_email(text, email_clean)
        company = extract_company_near_email(text, email_clean)
        
        recipients.append({
            'email': email_lower,
            'name': name,
            'company': company
        })
    
    # Sort by domain then email
    recipients.sort(key=lambda x: (x['email'].split('@')[1] if '@' in x['email'] else '', x['email']))
    
    return recipients


def extract_name_near_email(text: str, email: str) -> Optional[str]:
    """
    Try to extract a name near an email address using heuristics.
    
    Args:
        text: Full text content
        email: Email address to find name for
        
    Returns:
        Extracted name or None
    """
    # Find position of email in text
    email_pos = text.lower().find(email.lower())
    if email_pos == -1:
        return None
    
    # Look for name patterns before the email (within 100 chars)
    context_start = max(0, email_pos - 100)
    context = text[context_start:email_pos + len(email)]
    
    for pattern in NAME_PATTERNS:
        matches = pattern.findall(context)
        if matches:
            # Return the first match that looks like a name
            name = matches[0].strip()
            if len(name.split()) >= 2:  # At least first and last name
                return name
    
    return None


def extract_company_near_email(text: str, email: str) -> Optional[str]:
    """
    Try to extract a company name near an email address.
    
    Args:
        text: Full text content
        email: Email address to find company for
        
    Returns:
        Extracted company name or None
    """
    # Extract domain from email
    domain_match = re.search(r'@([A-Za-z0-9.-]+)\.', email)
    if domain_match:
        domain = domain_match.group(1)
        # Clean up common domain patterns
        domain = domain.replace('mail.', '').replace('www.', '')
        # Capitalize for display
        return domain.title()
    
    # Try to find company mentioned near email
    email_pos = text.lower().find(email.lower())
    if email_pos == -1:
        return None
    
    context_start = max(0, email_pos - 150)
    context_end = min(len(text), email_pos + len(email) + 50)
    context = text[context_start:context_end]
    
    for pattern in COMPANY_PATTERNS:
        matches = pattern.findall(context)
        if matches:
            return matches[0].strip()
    
    return None
