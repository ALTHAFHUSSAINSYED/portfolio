"""
Test script for WebSearchEngine class
"""
import os
import sys
import logging
from dotenv import load_dotenv
from pprint import pprint

# Add the current directory to the path to import from the agent_service module
sys.path.append(os.getcwd())
import agent_service

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_web_search_engine():
    """Test WebSearchEngine class functionality"""
    print("Creating WebSearchEngine instance...")
    search_engine = agent_service.WebSearchEngine()
    
    # Test RSS news functionality
    print("\n===== Testing News from RSS Feeds =====")
    try:
        print("Fetching technology news from RSS feeds...")
        tech_news = search_engine._get_news_from_rss("technology")
        print(f"Found {len(tech_news)} technology news articles")
        
        if tech_news:
            print("\nFirst article:")
            pprint(tech_news[0])
            
            if len(tech_news) > 1:
                print("\nSecond article:")
                pprint(tech_news[1])
    except Exception as e:
        print(f"Error testing RSS news functionality: {e}")
    
    # Test the full get_latest_news method
    print("\n===== Testing get_latest_news Method =====")
    try:
        print("Fetching latest technology news...")
        latest_news = search_engine.get_latest_news("technology")
        print(f"Found {len(latest_news)} latest news articles")
        
        if latest_news:
            print("\nFirst article:")
            pprint(latest_news[0])
    except Exception as e:
        print(f"Error testing get_latest_news method: {e}")
    
    # Test web search functionality
    print("\n===== Testing Web Search Functionality =====")
    try:
        print("Searching the web for 'Python programming trends'...")
        search_results = search_engine.search_web("Python programming trends", max_results=3)
        print(f"Found {len(search_results)} search results")
        
        if search_results:
            print("\nFirst result:")
            pprint(search_results[0])
    except Exception as e:
        print(f"Error testing web search functionality: {e}")

if __name__ == "__main__":
    test_web_search_engine()