"""
Rate Limiter for Chatbot API Calls
Prevents quota exhaustion with configurable per-session RPM limits
"""
import time
from collections import deque, defaultdict
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """Per-session sliding window rate limiter for API requests"""
    
    def __init__(self, max_requests_per_minute: int = 12):
        """
        Initialize per-session rate limiter
        
        Args:
            max_requests_per_minute: Maximum requests allowed per minute per session (default: 12)
        """
        self.max_rpm = max_requests_per_minute
        self.session_request_times: Dict[str, deque] = defaultdict(deque)  # {session_id: deque([timestamps])}
        self.last_cleanup_time = time.time()
        logger.info(f"Initialized per-session RateLimiter with max_rpm={max_requests_per_minute}")
    
    def _cleanup_old_requests(self, session_id: str):
        """Remove request timestamps older than 1 minute for a specific session"""
        current_time = time.time()
        cutoff_time = current_time - 60  # 60 seconds = 1 minute
        
        session_times = self.session_request_times[session_id]
        while session_times and session_times[0] < cutoff_time:
            session_times.popleft()
        
        # Remove empty session entries (memory optimization)
        if not session_times:
            del self.session_request_times[session_id]
    
    def _cleanup_inactive_sessions(self):
        """Remove sessions with no requests in the last 5 minutes (memory optimization)"""
        current_time = time.time()
        
        # Run cleanup every 5 minutes
        if current_time - self.last_cleanup_time < 300:
            return
        
        self.last_cleanup_time = current_time
        cutoff_time = current_time - 300  # 5 minutes
        
        inactive_sessions = [
            session_id for session_id, times in self.session_request_times.items()
            if not times or times[-1] < cutoff_time
        ]
        
        for session_id in inactive_sessions:
            del self.session_request_times[session_id]
        
        if inactive_sessions:
            logger.info(f"Cleaned up {len(inactive_sessions)} inactive sessions")
    
    def check_limit(self, session_id: str = 'default') -> bool:
        """
        Check if request is within rate limit for a specific session
        
        Args:
            session_id: Unique session identifier (per user/browser session)
        
        Returns:
            True if request is allowed, False if rate limited
        """
        self._cleanup_old_requests(session_id)
        self._cleanup_inactive_sessions()
        
        session_times = self.session_request_times[session_id]
        
        if len(session_times) >= self.max_rpm:
            logger.warning(f"Rate limit exceeded for session {session_id}: {len(session_times)}/{self.max_rpm} RPM")
            return False
        
        return True
    
    def record_request(self, session_id: str = 'default'):
        """
        Record a new request timestamp for a specific session
        
        Args:
            session_id: Unique session identifier
        """
        self._cleanup_old_requests(session_id)
        self.session_request_times[session_id].append(time.time())
        logger.debug(f"Request recorded for session {session_id}: {len(self.session_request_times[session_id])}/{self.max_rpm} RPM")
    
    def get_wait_time(self, session_id: str = 'default') -> float:
        """
        Calculate seconds to wait before next request is allowed for a specific session
        
        Args:
            session_id: Unique session identifier
        
        Returns:
            Seconds to wait (0 if no wait needed)
        """
        self._cleanup_old_requests(session_id)
        
        session_times = self.session_request_times[session_id]
        
        if len(session_times) < self.max_rpm:
            return 0.0
        
        # Wait until oldest request expires
        oldest_request = session_times[0]
        wait_time = max(0, 60 - (time.time() - oldest_request))
        
        logger.info(f"Session {session_id} rate limited. Wait time: {wait_time:.1f}s")
        return wait_time
    
    def get_stats(self, session_id: str = 'default') -> dict:
        """
        Get rate limiter statistics for a specific session
        
        Args:
            session_id: Unique session identifier
        
        Returns:
            Dictionary with session statistics
        """
        self._cleanup_old_requests(session_id)
        
        session_times = self.session_request_times[session_id]
        
        return {
            "session_id": session_id,
            "current_rpm": len(session_times),
            "max_rpm": self.max_rpm,
            "requests_available": max(0, self.max_rpm - len(session_times)),
            "active_sessions": len(self.session_request_times)
        }
    
    def get_global_stats(self) -> dict:
        """
        Get global rate limiter statistics across all sessions
        
        Returns:
            Dictionary with global statistics
        """
        self._cleanup_inactive_sessions()
        
        total_requests = sum(len(times) for times in self.session_request_times.values())
        
        return {
            "active_sessions": len(self.session_request_times),
            "total_current_rpm": total_requests,
            "max_rpm_per_session": self.max_rpm,
            "estimated_total_capacity": self.max_rpm * len(self.session_request_times) if self.session_request_times else self.max_rpm
        }
