"""
Rate Limiter for Chatbot API Calls
Prevents quota exhaustion with configurable RPM limits
"""
import time
from collections import deque
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """Sliding window rate limiter for API requests"""
    
    def __init__(self, max_requests_per_minute: int = 20):
        """
        Initialize rate limiter
        
        Args:
            max_requests_per_minute: Maximum requests allowed per minute
        """
        self.max_rpm = max_requests_per_minute
        self.request_times = deque()  # Timestamps of recent requests
        logger.info(f"Initialized RateLimiter with max_rpm={max_requests_per_minute}")
    
    def _cleanup_old_requests(self):
        """Remove request timestamps older than 1 minute"""
        current_time = time.time()
        cutoff_time = current_time - 60  # 60 seconds = 1 minute
        
        while self.request_times and self.request_times[0] < cutoff_time:
            self.request_times.popleft()
    
    def check_limit(self) -> bool:
        """
        Check if request is within rate limit
        
        Returns:
            True if request is allowed, False if rate limited
        """
        self._cleanup_old_requests()
        
        if len(self.request_times) >= self.max_rpm:
            logger.warning(f"Rate limit exceeded: {len(self.request_times)}/{self.max_rpm} RPM")
            return False
        
        return True
    
    def record_request(self):
        """Record a new request timestamp"""
        self._cleanup_old_requests()
        self.request_times.append(time.time())
        logger.debug(f"Request recorded: {len(self.request_times)}/{self.max_rpm} RPM")
    
    def get_wait_time(self) -> float:
        """
        Calculate seconds to wait before next request is allowed
        
        Returns:
            Seconds to wait (0 if no wait needed)
        """
        self._cleanup_old_requests()
        
        if len(self.request_times) < self.max_rpm:
            return 0.0
        
        # Wait until oldest request expires
        oldest_request = self.request_times[0]
        wait_time = max(0, 60 - (time.time() - oldest_request))
        
        logger.info(f"Rate limited. Wait time: {wait_time:.1f}s")
        return wait_time
    
    def get_stats(self) -> dict:
        """Get rate limiter statistics"""
        self._cleanup_old_requests()
        return {
            "current_rpm": len(self.request_times),
            "max_rpm": self.max_rpm,
            "requests_available": max(0, self.max_rpm - len(self.request_times))
        }
