from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import logging

from .config import settings

logger = logging.getLogger(__name__)


class APIKeyMiddleware(BaseHTTPMiddleware):
    """Middleware to check API key for protected endpoints"""
    
    async def dispatch(self, request: Request, call_next):
        # Skip API key check for health endpoint and docs
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json", "/"]:
            return await call_next(request)
        
        # Check if API key is required
        if settings.app_api_key:
            api_key = request.headers.get("X-APP-KEY")
            
            if not api_key or api_key != settings.app_api_key:
                logger.warning(f"Unauthorized access attempt to {request.url.path}")
                return Response(
                    content='{"detail":"Unauthorized: Invalid or missing API key"}',
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    media_type="application/json"
                )
        
        return await call_next(request)
