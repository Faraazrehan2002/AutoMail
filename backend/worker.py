#!/usr/bin/env python3
"""
RQ Worker for processing email batches

Run this script to start a worker that processes email sending jobs from the queue.

Usage:
    python worker.py

Or with RQ directly:
    rq worker emails --url redis://localhost:6379/0
"""
import os
import sys
import logging

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

# Fix for macOS: Use threading instead of forking to avoid objc issues
os.environ['OBJC_DISABLE_INITIALIZE_FORK_SAFETY'] = 'YES'

from rq import Worker, Queue, Connection
from rq.worker import SimpleWorker
from app.services.queue import get_redis_connection

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    try:
        redis_conn = get_redis_connection()
        queue = Queue('emails', connection=redis_conn)
        
        logger.info("Starting RQ worker for 'emails' queue...")
        logger.info(f"Connected to Redis: {redis_conn.connection_pool.connection_kwargs}")
        
        with Connection(redis_conn):
            # Use SimpleWorker on macOS to avoid forking issues
            # SimpleWorker uses threading instead of forking
            worker = SimpleWorker([queue], connection=redis_conn)
            worker.work()
    except KeyboardInterrupt:
        logger.info("Worker stopped by user")
    except Exception as e:
        logger.error(f"Worker error: {e}", exc_info=True)
        sys.exit(1)
