#!/usr/bin/env python3
"""
Auto-Blogger Diagnostic Test
Tests each component individually to identify where the pipeline is failing.
"""
import sys
import logging
import json
sys.path.insert(0, "/app")

# Configure verbose logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - [%(levelname)s] - %(message)s"
)
logger = logging.getLogger(__name__)

def test_researcher():
    """Test the researcher module"""
    logger.info("=" * 60)
    logger.info("TEST 1: BlogResearcher")
    logger.info("=" * 60)
    try:
        from backend.auto_blogger.researcher import BlogResearcher
        researcher = BlogResearcher()
        
        logger.info("Analyzing trends for DevOps...")
        research_data = researcher.analyze_trends("DevOps")
        
        logger.info(f"✅ Research SUCCESS!")
        logger.info(f"Found {len(research_data.get('authoritative_sources', []))} sources")
        logger.info(f"Headlines: {research_data.get('headlines', [])[0:2]}")
        return research_data
    except Exception as e:
        logger.error(f"❌ Research FAILED: {e}", exc_info=True)
        return None

def test_writer(research_data):
    """Test the writer module"""
    logger.info("=" * 60)
    logger.info("TEST 2: BlogWriter")
    logger.info("=" * 60)
    try:
        from backend.auto_blogger.writer import BlogWriter
        writer = BlogWriter()
        
        logger.info("Generating blog draft for DevOps...")
        draft = writer.generate_blog("DevOps", research_data)
        
        logger.info(f"✅ Writer SUCCESS!")
        logger.info(f"Draft length: {len(draft)} characters")
        logger.info(f"First 200 chars: {draft[:200]}")
        return draft
    except Exception as e:
        logger.error(f"❌ Writer FAILED: {e}", exc_info=True)
        return None

def test_critic(draft):
    """Test the critic module"""
    logger.info("=" * 60)
    logger.info("TEST 3: BlogCritic")
    logger.info("=" * 60)
    try:
        from backend.auto_blogger.critic import BlogCritic
        critic = BlogCritic()
        
        logger.info("Evaluating draft quality...")
        passed, review_json = critic.evaluate(draft, "DevOps")
        
        review = json.loads(review_json)
        logger.info(f"✅ Critic SUCCESS!")
        logger.info(f"Verdict: {'PASS' if passed else 'FAIL'}")
        logger.info(f"Score: {review.get('score', 'N/A')}")
        logger.info(f"Strengths: {review.get('strengths', [])}")
        return passed, review_json
    except Exception as e:
        logger.error(f"❌ Critic FAILED: {e}", exc_info=True)
        return False, "{}"

def test_publisher(draft):
    """Test the publisher module"""
    logger.info("=" * 60)
    logger.info("TEST 4: BlogPublisher")
    logger.info("=" * 60)
    try:
        from backend.auto_blogger.publisher import BlogPublisher
        publisher = BlogPublisher()
        
        # Create a minimal blog dict for testing
        test_blog = {
            "title": "Test Blog Post",
            "content": draft[:1000],  # Use first 1000 chars
            "category": "DevOps",
            "tags": ["test", "devops"]
        }
        
        logger.info("Publishing test blog...")
        url = publisher.publish(test_blog)
        
        logger.info(f"✅ Publisher SUCCESS!")
        logger.info(f"Published URL: {url}")
        return url
    except Exception as e:
        logger.error(f"❌ Publisher FAILED: {e}", exc_info=True)
        return None

def main():
    logger.info("\n" + "=" * 60)
    logger.info("AUTO-BLOGGER DIAGNOSTIC TEST SUITE")
    logger.info("=" * 60 + "\n")
    
    # Test 1: Researcher
    research_data = test_researcher()
    if not research_data:
        logger.error("❌ DIAGNOSTIC FAILED: Researcher module failed")
        return
    
    # Test 2: Writer
    draft = test_writer(research_data)
    if not draft:
        logger.error("❌ DIAGNOSTIC FAILED: Writer module failed")
        return
    
    # Test 3: Critic
    passed, review = test_critic(draft)
    logger.info(f"Critic evaluation: {'PASSED' if passed else 'FAILED'}")
    
    # Test 4: Publisher
    url = test_publisher(draft)
    if not url:
        logger.error("❌ DIAGNOSTIC FAILED: Publisher module failed")
        return
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ ALL TESTS PASSED!")
    logger.info("=" * 60)
    logger.info(f"Published blog at: {url}")

if __name__ == "__main__":
    main()
