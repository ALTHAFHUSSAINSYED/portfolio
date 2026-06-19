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
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env.local'))

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
        # CRITICAL FIX: Move state file to persistent volume (not code directory)
        # This prevents state loss during Docker rebuilds and git pulls
        self.state_file = "/app/backend/logs/auto_blogger/scheduler_state.json"
        # FIXED: Use frontend-compatible category names (spaces instead of underscores)
        self.categories = [
            "AI and ML",
            "Cloud Computing", 
            "Cybersecurity",
            "DevOps",
            "Low-Code/No-Code",
            "Software Development"
        ]
        
        # Components
        self.researcher = BlogResearcher()
        self.writer = BlogWriter()
        self.critic = BlogCritic()
        self.publisher = BlogPublisher()
        self.cleanup = BlogCleanup()
        self.notifier = BlogNotifier()
        
        # Temp Draft Storage (with disk persistence)
        self.pending_draft = None
        self.draft_file = "/app/backend/logs/auto_blogger/pending_draft.json"

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
        logger.info(f"⏱️ Pipeline started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        try:
            # 1. Select Category
            category = self.select_next_category()
            
            # 2. Research
            research_start = datetime.now()
            research_data = self.researcher.analyze_trends(category)
            research_time = (datetime.now() - research_start).total_seconds()
            logger.info(f"⏱️ Research completed in {research_time:.1f}s")
            
            # 3. Write Draft
            draft_start = datetime.now()
            blog_data = self.writer.generate_blog(category, research_data)
            draft_time = (datetime.now() - draft_start).total_seconds()
            logger.info(f"⏱️ Drafting completed in {draft_time:.1f}s ({draft_time/60:.1f} minutes)")
            
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
            
            # 4. Critique Loop (Max 2 iterations - reduced from 3)
            # CRITICAL: Revision is risky and can corrupt content. Only revise if score < 75.
            critique_start = datetime.now()
            passed = False
            for i in range(2):  # Reduced from 3 to 2 iterations
                passed, review_json = self.critic.evaluate(draft, category)
                try:
                    review = json.loads(review_json)
                except:
                    review = {"score": 0, "verdict": "FAIL"}
                
                score = review.get('score', 0)
                logger.info(f"Critique Iteration {i+1}: Score {score}, Verdict: {review.get('verdict')}")
                
                # Accept if passed OR score >= 75 (acceptable quality)
                if passed or score >= 75:
                    if not passed and score >= 75:
                        logger.info(f"✅ Score {score} is acceptable (>= 75). Skipping revision to avoid corruption risk.")
                    break
                
                # Only revise if score < 75 AND we have attempts left
                if i < 1 and score < 75:  # Only 1 revision attempt (i=0)
                    logger.warning(f"⚠️ Score {score} < 75. Attempting revision (RISKY OPERATION)...")
                    draft = self.writer.revise_blog(draft, review)
                else:
                    logger.info(f"Score {score} < 75 but no revision attempts left. Proceeding with current draft.")
            
            critique_time = (datetime.now() - critique_start).total_seconds()
            logger.info(f"⏱️ Critique loop completed in {critique_time:.1f}s")
            
            if not passed and review.get('score', 0) < 60:
                 # Strict fail only if score is abysmal (< 60)
                 error_msg = f"Failed quality gate after 3 attempts. Best score: {review.get('score')}"
                 await self.notifier.send_failure(error_msg, f"Generation - {category}", metadata={"category": category, "pending_title": "Quality Fail"})
                 self.pending_draft = None
                 return
            elif not passed:
                logger.warning(f"⚠️ Quality Gate Compromised: Publishing with score {review.get('score')} due to 'guarantee' policy. (Auto-publishing without review flag as per user request)")
                # category = category # KEEP ORIGINAL CATEGORY. Do not append (Review Pending)

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
                "summary": summary,
                "category": category,
                "content": draft,
                "tags": [category, "Tech", "Auto-Generated"],
                "created_at": datetime.now().isoformat(),
                "gen_start_time": start_time.isoformat(),
                "gen_end_time": datetime.now().isoformat()
            }
            
            # CRITICAL FIX: Persist draft to disk (survives Docker rebuilds)
            try:
                with open(self.draft_file, 'w') as f:
                    json.dump(self.pending_draft, f, indent=2)
                logger.info(f"✅ Draft persisted to disk: {self.draft_file}")
            except Exception as e:
                logger.warning(f"Failed to persist draft to disk: {e}")
            
            total_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"⏱️ TOTAL PIPELINE TIME: {total_time:.1f}s ({total_time/60:.1f} minutes)")
            logger.info(f"   - Research: {research_time:.1f}s")
            logger.info(f"   - Drafting: {draft_time:.1f}s")
            logger.info(f"   - Critique: {critique_time:.1f}s")
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
        
        # CRITICAL FIX: Load draft from disk if not in memory (Docker rebuild recovery)
        if not self.pending_draft and os.path.exists(self.draft_file):
            try:
                with open(self.draft_file, 'r') as f:
                    self.pending_draft = json.load(f)
                logger.info(f"✅ Recovered draft from disk: {self.pending_draft.get('title')}")
            except Exception as e:
                logger.error(f"Failed to load draft from disk: {e}")
        
        if not self.pending_draft:
            logger.warning("No pending draft to publish.")
            return

        try:
            url = self.publisher.publish(self.pending_draft)
            await self.notifier.send_success(self.pending_draft, url)
            self.pending_draft = None # Clear memory
            
            # CRITICAL FIX: Remove draft file after successful publish
            if os.path.exists(self.draft_file):
                os.remove(self.draft_file)
                logger.info(f"✅ Removed draft file after successful publish")
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
