"""
Redis Queue setup for background job processing
"""
from redis import Redis
from rq import Queue
from ..config import settings
import logging

logger = logging.getLogger(__name__)

# Initialize Redis connection
redis_conn = None
email_queue = None


def get_redis_connection():
    """Get or create Redis connection"""
    global redis_conn
    if redis_conn is None:
        try:
            # Validate Redis URL
            redis_url = settings.redis_url
            if not redis_url:
                raise ValueError("REDIS_URL environment variable is not set")
            if not redis_url.startswith(('redis://', 'rediss://', 'unix://')):
                raise ValueError(f"Invalid Redis URL format. Must start with redis://, rediss://, or unix://. Got: {redis_url[:20]}...")
            
            # Don't use decode_responses=True - RQ needs binary data
            redis_conn = Redis.from_url(redis_url, decode_responses=False)
            # Test connection
            redis_conn.ping()
            logger.info(f"Connected to Redis successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            logger.error(f"REDIS_URL value: {settings.redis_url[:50] if settings.redis_url else 'NOT SET'}...")
            raise
    return redis_conn


def get_email_queue():
    """Get or create email queue"""
    global email_queue
    if email_queue is None:
        redis_conn = get_redis_connection()
        email_queue = Queue('emails', connection=redis_conn)
        logger.info("Email queue initialized")
    return email_queue
