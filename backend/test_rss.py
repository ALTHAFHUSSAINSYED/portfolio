"""
Test script for RSS feed parsing functionality
"""
import os
import sys
import logging
import feedparser

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_rss_feeds():
    """Test RSS feed parsing functionality"""
    tech_rss_feeds = [
        "https://feeds.feedburner.com/TechCrunch",
        "https://www.wired.com/feed/rss",
        "https://www.theverge.com/rss/index.xml",
        "https://feeds.feedburner.com/venturebeat/SZYF",
        "https://www.cnet.com/rss/all/"
    ]
    
    print("Testing RSS feed parsing functionality...")
    
    for feed_url in tech_rss_feeds:
        try:
            print(f"\nFetching feed from {feed_url}...")
            feed = feedparser.parse(feed_url)
            
            if feed.bozo:
                print(f"Warning: Feed has errors: {feed.bozo_exception}")
            
            print(f"Feed title: {feed.feed.get('title', 'No title')}")
            print(f"Number of entries: {len(feed.entries)}")
            
            if feed.entries:
                print("\nLatest entry:")
                entry = feed.entries[0]
                print(f"Title: {entry.get('title', 'No title')}")
                print(f"Link: {entry.get('link', 'No link')}")
                print(f"Published: {entry.get('published', 'No date')}")
                
                # Print summary (truncated)
                summary = entry.get('summary', 'No summary')
                if len(summary) > 100:
                    summary = summary[:100] + "..."
                print(f"Summary: {summary}")
            else:
                print("No entries found in feed")
                
        except Exception as e:
            print(f"Error fetching feed {feed_url}: {e}")

if __name__ == "__main__":
    test_rss_feeds()