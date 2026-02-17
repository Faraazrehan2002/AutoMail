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
            redis_conn = Redis.from_url(settings.redis_url, decode_responses=True)
            # Test connection
            redis_conn.ping()
            logger.info(f"Connected to Redis at {settings.redis_url}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
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
