"""
Auto-Blogger Watchdog
Automatically resumes stale/incomplete jobs every 15 minutes.
"""

import logging
from backend.auto_blogger.job_state import get_job_state_manager
from backend.auto_blogger.worker import process_job

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def watchdog_check():
    """
    Find and resume stale jobs.
    Jobs are considered stale if not updated in 15+ minutes.
    """
    logger.info(" Watchdog: Checking for stale jobs...")
    
    job_mgr = get_job_state_manager()
    stale_jobs = job_mgr.find_stale_jobs(minutes=15)
    
    if not stale_jobs:
        logger.info("✅ No stale jobs found")
        return
    
    logger.info(f"⚠️ Found {len(stale_jobs)} stale job(s), resuming...")
    
    for job in stale_jobs:
        job_id = job['job_id']
        logger.info(f"🔄 Resum job: {job_id}")
        process_job(job_id)

if __name__ == "__main__":
    watchdog_check()
