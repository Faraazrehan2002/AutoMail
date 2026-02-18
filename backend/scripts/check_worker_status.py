#!/usr/bin/env python3
"""
Check RQ worker and queue status
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.services.queue import get_redis_connection
from rq import Queue, Worker

def check_worker_status():
    """Check if workers are running and queue status"""
    try:
        redis_conn = get_redis_connection()
        queue = Queue('emails', connection=redis_conn)
        
        # Get all workers
        workers = Worker.all(connection=redis_conn)
        print(f"\n🔧 Workers: {len(workers)} active")
        for worker in workers:
            print(f"  - {worker.name} (PID: {worker.pid})")
            print(f"    State: {worker.get_state()}")
            current_job = worker.get_current_job()
            if current_job:
                print(f"    Current job: {current_job.id}")
                print(f"    Job function: {current_job.func_name}")
            else:
                print(f"    Current job: None (idle)")
        
        # Get queue status
        print(f"\n📬 Queue 'emails':")
        print(f"  Jobs in queue: {len(queue)}")
        print(f"  Failed jobs: {len(queue.failed_job_registry)}")
        
        if len(queue) > 0:
            print(f"\n  Queued jobs:")
            for job in queue.jobs:
                print(f"    - {job.id}")
                print(f"      Function: {job.func_name}")
                print(f"      Args: {job.args}")
                print(f"      Created: {job.created_at}")
        
        if len(queue.failed_job_registry) > 0:
            print(f"\n  Failed jobs:")
            for job_id in queue.failed_job_registry.get_job_ids():
                job = queue.failed_job_registry.job_class.fetch(job_id, connection=redis_conn)
                print(f"    - {job_id}")
                print(f"      Error: {job.exc_info}")
        
        if len(workers) == 0:
            print("\n⚠️  WARNING: No workers are running!")
            print("   Start a worker with: python worker.py")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    check_worker_status()
