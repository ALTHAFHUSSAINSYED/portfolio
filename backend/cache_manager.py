"""
In-Memory Response Cache for Chatbot
Provides fast LRU caching to reduce API calls and improve latency
"""
import hashlib
import time
from functools import lru_cache
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


class ResponseCache:
    """In-memory cache for chatbot responses with LRU eviction"""
    
    def __init__(self, max_size: int = 100, ttl_seconds: int = 3600):
        """
        Initialize cache
        
        Args:
            max_size: Maximum number of cached responses
            ttl_seconds: Time-to-live for cached responses (default 1 hour)
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, tuple] = {}  # {key: (response, timestamp)}
        logger.info(f"Initialized ResponseCache with max_size={max_size}, ttl={ttl_seconds}s")
    
    def _generate_cache_key(self, query: str, history: list = None) -> str:
        """
        Generate cache key from query and conversation history
        
        Args:
            query: User query
            history: Last 5 conversation messages
            
        Returns:
            Cache key hash
        """
        # Include last 5 messages for context-aware caching
        history_str = ""
        if history:
            history_str = str(history[-5:])
        
        key_string = f"{query}|{history_str}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, query: str, history: list = None) -> Optional[str]:
        """
        Retrieve cached response if available and not expired
        
        Args:
            query: User query
            history: Conversation history
            
        Returns:
            Cached response or None
        """
        cache_key = self._generate_cache_key(query, history)
        
        if cache_key in self.cache:
            response, timestamp = self.cache[cache_key]
            
            # Check if expired
            if time.time() - timestamp > self.ttl_seconds:
                del self.cache[cache_key]
                logger.debug(f"Cache expired for key: {cache_key[:8]}...")
                return None
            
            logger.info(f"Cache HIT for key: {cache_key[:8]}...")
            return response
        
        logger.debug(f"Cache MISS for key: {cache_key[:8]}...")
        return None
    
    def set(self, query: str, response: str, history: list = None):
        """
        Store response in cache with LRU eviction
        
        Args:
            query: User query
            response: Bot response to cache
            history: Conversation history
        """
        cache_key = self._generate_cache_key(query, history)
        
        # LRU eviction if at capacity
        if len(self.cache) >= self.max_size:
            # Remove oldest entry
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k][1])
            del self.cache[oldest_key]
            logger.debug(f"Cache evicted oldest entry: {oldest_key[:8]}...")
        
        self.cache[cache_key] = (response, time.time())
        logger.info(f"Cache SET for key: {cache_key[:8]}... (size: {len(self.cache)}/{self.max_size})")
    
    def clear(self):
        """Clear all cached responses"""
        self.cache.clear()
        logger.info("Cache cleared")
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "ttl_seconds": self.ttl_seconds
        }
