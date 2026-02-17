import pdfplumber
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Try to import pypdf as fallback
try:
    from pypdf import PdfReader
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False
    logger.warning("pypdf not available, will only use pdfplumber")


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from PDF using pdfplumber first, then pypdf as fallback.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Extracted text as string
        
    Raises:
        ValueError: If PDF appears to be scanned/image-based with no extractable text
    """
    # Try pdfplumber first
    text = _extract_with_pdfplumber(file_path)
    
    # If pdfplumber returns empty/very small text, try pypdf
    if not text or len(text.strip()) < 10:
        logger.info("pdfplumber returned minimal text, trying pypdf fallback")
        if PYPDF_AVAILABLE:
            text = _extract_with_pypdf(file_path)
        else:
            logger.warning("pypdf not available, cannot use fallback")
    
    # Final check
    if not text or len(text.strip()) < 10:
        error_response = {
            "error_code": "PDF_SCANNED_NO_TEXT",
            "message": "PDF appears to be scanned or contains no extractable text. Please enable OCR or provide a PDF with selectable text."
        }
        raise ValueError(str(error_response))
    
    return text


def _extract_with_pdfplumber(file_path: str) -> str:
    """Extract text using pdfplumber"""
    try:
        text_content = []
        
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_content.append(page_text)
        
        return "\n".join(text_content)
    except Exception as e:
        logger.warning(f"pdfplumber extraction failed: {str(e)}")
        return ""


def _extract_with_pypdf(file_path: str) -> str:
    """Extract text using pypdf as fallback"""
    try:
        reader = PdfReader(file_path)
        text_content = []
        
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_content.append(page_text)
        
        return "\n".join(text_content)
    except Exception as e:
        logger.warning(f"pypdf extraction failed: {str(e)}")
        return ""
