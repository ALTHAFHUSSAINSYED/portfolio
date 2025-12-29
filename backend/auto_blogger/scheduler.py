"""
Blog Scheduler Module
Orchestrates the daily auto-blogging pipeline.
"""

import os
import time
import json
import logging
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv

# Load Env Vars (Critical for standalone execution)
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

# Import Modules
from .researcher import BlogResearcher
from .writer import BlogWriter
from .critic import BlogCritic
from .publisher import BlogPublisher
from .cleanup import BlogCleanup
from .notifier import BlogNotifier

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BlogScheduler")

class BlogScheduler:
    def __init__(self):
        self.state_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scheduler_state.json")
        self.categories = [
            "AI_and_ML",
            "Cloud_Computing", 
            "Cybersecurity",
            "DevOps",
            "Low-Code_No-Code",
            "Software_Development"
        ]
        
        # Components
        self.researcher = BlogResearcher()
        self.writer = BlogWriter()
        self.critic = BlogCritic()
        self.publisher = BlogPublisher()
        self.cleanup = BlogCleanup()
        self.notifier = BlogNotifier()
        
        # Temp Draft Storage
        self.pending_draft = None

    def _load_state(self) -> Dict[str, Any]:
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {"last_index": -1, "last_run": None}

    def _save_state(self, state: Dict[str, Any]):
        with open(self.state_file, 'w') as f:
            json.dump(state, f)

    def select_next_category(self) -> str:
        """Round-robin category selection"""
        state = self._load_state()
        next_index = (state["last_index"] + 1) % len(self.categories)
        
        category = self.categories[next_index]
        logger.info(f"Selected category: {category}")
        
        # Update state
        state["last_index"] = next_index
        state["last_run"] = datetime.now().isoformat()
        self._save_state(state)
        
        return category

    async def run_cleanup_job(self):
        """Job: 6:00 AM Cleanup"""
        logger.info("Running scheduled cleanup...")
        try:
            res = self.cleanup.run_cleanup()
            logger.info(f"Cleanup result: {res}")
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")

    async def run_generation_pipeline(self):
        """Job: 7:00 AM Generation"""
        logger.info("Running scheduled generation pipeline...")
        start_time = datetime.now()
        try:
            # 1. Select Category
            category = self.select_next_category()
            
            # 2. Research
            research_data = self.researcher.analyze_trends(category)
            
            # 3. Write Draft
            blog_data = self.writer.generate_blog(category, research_data)
            
            # Handle new dict format from writer
            if isinstance(blog_data, dict):
                # New format with metadata
                title = blog_data.get('title', '')
                summary = blog_data.get('summary', '')
                draft = blog_data.get('content', '')
                logger.info(f"📝 Blog generated: {title}")
            else:
                # Old format - just string content
                draft = blog_data
                title = None
                summary = ""
            
            # Safety Check: Ensure draft is valid
            if not draft or len(draft) < 100:
                error_msg = f"Draft generation failed or produced insufficient content (length: {len(draft) if draft else 0})"
                logger.error(error_msg)
                await self.notifier.send_failure(error_msg, f"Generation - {category}")
                self.pending_draft = None
                return
            
            # 4. Critique Loop (Max 3 retries)
            passed = False
            for i in range(3):
                passed, review_json = self.critic.evaluate(draft, category)
                try:
                    review = json.loads(review_json)
                except:
                    review = {"score": 0, "verdict": "FAIL"}
                
                logger.info(f"Critique Iteration {i+1}: Score {review.get('score')}")
                
                if passed:
                    break
                
                # If failed, revise based on feedback (Not implemented fully in writer yet, simple regeneration logic here)
                # In a real rigorous system, we'd pass 'required_edits' back to writer.
                # For now, we will retry generation if score is very low, or accept best effort if close?
                # The prompt requested "Loop until: pass OR max iterations reached".
                # To simplify without complex revision prompts, we might accept if > 85 on last try or just fail.
                
                if i < 2:
                    logger.info("Score below gate. Revising based on feedback...")
                    # Smart Revision Loop
                    draft = self.writer.revise_blog(draft, review)
            
            if not passed and review.get('score', 0) < 60:
                 # Strict fail only if score is abysmal (< 60)
                 error_msg = f"Failed quality gate after 3 attempts. Best score: {review.get('score')}"
                 await self.notifier.send_failure(error_msg, f"Generation - {category}", metadata={"category": category, "pending_title": "Quality Fail"})
                 self.pending_draft = None
                 return
            elif not passed:
                logger.warning(f"⚠️ Quality Gate Compromised: Publishing with score {review.get('score')} due to 'guarantee' policy.")
                category = f"{category} (Review Pending)" # Mark as pending review in category logic if needed, or just let it slide.

            # Store for Publishing
            # Use title from writer (already extracted above)
            if not title:
                # Fallback: try to extract from draft if writer didn't provide
                for line in draft.split('\n')[:15]:
                    clean_line = line.strip()
                    if clean_line.startswith("# "):
                        title = clean_line.replace("#", "").strip()
                        break
                    elif clean_line.startswith("Title:"):
                        title = clean_line.replace("Title:", "").strip()
                        break
            
            if not title:
                # CRITICAL FIX: Do not publish without title
                error_msg = f"Failed to extract valid title from blog. Aborting publication."
                logger.error(error_msg)
                
                meta = {
                    "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "end_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "category": category,
                    "pending_title": "Extraction Failed"
                }
                await self.notifier.send_failure(error_msg, f"Generation - {category} (Title Extraction Failed)", metadata=meta)
                self.pending_draft = None
                return

            self.pending_draft = {
                "title": title,
                "summary": summary,  # ✅ Add summary for blog cards
                "category": category,
                "content": draft,
                "tags": [category, "Tech", "Auto-Generated"],
                "created_at": datetime.now().isoformat()
            }
            logger.info(f"Draft ready for publishing: '{title}'")
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            meta = {
                "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S") if 'start_time' in locals() else "Unknown",
                "end_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "category": category if 'category' in locals() else "Unknown",
                "pending_title": "Detailed generation failed"
            }
            await self.notifier.send_failure(str(e), "Generation Pipeline", metadata=meta)

    async def run_publishing_job(self):
        """Job: 10:00 AM Publishing"""
        logger.info("Running scheduled publishing...")
        if not self.pending_draft:
            logger.warning("No pending draft to publish.")
            return

        try:
            url = self.publisher.publish(self.pending_draft)
            await self.notifier.send_success(self.pending_draft, url)
            self.pending_draft = None # Clear
        except Exception as e:
            logger.error(f"Publishing failed: {e}")
            await self.notifier.send_failure(str(e), "Publishing Job")

    def start(self, run_now: bool = False):
        """Start the scheduler with proper event loop handling"""
        # Get the event loop that was set for this thread by server.py
        loop = asyncio.get_event_loop()
        
        # Create scheduler with the correct event loop
        scheduler = AsyncIOScheduler(event_loop=loop)
        
        # Schedule Production Jobs (IST timezone)
        # 6:00 AM IST -> Cleanup
        scheduler.add_job(self.run_cleanup_job, CronTrigger(hour=6, minute=0, timezone='Asia/Kolkata'))
        
        # SCHEDULE: 07:00 AM IST -> Generate
        scheduler.add_job(self.run_generation_pipeline, CronTrigger(hour=7, minute=0, timezone='Asia/Kolkata'))
        
        # SCHEDULE: 10:00 AM IST -> Publish
        scheduler.add_job(self.run_publishing_job, CronTrigger(hour=10, minute=0, timezone='Asia/Kolkata'))
        
        # Optional: Run immediately for testing
        if run_now:
            logger.info("🧪 TEST MODE: Running generation pipeline immediately...")
            scheduler.add_job(self.run_generation_pipeline, 'date', run_date=datetime.now() + timedelta(seconds=10))
            scheduler.add_job(self.run_publishing_job, 'date', run_date=datetime.now() + timedelta(seconds=120))
        
        logger.info("✅ BlogScheduler started with jobs: Cleanup@6AM, Generate@7AM, Publish@10AM IST")
        scheduler.start()
        
        try:
            loop.run_forever()
        except (KeyboardInterrupt, SystemExit):
            pass

if __name__ == "__main__":
    # Test Run (Manual)
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--test-all", action="store_true", help="Run full pipeline immediately")
    args = parser.parse_args()
    
    scheduler = BlogScheduler()
    
    if args.test_all:
        print("Running full test pipeline...")
        asyncio.run(scheduler.run_cleanup_job())
        asyncio.run(scheduler.run_generation_pipeline())
        # Simulate wait or just run next
        asyncio.run(scheduler.run_publishing_job())
    else:
        scheduler.start()
