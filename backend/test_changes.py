"""
Test script to validate the removal of OpenAI and 
implementation of expanded topic categories
"""

import sys
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("TestScript")

def run_tests():
    """Run all tests to validate our changes"""
    logger.info("Starting tests...")
    
    # Test 1: Check for any remaining OpenAI imports
    logger.info("Test 1: Checking for OpenAI imports...")
    
    import importlib
    try:
        openai = importlib.import_module("openai")
        logger.error("❌ OpenAI module is still importable, may not be fully removed")
    except ImportError:
        logger.info("✅ OpenAI module not found - good!")
    
    # Test 2: Check that the expanded topics are available
    logger.info("Test 2: Checking expanded topics...")
    
    try:
        from agent_service import BlogGenerator
        blog_gen = BlogGenerator()
        
        # Attempt to access the topic categories
        # This will indirectly test if it_software_topics is properly defined
        blog = blog_gen.generate_blog()
        
        if blog and isinstance(blog, dict) and "title" in blog:
            logger.info(f"✅ Blog generation successful with title: {blog['title']}")
            if "category" in blog:
                logger.info(f"✅ Blog category assigned: {blog['category']}")
            else:
                logger.warning("⚠️ Blog generated but category not assigned")
        else:
            logger.error("❌ Blog generation failed")
    except Exception as e:
        logger.error(f"❌ Error testing blog generator: {e}")
    
    # Test 3: Check Google Gemini API status
    logger.info("Test 3: Checking Gemini API status...")
    
    try:
        from check_gemini_status import check_gemini_status
        check_gemini_status()
    except Exception as e:
        logger.error(f"❌ Error checking Gemini status: {e}")
    
    logger.info("All tests completed!")

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print(" PORTFOLIO CODEBASE TEST SCRIPT ".center(80, "="))
    print("=" * 80)
    print("\nThis script tests:")
    print("1. Complete removal of OpenAI dependencies")
    print("2. Implementation of expanded IT software topics")
    print("3. Google Gemini API status and quota\n")
    
    run_tests()
    
    print("\n" + "=" * 80)
    print(" TEST COMPLETE ".center(80, "="))
    print("=" * 80)