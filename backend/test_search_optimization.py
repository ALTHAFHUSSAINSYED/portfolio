"""
Test script for credit-saving search utilities
"""

import os
import time
from dotenv import load_dotenv
from search_utils import search_cache, rate_limiter, query_optimizer
from agent_service import WebSearchEngine

# Load environment variables
load_dotenv()

def test_search_optimization():
    """Test the search optimization features"""
    print("\n=== Testing Search Optimization Features ===\n")
    
    # Initialize the web search engine
    search_engine = WebSearchEngine()
    
    # Test with a sample query
    original_query = "modern web development trends 2025"
    optimized_query = query_optimizer.optimize_query(original_query)
    
    print(f"Original query: {original_query}")
    print(f"Optimized query: {optimized_query}")
    print()
    
    # First search - Should call the API
    print("First search (API call expected):")
    results1 = search_engine.search_web(original_query, max_results=3)
    print(f"Found {len(results1)} results")
    print(f"First result: {results1[0]['title'][:50]}...")
    print()
    
    # Second search with same query - Should use cache
    print("Second search with same query (should use cache):")
    results2 = search_engine.search_web(original_query, max_results=3)
    print(f"Found {len(results2)} results")
    print(f"First result: {results2[0]['title'][:50]}...")
    print()
    
    # Display cache statistics
    stats = search_cache.get_stats()
    print("Cache statistics:")
    print(f"Hits: {stats['hits']}")
    print(f"Misses: {stats['misses']}")
    print(f"Hit rate: {stats['hit_rate']}")
    print()
    
    # Display rate limiter statistics
    remaining = rate_limiter.get_remaining()
    print("Rate limiter statistics:")
    print(f"Remaining requests in window: {remaining}")
    print()
    
    # Test query optimization with different queries
    test_queries = [
        "how to create a react application",
        "best javascript frameworks",
        "latest AI developments in 2025",
        "python for data science tutorial",
        "the future of mobile app development"
    ]
    
    print("Query optimization examples:")
    for query in test_queries:
        optimized = query_optimizer.optimize_query(query)
        print(f"Original: {query}")
        print(f"Optimized: {optimized}")
        print()

if __name__ == "__main__":
    test_search_optimization()