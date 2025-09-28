"""
Serper API Usage Dashboard

This script provides a simple dashboard to monitor Serper.dev API usage
and help manage your credit consumption.
"""

import os
import json
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
from search_utils import search_cache, rate_limiter

# Load environment variables
load_dotenv()

def format_number(num):
    """Format a number with commas for thousands"""
    return f"{num:,}"

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def display_dashboard():
    """Display the Serper API usage dashboard"""
    clear_screen()
    
    # Get current time
    now = datetime.now()
    
    # Header
    print("\n" + "=" * 60)
    print(" SERPER.DEV API USAGE DASHBOARD ".center(60, "="))
    print("=" * 60)
    
    # Credits information
    serper_api_key = os.getenv("SERPER_API_KEY", "Not configured")
    api_key_preview = serper_api_key[:8] + "..." + serper_api_key[-4:] if len(serper_api_key) > 12 else "Not configured"
    
    print(f"\nAPI Key: {api_key_preview}")
    print(f"Total Credits: 2,500 (Free Tier)")
    
    # Rate limiting info
    remaining_requests = rate_limiter.get_remaining()
    print(f"\nRate Limit Status:")
    print(f"  Remaining Requests: {remaining_requests}/100 per hour")
    
    if remaining_requests < 100:
        time_until_reset = rate_limiter.time_until_reset()
        reset_time = now + timedelta(seconds=time_until_reset)
        print(f"  Next Reset: {time_until_reset:.1f} seconds ({reset_time.strftime('%H:%M:%S')})")
    
    # Cache statistics
    cache_stats = search_cache.get_stats()
    print(f"\nCache Statistics:")
    print(f"  Cache Hits: {cache_stats['hits']}")
    print(f"  Cache Misses: {cache_stats['misses']}")
    print(f"  Hit Rate: {cache_stats['hit_rate']}")
    
    # Calculate credit savings
    credits_saved = cache_stats['hits']
    print(f"\nEstimated Credits Saved: {format_number(credits_saved)}")
    
    # Get cache files count and size
    cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")
    cache_files = [f for f in os.listdir(cache_dir) if f.endswith('.json')]
    cache_size_bytes = sum(os.path.getsize(os.path.join(cache_dir, f)) for f in cache_files)
    cache_size_kb = cache_size_bytes / 1024
    
    print(f"\nCache Information:")
    print(f"  Cached Queries: {len(cache_files)}")
    print(f"  Cache Size: {cache_size_kb:.2f} KB")
    
    # Tips to save credits
    print("\nTips to Save Credits:")
    print("  1. Use specific search queries instead of general ones")
    print("  2. Implement weekly blog generation instead of daily")
    print("  3. Clear cache only when necessary (older than 24 hours)")
    print("  4. Group related searches together")
    
    print("\n" + "=" * 60)
    print(f"Last Updated: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

if __name__ == "__main__":
    display_dashboard()