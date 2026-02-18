from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # SendGrid Configuration (optional for development)
    sendgrid_api_key: Optional[str] = None
    from_email: Optional[str] = None
    
    # Database
    database_url: str = "sqlite:///./automail.db"
    
    # Rate Limiting (emails per second)
    emails_per_second: float = 1.0
    
    # Storage
    storage_dir: str = "./storage"
    
    # Max recipients per send request
    max_recipients_per_request: int = 200
    
    # Security
    app_api_key: Optional[str] = None  # API key for authentication
    
    # CORS
    allowed_origins: str = "*"  # Comma-separated list, or "*" for all
    
    # Redis (for job queue)
    redis_url: str = "redis://localhost:6379/0"
    
    # Development
    auto_migrate_dev: bool = False  # Auto-run migrations in dev (set AUTO_MIGRATE_DEV=true)
    
    # JWT Authentication
    jwt_secret_key: Optional[str] = None  # Will generate if not set
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30 * 24 * 60  # 30 days


settings = Settings()
