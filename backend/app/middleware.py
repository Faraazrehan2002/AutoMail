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
        # Skip API key check for public endpoints
        public_paths = [
            "/health", "/docs", "/redoc", "/openapi.json", "/",
            "/auth/register", "/auth/login", "/auth/refresh"
        ]
        
        # Check if path starts with any public path
        if any(request.url.path == path or request.url.path.startswith(path + "/") for path in public_paths):
            return await call_next(request)
        
        # Also skip WebSocket connections (they use different auth)
        if request.url.path.startswith("/ws/"):
            return await call_next(request)
        
        # Check if API key is required
        if settings.app_api_key:
            api_key = request.headers.get("X-APP-KEY")
            
            # Allow requests with valid JWT token (Bearer auth) even without API key
            # This allows browser clients to use JWT while API key is for server-to-server
            auth_header = request.headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                # JWT token present, allow through (JWT validation happens in route)
                return await call_next(request)
            
            if not api_key or api_key != settings.app_api_key:
                logger.warning(f"Unauthorized access attempt to {request.url.path}")
                return Response(
                    content='{"detail":"Unauthorized: Invalid or missing API key"}',
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    media_type="application/json"
                )
        
        return await call_next(request)
