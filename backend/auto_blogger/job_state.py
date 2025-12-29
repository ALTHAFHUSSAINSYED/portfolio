"""
Job State Manager for Auto-Blogger
Handles MongoDB CRUD operations for job state tracking and resume capability.
"""

import os
from datetime import datetime
from typing import Optional, Dict, List
from pymongo import MongoClient
from bson import ObjectId
import pytz
import logging

logger = logging.getLogger(__name__)

# IST Timezone
IST = pytz.timezone('Asia/Kolkata')

class JobStateManager:
    """Manages auto-blogger job state in MongoDB"""
    
    def __init__(self):
        """Initialize MongoDB connection"""
        mongo_url = os.getenv('MONGO_URL')
        if not mongo_url:
            raise ValueError("MONGO_URL environment variable not set")
        
        self.client = MongoClient(mongo_url)
        self.db = self.client['portfolioDB']
        self.collection = self.db['blog_generation_jobs']
        
        # Create indexes for performance
        self.collection.create_index('job_id', unique=True)
        self.collection.create_index('status')
        self.collection.create_index('last_updated')
    
    def create_job(self, category: str) -> str:
        """
        Create a new blog generation job.
        
        Args:
            category: Blog category (e.g., "DevOps", "AI/ML")
            
        Returns:
            job_id: Unique job identifier
        """
        now_ist = datetime.now(IST)
        job_id = f"{category.replace('/', '-')}-{now_ist.strftime('%Y-%m-%d-%H%M%S')}"
        
        job_doc = {
            "job_id": job_id,
            "category": category,
            "status": "PENDING",
            "current_section": 0,
            "total_sections": 0,
            "outline": [],
            "sections": {},
            "metadata": {
                "started_at": now_ist,
                "last_updated": now_ist,
                "retries": 0,
                "error": None
            }
        }
        
        self.collection.insert_one(job_doc)
        logger.info(f"Created job {job_id} with status PENDING")
        
        return job_id
    
    def load_job(self, job_id: str) -> Optional[Dict]:
        """
        Load job state from MongoDB.
        
        Args:
            job_id: Unique job identifier
            
        Returns:
            Job document or None if not found
        """
        job = self.collection.find_one({"job_id": job_id})
        return job
    
    def update_status(self, job_id: str, status: str, error: str = None):
        """
        Update job status.
        
        Args:
            job_id: Unique job identifier
            status: New status (PENDING, DRAFTING, COMPLETED, FAILED)
            error: Optional error message
        """
        now_ist = datetime.now(IST)
        
        update_doc = {
            "$set": {
                "status": status,
                "metadata.last_updated": now_ist
            }
        }
        
        if error:
            update_doc["$set"]["metadata.error"] = error
        
        self.collection.update_one({"job_id": job_id}, update_doc)
        logger.info(f"Job {job_id} status updated to {status}")
    
    def save_outline(self, job_id: str, outline: List[str]):
        """
        Save generated outline to job.
        
        Args:
            job_id: Unique job identifier
            outline: List of section titles
        """
        now_ist = datetime.now(IST)
        
        self.collection.update_one(
            {"job_id": job_id},
            {
                "$set": {
                    "outline": outline,
                    "total_sections": len(outline),
                    "metadata.last_updated": now_ist
                }
            }
        )
        logger.info(f"Job {job_id} outline saved ({len(outline)} sections)")
    
    def save_section(self, job_id: str, section_index: int, content: str):
        """
        Save section content immediately after generation.
        
        Args:
            job_id: Unique job identifier
            section_index: Section number (0-indexed)
            content: Generated section content
        """
        now_ist = datetime.now(IST)
        
        self.collection.update_one(
            {"job_id": job_id},
            {
                "$set": {
                    f"sections.{section_index}": content,
                    "current_section": section_index + 1,
                    "metadata.last_updated": now_ist
                }
            }
        )
        logger.info(f"Job {job_id} section {section_index} saved ({len(content)} chars)")
    
    def get_completed_sections(self, job_id: str) -> Dict[int, str]:
        """
        Get all completed sections for a job.
        
        Args:
            job_id: Unique job identifier
            
        Returns:
            Dictionary of {section_index: content}
        """
        job = self.load_job(job_id)
        if not job:
            return {}
        
        sections = job.get('sections', {})
        # Convert string keys back to integers
        return {int(k): v for k, v in sections.items() if v is not None}
    
    def mark_complete(self, job_id: str):
        """
        Mark job as completed successfully.
        
        Args:
            job_id: Unique job identifier
        """
        now_ist = datetime.now(IST)
        
        self.collection.update_one(
            {"job_id": job_id},
            {
                "$set": {
                    "status": "COMPLETED",
                    "metadata.completed_at": now_ist,
                    "metadata.last_updated": now_ist
                }
            }
        )
        logger.info(f"Job {job_id} marked as COMPLETED")
    
    def find_pending_jobs(self) -> List[Dict]:
        """
        Find all jobs with status PENDING or DRAFTING.
        
        Returns:
            List of job documents
        """
        jobs = list(self.collection.find({
            "status": {"$in": ["PENDING", "DRAFTING"]}
        }))
        return jobs
    
    def find_stale_jobs(self, minutes: int = 15) -> List[Dict]:
        """
        Find jobs that haven't been updated in N minutes.
        Useful for watchdog to detect stuck jobs.
        
        Args:
            minutes: Threshold for stale jobs
            
        Returns:
            List of stale job documents
        """
        from datetime import timedelta
        
        cutoff = datetime.now(IST) - timedelta(minutes=minutes)
        
        jobs = list(self.collection.find({
            "status": {"$in": ["PENDING", "DRAFTING"]},
            "metadata.last_updated": {"$lt": cutoff}
        }))
        
        return jobs
    
    def increment_retries(self, job_id: str):
        """
        Increment retry counter for a job.
        
        Args:
            job_id: Unique job identifier
        """
        self.collection.update_one(
            {"job_id": job_id},
            {"$inc": {"metadata.retries": 1}}
        )
    
    def cleanup_old_jobs(self, days: int = 30):
        """
        Delete jobs older than N days.
        
        Args:
            days: Retention period
        """
        from datetime import timedelta
        
        cutoff = datetime.now(IST) - timedelta(days=days)
        
        result = self.collection.delete_many({
            "metadata.started_at": {"$lt": cutoff}
        })
        
        logger.info(f"Cleaned up {result.deleted_count} jobs older than {days} days")


# Global instance
_job_state_manager = None

def get_job_state_manager() -> JobStateManager:
    """Get singleton instance of JobStateManager"""
    global _job_state_manager
    if _job_state_manager is None:
        _job_state_manager = JobStateManager()
    return _job_state_manager
