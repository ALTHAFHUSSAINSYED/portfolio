#!/usr/bin/env python3
"""
Manual Blog Generation Test - Simplified
Generates and publishes a blog WITHOUT critic validation
"""
import logging
import sys
import os

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

def main():
    logger.info("=" * 60)
    logger.info("MANUAL BLOG GENERATION TEST (No Critic)")
    logger.info("=" * 60)
    
    try:
        # Import modules
        logger.info("Importing auto-blogger modules...")
        from backend.auto_blogger.researcher import BlogResearcher
        from backend.auto_blogger.writer import BlogWriter
        from backend.auto_blogger.publisher import BlogPublisher
        
        # Step 1: Research
        logger.info("\n[1/3] Starting Research Phase...")
        researcher = BlogResearcher()
        category = "DevOps"
        research_data = researcher.analyze_trends(category)
        logger.info(f"✓ Research complete: {len(research_data.get('authoritative_sources', []))} sources found")
        
        # Step 2: Write
        logger.info("\n[2/3] Starting Writing Phase...")
        writer = BlogWriter()
        draft = writer.generate_blog(category, research_data)
        
        # Parse the draft to extract metadata
        logger.info(f"✓ Draft generated: {len(draft)} characters")
        logger.info(f"Preview: {draft[:200]}...")
        
        # Extract title from draft (first line after # or ##)
        import re
        title_match = re.search(r'#+\s*(.+)', draft)
        title = title_match.group(1).strip() if title_match else f"Latest Insights in {category}"
        
        # Step 3: Publish (NO CRITIC)
        logger.info("\n[3/3] Publishing directly (skipping critic)...")
        publisher = BlogPublisher()
        
        # Create blog object
        blog = {
            "title": title,
            "content": draft,
            "category": category,
            "tags": [category.lower(), "technology", "devops", "automation"]
        }
        
        url = publisher.publish(blog)
        
        logger.info("=" * 60)
        logger.info("✅ BLOG PUBLISHED SUCCESSFULLY!")
        logger.info("=" * 60)
        logger.info(f"Title: {title}")
        logger.info(f"Category: {category}")
        logger.info(f"URL: {url}")
        logger.info(f"Length: {len(draft)} characters")
        
        # Verify file was created
        import os
        blog_dir = "/app/backend/generated_blogs"
        files = os.listdir(blog_dir)
        logger.info(f"\nGenerated blogs directory: {len(files)} file(s)")
        for f in files:
            logger.info(f"  - {f}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ FAILED: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
