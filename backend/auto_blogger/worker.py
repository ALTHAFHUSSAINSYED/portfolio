"""
Auto-Blogger Worker
Executes pending blog generation jobs created by the scheduler.
"""

import logging
import sys
import os
from backend.auto_blogger.job_state import get_job_state_manager
from backend.auto_blogger.researcher import BlogResearcher
from backend.auto_blogger.writer import BlogWriter
from backend.auto_blogger.critic import BlogCritic
from backend.auto_blogger.publisher import BlogPublisher
from backend.auto_blogger.logger_utils import setup_agent_logger, update_job_metadata, IST
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_job(job_id: str):
    """
    Process a single blog generation job.
    
    Args:
        job_id: Unique job identifier
    """
    job_mgr = get_job_state_manager()
    job = job_mgr.load_job(job_id)
    
    if not job:
        logger.error(f"Job {job_id} not found")
        return False
    
    logger.info(f"🔄 Processing job {job_id} (status: {job['status']})")
    
    try:
        category = job['category']
        
        # Mark as in-progress
        job_mgr.update_status(job_id, "DRAFTING")
        
        # Step 1: Research (if not already done)
        research_data = job.get('metadata', {}).get('research_data')
        if not research_data:
            logger.info("Conducting research...")
            researcher = BlogResearcher()
            research_data = researcher.research_topic(category)
            
            # Save research to job metadata
            job_mgr.collection.update_one(
                {"job_id": job_id},
                {"$set": {"metadata.research_data": research_data}}
            )
        
        # Step 2: Generate Blog (Resumable)
        writer = BlogWriter()
        blog_content = writer.generate_blog(category, research_data, job_id=job_id)
        
        # Step 3: Critic Evaluation
        critic_logger = setup_agent_logger(job_id, "critic_evaluation")
        critic_logger.info("Starting quality evaluation...")
        
        critic = BlogCritic()
        passed, feedback = critic.evaluate(blog_content, category)
        
        critic_logger.info(f"Evaluation result: {'PASS' if passed else 'FAIL'}")
        critic_logger.info(f"Feedback: {feedback}")
        
        if not passed:
            logger.warning(f"Blog did not pass critic evaluation. Feedback: {feedback}")
            # Could implement revision loop here
        
        # Step 4: Publish
        publisher_logger = setup_agent_logger(job_id, "publisher_result")
        publisher_logger.info("Publishing blog...")
        
        publisher = BlogPublisher()
        blog_url = publisher.publish({
            "title": category,
            "category": category,
            "content": blog_content
        })
        
        publisher_logger.info(f"✅ Blog published: {blog_url}")
        
        # Mark complete
        job_mgr.mark_complete(job_id)
        update_job_metadata(job_id, {
            "published_url": blog_url,
            "completed_at": datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S IST')
        })
        
        logger.info(f"✅ Job {job_id} completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Job {job_id} failed: {e}", exc_info=True)
        job_mgr.update_status(job_id, "FAILED", error=str(e))
        job_mgr.increment_retries(job_id)
        update_job_metadata(job_id, {
            "failed_at": datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S IST'),
            "error": str(e)
        })
        return False

def process_all_pending_jobs():
    """Find and process all pending jobs"""
    job_mgr = get_job_state_manager()
    jobs = job_mgr.find_pending_jobs()
    
    if not jobs:
        logger.info("No pending jobs found")
        return
    
    logger.info(f"Found {len(jobs)} pending job(s)")
    
    for job in jobs:
        process_job(job['job_id'])

if __name__ == "__main__":
    logger.info("🤖 Auto-Blogger Worker started")
    process_all_pending_jobs()
    logger.info("✅ Worker finished")
