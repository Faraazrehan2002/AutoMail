from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from .db import init_db
from .routers import jobs, health, auth, websocket, templates, scheduling, analytics, attachments
from .config import settings
from .middleware import APIKeyMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AutoMail API",
    description="PDF email extraction and sending service",
    version="1.0.0"
)

# Parse allowed origins from env
allowed_origins = ["*"]  # Default
if settings.allowed_origins and settings.allowed_origins != "*":
    allowed_origins = [origin.strip() for origin in settings.allowed_origins.split(",")]

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Key middleware (if configured)
if settings.app_api_key:
    app.add_middleware(APIKeyMiddleware)
    logger.info("API key authentication enabled")
else:
    logger.warning("API key not configured - API is open. Set APP_API_KEY in .env for security.")

# Initialize database
@app.on_event("startup")
async def startup_event():
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized")
    
    # Check migrations in development
    from .migration_check import check_migrations, auto_migrate_dev
    auto_migrate_dev()  # Auto-migrate if AUTO_MIGRATE_DEV=true
    check_migrations()  # Warn if migrations are behind
    
    # Ensure storage directory exists
    import os
    os.makedirs(settings.storage_dir, exist_ok=True)
    logger.info(f"Storage directory ready: {settings.storage_dir}")


# Include routers
app.include_router(auth.router)
app.include_router(attachments.router)
app.include_router(jobs.router, tags=["jobs"])
app.include_router(health.router, tags=["health"])
app.include_router(websocket.router, tags=["websocket"])
app.include_router(templates.router)
app.include_router(scheduling.router)
app.include_router(analytics.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AutoMail API",
        "version": "1.0.0",
        "docs": "/docs"
    }
