#!/usr/bin/env python3
"""
Scheduler process for processing scheduled email batches

Run this as a separate process to check for and enqueue scheduled batches.

Usage:
    python scheduler.py
"""
import os
import sys
import logging

sys.path.insert(0, os.path.dirname(__file__))

from app.services.scheduler import run_scheduler_loop

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

if __name__ == '__main__':
    try:
        run_scheduler_loop(interval_seconds=60)  # Check every minute
    except KeyboardInterrupt:
        logging.info("Scheduler stopped by user")
    except Exception as e:
        logging.error(f"Scheduler error: {e}", exc_info=True)
        sys.exit(1)
