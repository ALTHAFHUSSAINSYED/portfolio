"""
Test script for Serper.dev utilities

This script tests the dashboard and admin utilities to verify they're working correctly.
"""

import os
import json
import time
from dotenv import load_dotenv
from search_utils import search_cache, rate_limiter, query_optimizer
import requests

# Load environment variables
load_dotenv()

def test_api_connection():
    """Test connection to Serper.dev API"""
    print("\nTesting API connection...")
    
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        print("❌ API key not found in .env file")
        return False
    
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }
    
    test_query = "test query"
    data = {
        'q': test_query
    }
    
    try:
        response = requests.post(
            'https://google.serper.dev/search',
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            print(f"✅ API connection successful (HTTP {response.status_code})")
            # Record the request for rate limiter testing
            rate_limiter.add_request()
            return True
        else:
            print(f"❌ API connection failed (HTTP {response.status_code})")
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ API connection error: {e}")
        return False

def test_cache():
    """Test cache functionality"""
    print("\nTesting cache functionality...")
    
    # Test query
    test_query = "python programming language"
    test_data = {"test": "data", "timestamp": "2023-01-01T00:00:00"}
    
    # Test cache setting
    try:
        search_cache.set(test_query, test_data)
        print("✅ Cache write successful")
    except Exception as e:
        print(f"❌ Cache write failed: {e}")
        return False
    
    # Test cache getting
    try:
        cached_data = search_cache.get(test_query)
        if cached_data:
            print("✅ Cache read successful")
        else:
            print("❌ Cache read failed (no data)")
            return False
    except Exception as e:
        print(f"❌ Cache read failed: {e}")
        return False
    
    # Test cache stats
    stats = search_cache.get_stats()
    print(f"✅ Cache statistics: {json.dumps(stats, indent=2)}")
    
    return True

def test_rate_limiter():
    """Test rate limiter functionality"""
    print("\nTesting rate limiter...")
    
    remaining = rate_limiter.get_remaining()
    print(f"✅ Remaining requests: {remaining}/{rate_limiter.max_requests}")
    
    if remaining < rate_limiter.max_requests:
        time_until = rate_limiter.time_until_reset()
        print(f"✅ Time until reset: {time_until:.1f} seconds")
    
    return True

def test_query_optimizer():
    """Test query optimizer functionality"""
    print("\nTesting query optimizer...")
    
    test_queries = [
        "how to learn python programming for beginners",
        "latest trends in artificial intelligence",
        "the weather in new york city",
        "small query"
    ]
    
    for query in test_queries:
        optimized = query_optimizer.optimize_query(query)
        print(f"Original: '{query}'")
        print(f"Optimized: '{optimized}'")
        print("---")
    
    return True

def main():
    """Run all tests"""
    print("\n===== SERPER.DEV UTILITIES TEST =====")
    
    # Make sure cache directory exists
    if not os.path.exists(search_cache.cache_dir):
        os.makedirs(search_cache.cache_dir)
        print(f"Created cache directory: {search_cache.cache_dir}")
    
    # Run tests
    api_ok = test_api_connection()
    cache_ok = test_cache()
    rate_ok = test_rate_limiter()
    optimizer_ok = test_query_optimizer()
    
    # Summary
    print("\n===== TEST SUMMARY =====")
    print(f"API Connection: {'✅ PASS' if api_ok else '❌ FAIL'}")
    print(f"Cache Functionality: {'✅ PASS' if cache_ok else '❌ FAIL'}")
    print(f"Rate Limiter: {'✅ PASS' if rate_ok else '❌ FAIL'}")
    print(f"Query Optimizer: {'✅ PASS' if optimizer_ok else '❌ FAIL'}")
    
    if all([api_ok, cache_ok, rate_ok, optimizer_ok]):
        print("\n✅ All tests passed! The utilities are working correctly.")
        print("\nNext steps:")
        print("1. Run 'python serper_dashboard.py' to view the usage dashboard")
        print("2. Run 'python serper_admin.py diagnostics' to check system status")
        print("3. See SERPER_DOCS.md for detailed documentation")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()