"""
Search Utilities for Portfolio Project

This module provides utilities for optimizing search operations and managing API usage,
particularly for Serper.dev API calls to save credits.
"""

import os
import json
import time
import hashlib
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("search_utils")

class SearchCache:
    """Cache for storing search results to minimize API calls"""
    
    def __init__(self, cache_dir="cache", max_age_hours=24):
        """
        Initialize the search cache
        
        Args:
            cache_dir (str): Directory to store cache files
            max_age_hours (int): Maximum age of cache entries in hours
        """
        self.cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), cache_dir)
        self.max_age = timedelta(hours=max_age_hours)
        
        # Create cache directory if it doesn't exist
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            
        # Track cache hits/misses for reporting
        self.hits = 0
        self.misses = 0
    
    def _get_cache_key(self, query, params=None):
        """Generate a unique cache key for a search query"""
        # Combine query with parameters for uniqueness
        if params:
            query_string = f"{query}_{json.dumps(params, sort_keys=True)}"
        else:
            query_string = query
            
        # Hash the query string to create a filename-safe key
        return hashlib.md5(query_string.encode()).hexdigest()
    
    def _get_cache_path(self, key):
        """Get the file path for a cache key"""
        return os.path.join(self.cache_dir, f"{key}.json")
    
    def get(self, query, params=None):
        """
        Get cached search results if available and not expired
        
        Args:
            query (str): The search query
            params (dict): Additional search parameters
            
        Returns:
            dict: Cached search results or None if not available
        """
        key = self._get_cache_key(query, params)
        cache_path = self._get_cache_path(key)
        
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r') as file:
                    data = json.load(file)
                
                # Check if cache is still valid
                cache_time = datetime.fromisoformat(data['timestamp'])
                if datetime.now() - cache_time < self.max_age:
                    logger.debug(f"Cache hit for query: {query}")
                    self.hits += 1
                    return data['results']
                else:
                    logger.debug(f"Cache expired for query: {query}")
                    # Cache expired, count as a miss
                    self.misses += 1
            except Exception as e:
                logger.error(f"Error reading cache: {e}")
        
        # Cache miss
        self.misses += 1
        return None
    
    def set(self, query, results, params=None):
        """
        Store search results in cache
        
        Args:
            query (str): The search query
            results (dict): The search results to cache
            params (dict): Additional search parameters
        """
        key = self._get_cache_key(query, params)
        cache_path = self._get_cache_path(key)
        
        try:
            # Store results with timestamp
            cache_data = {
                'query': query,
                'params': params,
                'timestamp': datetime.now().isoformat(),
                'results': results
            }
            
            with open(cache_path, 'w') as file:
                json.dump(cache_data, file)
                
            logger.debug(f"Cached results for query: {query}")
        except Exception as e:
            logger.error(f"Error writing to cache: {e}")
    
    def get_stats(self):
        """Get cache statistics"""
        total = self.hits + self.misses
        hit_rate = (self.hits / total) * 100 if total > 0 else 0
        
        return {
            'hits': self.hits,
            'misses': self.misses,
            'total': total,
            'hit_rate': f"{hit_rate:.1f}%"
        }
    
    def clear_expired(self):
        """Remove expired cache entries"""
        count = 0
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(self.cache_dir, filename)
                try:
                    with open(file_path, 'r') as file:
                        data = json.load(file)
                    
                    # Check if cache is expired
                    cache_time = datetime.fromisoformat(data['timestamp'])
                    if datetime.now() - cache_time > self.max_age:
                        os.remove(file_path)
                        count += 1
                except Exception as e:
                    logger.error(f"Error clearing expired cache: {e}")
        
        return count


class RateLimiter:
    """
    Rate limiter to control API usage
    """
    
    def __init__(self, max_requests=100, time_window=3600):
        """
        Initialize rate limiter
        
        Args:
            max_requests (int): Maximum number of requests allowed in the time window
            time_window (int): Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.request_timestamps = []
    
    def check_limit(self):
        """
        Check if the rate limit has been reached
        
        Returns:
            bool: True if under limit, False if limit reached
        """
        # Remove timestamps outside the current time window
        current_time = time.time()
        self.request_timestamps = [t for t in self.request_timestamps 
                                 if current_time - t <= self.time_window]
        
        # Check if we're still under the limit
        return len(self.request_timestamps) < self.max_requests
    
    def add_request(self):
        """Record a new request"""
        self.request_timestamps.append(time.time())
    
    def get_remaining(self):
        """
        Get the number of remaining requests in the current time window
        
        Returns:
            int: Number of remaining requests
        """
        # Update the timestamps list first
        self.check_limit()
        return self.max_requests - len(self.request_timestamps)
    
    def time_until_reset(self):
        """
        Get the time until the oldest request ages out of the window
        
        Returns:
            float: Seconds until a new request is available, or 0 if under limit
        """
        if not self.request_timestamps or len(self.request_timestamps) < self.max_requests:
            return 0
        
        current_time = time.time()
        oldest_timestamp = min(self.request_timestamps)
        
        return max(0, self.time_window - (current_time - oldest_timestamp))


class QueryOptimizer:
    """
    Optimize search queries to get better results with fewer API calls
    """
    
    @staticmethod
    def optimize_query(query):
        """
        Optimize a search query for better results
        
        Args:
            query (str): The original query
            
        Returns:
            str: The optimized query
        """
        # Remove unnecessary words
        filler_words = ["the", "a", "an", "and", "or", "but", "for", "with", "about"]
        words = query.split()
        filtered_words = [word for word in words if word.lower() not in filler_words or len(words) <= 3]
        
        # Add quotes for exact phrases if it looks like a phrase
        optimized = " ".join(filtered_words)
        
        # Add qualifiers for better results
        if "how to" in query.lower() or "guide" in query.lower():
            optimized += " tutorial OR guide"
        
        if "trends" in query.lower() or "latest" in query.lower():
            optimized += " current OR recent OR 2025"
            
        # Ensure we don't overoptimize short queries
        if len(filtered_words) <= 3:
            return query
            
        return optimized


# Create global instances for use across the application
search_cache = SearchCache()
rate_limiter = RateLimiter(max_requests=100, time_window=3600)  # 100 requests per hour
query_optimizer = QueryOptimizer()