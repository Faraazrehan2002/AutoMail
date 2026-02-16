"""Migration safety check for development"""
import logging
import os
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.runtime.migration import MigrationContext
from sqlalchemy import create_engine

from .config import settings

logger = logging.getLogger(__name__)


def check_migrations():
    """Check if database migrations are up to date"""
    try:
        # Get Alembic config
        alembic_cfg = Config("alembic.ini")
        script = ScriptDirectory.from_config(alembic_cfg)
        
        # Get current database revision
        engine = create_engine(
            settings.database_url,
            connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
        )
        
        with engine.connect() as connection:
            context = MigrationContext.configure(connection)
            current_rev = context.get_current_revision()
        
        # Get head revision
        head_rev = script.get_current_head()
        
        if current_rev != head_rev:
            logger.warning("=" * 60)
            logger.warning("⚠️  DATABASE SCHEMA OUT OF DATE")
            logger.warning("=" * 60)
            logger.warning(f"Current revision: {current_rev or 'None (no migrations applied)'}")
            logger.warning(f"Head revision: {head_rev}")
            logger.warning("")
            logger.warning("To update, run:")
            logger.warning("  alembic upgrade head")
            logger.warning("=" * 60)
            return False
        
        logger.info("✓ Database schema is up to date")
        return True
        
    except Exception as e:
        logger.error(f"Error checking migrations: {e}")
        # Don't fail startup if migration check fails
        return True


def auto_migrate_dev():
    """Auto-run migrations in development if enabled"""
    auto_migrate = settings.auto_migrate_dev or os.getenv("AUTO_MIGRATE_DEV", "false").lower() == "true"
    
    if not auto_migrate:
        return
    
    try:
        logger.info("AUTO_MIGRATE_DEV=true - Running migrations automatically...")
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        logger.info("✓ Migrations completed")
    except Exception as e:
        logger.error(f"Failed to auto-run migrations: {e}")
        raise
