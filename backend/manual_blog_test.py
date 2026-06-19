#!/usr/bin/env python3
"""
Manual Blog Generation Test - Simplified
Generates and publishes a blog WITHOUT critic validation
"""
import logging
import sys
import os
import asyncio  # Add for async support

# Configure logging to stdout explicitly
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(name)s] - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Force other loggers to info
logging.getLogger("BlogWriterAgent").setLevel(logging.INFO)
logging.getLogger("BlogWriterAgent").addHandler(logging.StreamHandler(sys.stdout))

async def main():
    logger.info("=" * 60)
    logger.info("MANUAL BLOG GENERATION TEST (No Critic)")
    logger.info("=" * 60)
    
    try:
        # Import modules
        logger.info("Importing auto-blogger modules...")
        from backend.auto_blogger.researcher import BlogResearcher
        from backend.auto_blogger.writer import BlogWriter
        from backend.auto_blogger.publisher import BlogPublisher
        from backend.auto_blogger.notifier import BlogNotifier  # ✅ ADD NOTIFIER
        
        # Initialize notifier
        notifier = BlogNotifier()
        
        # Step 1: Research
        logger.info("\n[1/3] Starting Research Phase...")
        researcher = BlogResearcher()
        category = "DevOps"
        research_data = researcher.analyze_trends(category)
        logger.info(f"✓ Research complete: {len(research_data.get('authoritative_sources', []))} sources found")
        
        # Step 2: Write
        logger.info("\n[2/3] Starting Writing Phase...")
        writer = BlogWriter()
        blog_data = writer.generate_blog(category, research_data)
        
        # Parse the result (now returns dict with metadata)
        if isinstance(blog_data, dict):
            # New format with metadata
            title = blog_data.get('title', f"Latest Insights in {category}")
            summary = blog_data.get('summary', '')
            draft = blog_data.get('content', '')
            logger.info(f"✓ Blog generated:")
            logger.info(f"   Title: {title}")
            logger.info(f"   Summary: {summary[:100]}...")
            logger.info(f"   Content: {len(draft)} characters")
        else:
            # Old format - just string content
            draft = blog_data
            import re
            title_match = re.search(r'#+\s*(.+)', draft)
            title = title_match.group(1).strip() if title_match else f"Latest Insights in {category}"
            summary = ""
            logger.info(f"✓ Draft generated: {len(draft)} characters")
        
        logger.info(f"Preview: {draft[:200]}...")
        
        # Step 3: Publish (NO CRITIC)
        logger.info("\n[3/3] Publishing directly (skipping critic)...")
        publisher = BlogPublisher()
        
        # Create blog object
        blog = {
            "title": title,
            "summary": summary,  # ✅ Add summary for card previews
            "content": draft,
            "category": category,
            "tags": [category.lower(), "technology", "devops", "automation"]
        }
        
        try:
            url = publisher.publish(blog)
            
            # ✅ SEND SUCCESS EMAIL
            await notifier.send_success(blog, url)
            
            logger.info("=" * 60)
            logger.info("✅ BLOG PUBLISHED SUCCESSFULLY!")
            logger.info("=" * 60)
            logger.info(f"Title: {title}")
            logger.info(f"Category: {category}")
            logger.info(f"URL: {url}")
            logger.info(f"Length: {len(draft)} characters")
            logger.info("📧 Success email sent!")
            
        except ValueError as ve:
            # Validation error (failed sections)
            logger.error(f"❌ VALIDATION FAILED: {ve}")
            await notifier.send_failure(
                str(ve),
                "Manual Blog Generation - Validation Failed",
                metadata={"category": category, "title": title}
            )
            logger.info("📧 Failure email sent!")
            return False
        
        # Verify file was created
        import os
        blog_dir = "/app/backend/generated_blogs"
        if os.path.exists(blog_dir):
            files = os.listdir(blog_dir)
            logger.info(f"\nGenerated blogs directory: {len(files)} file(s)")
            for f in files:
                logger.info(f"  - {f}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ FAILED: {e}", exc_info=True)
        
        # ✅ SEND FAILURE EMAIL
        try:
            await notifier.send_failure(
                str(e),
                "Manual Blog Generation - System Error", 
                metadata={"category": category if 'category' in locals() else "Unknown"}
            )
            logger.info("📧 Failure email sent!")
        except:
            logger.error("Could not send failure email")
        
        return False

if __name__ == "__main__":
    success = asyncio.run(main())  # ✅ Run async
    sys.exit(0 if success else 1)
