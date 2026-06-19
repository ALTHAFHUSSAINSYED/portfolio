"""
ChromaDB Migration Monitoring & Alerting System
Monitors ChromaDB operations during migration and sends notifications for critical failures.
"""

import logging
import os
from datetime import datetime
from typing import Dict, Optional
from enum import Enum

# Import notification service
try:
    from backend.notification_service import notification_service
except ImportError:
    notification_service = None
    logging.warning("notification_service not available - email alerts disabled")

logger = logging.getLogger('ChromaDBMonitor')


class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ChromaDBMonitor:
    """Monitor ChromaDB operations and send alerts for failures"""
    
    def __init__(self):
        self.error_count = 0
        self.warning_count = 0
        self.alert_threshold = 5  # Send alert after 5 errors
        self.last_alert_time = None
        self.alert_cooldown = 300  # 5 minutes between alerts
    
    def log_operation(self, operation: str, success: bool, details: Optional[Dict] = None):
        """
        Log ChromaDB operation and trigger alerts if needed.
        
        Args:
            operation: Operation name (e.g., "query", "add", "get_collection")
            success: Whether operation succeeded
            details: Additional context (collection name, error message, etc.)
        """
        timestamp = datetime.now().isoformat()
        details = details or {}
        
        if success:
            logger.info(f"✅ ChromaDB {operation} succeeded | {details}")
        else:
            self.error_count += 1
            logger.error(f"❌ ChromaDB {operation} failed | {details}")
            
            # Send alert if threshold reached
            if self.error_count >= self.alert_threshold:
                self._send_alert(
                    level=AlertLevel.CRITICAL,
                    operation=operation,
                    details=details
                )
    
    def log_collection_not_found(self, collection_name: str, context: str):
        """Log collection not found error (common during migration)"""
        self.warning_count += 1
        logger.warning(
            f"⚠️ ChromaDB collection '{collection_name}' not found | "
            f"Context: {context} | "
            f"This may be expected during migration"
        )
        
        # Send warning alert if too many
        if self.warning_count >= 10:
            self._send_alert(
                level=AlertLevel.WARNING,
                operation="collection_not_found",
                details={
                    "collection": collection_name,
                    "context": context,
                    "count": self.warning_count
                }
            )
    
    def log_query_failure(self, collection_name: str, error: str, query_type: str):
        """Log query failure with context"""
        self.error_count += 1
        logger.error(
            f"❌ ChromaDB query failed | "
            f"Collection: {collection_name} | "
            f"Query type: {query_type} | "
            f"Error: {error}"
        )
        
        self._send_alert(
            level=AlertLevel.ERROR,
            operation="query_failure",
            details={
                "collection": collection_name,
                "query_type": query_type,
                "error": error
            }
        )
    
    def log_publish_failure(self, blog_id: str, collection_name: str, error: str):
        """Log auto-blogger publish failure"""
        self.error_count += 1
        logger.error(
            f"❌ Blog publish failed | "
            f"Blog ID: {blog_id} | "
            f"Collection: {collection_name} | "
            f"Error: {error}"
        )
        
        self._send_alert(
            level=AlertLevel.CRITICAL,
            operation="blog_publish_failure",
            details={
                "blog_id": blog_id,
                "collection": collection_name,
                "error": error
            }
        )
    
    def log_migration_event(self, event_type: str, details: Dict):
        """Log migration-specific events (rollback, cutover, etc.)"""
        logger.info(f"🔄 Migration Event: {event_type} | {details}")
        
        # Send info alert for major migration events
        if event_type in ["rollback_triggered", "cutover_completed", "legacy_deleted"]:
            self._send_alert(
                level=AlertLevel.INFO,
                operation=event_type,
                details=details
            )
    
    def _send_alert(self, level: AlertLevel, operation: str, details: Dict):
        """
        Send alert via email notification service.
        Respects cooldown period to avoid spam.
        """
        now = datetime.now()
        
        # Check cooldown
        if self.last_alert_time:
            elapsed = (now - self.last_alert_time).total_seconds()
            if elapsed < self.alert_cooldown:
                logger.debug(f"Alert cooldown active ({int(elapsed)}s / {self.alert_cooldown}s)")
                return
        
        # Format alert message
        subject = f"[{level.value}] ChromaDB Alert: {operation}"
        message = self._format_alert_message(level, operation, details)
        
        # Send via notification service
        if notification_service:
            try:
                # Use the existing send_blog_notification method
                # (We'll adapt it for general alerts)
                success = notification_service.send_notification(
                    subject=subject,
                    message=message
                )
                
                if success:
                    logger.info(f"📧 Alert sent: {subject}")
                    self.last_alert_time = now
                else:
                    logger.warning(f"Failed to send alert: {subject}")
            except Exception as e:
                logger.error(f"Error sending alert: {e}")
        else:
            logger.warning(f"Alert NOT sent (notification_service unavailable): {subject}")
    
    def _format_alert_message(self, level: AlertLevel, operation: str, details: Dict) -> str:
        """Format alert message for email"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        message = f"""
ChromaDB Migration Alert

Severity: {level.value}
Operation: {operation}
Timestamp: {timestamp}

Details:
{self._format_details(details)}

Error Statistics:
- Total Errors: {self.error_count}
- Total Warnings: {self.warning_count}

Action Required:
{self._get_action_recommendation(level, operation)}

---
Automated alert from Portfolio Backend
EC2 Instance: Check /home/ec2-user/portfolio-logs for detailed logs
"""
        return message
    
    def _format_details(self, details: Dict) -> str:
        """Format details dict as readable string"""
        lines = []
        for key, value in details.items():
            lines.append(f"  - {key}: {value}")
        return "\n".join(lines) if lines else "  No additional details"
    
    def _get_action_recommendation(self, level: AlertLevel, operation: str) -> str:
        """Provide action recommendations based on alert"""
        if level == AlertLevel.CRITICAL:
            if "publish" in operation:
                return (
                    "1. Check auto-blogger logs: /home/ec2-user/portfolio-logs/auto_blogger/\n"
                    "2. Verify ChromaDB connection and credentials\n"
                    "3. Consider triggering rollback if errors persist"
                )
            return (
                "1. SSH to EC2 and check Docker logs: docker logs portfolio-backend\n"
                "2. Check ChromaDB Cloud status: https://app.trychroma.com\n"
                "3. Consider rollback: export USE_LEGACY_COLLECTIONS=true && docker restart portfolio-backend"
            )
        elif level == AlertLevel.ERROR:
            return (
                "1. Monitor error frequency\n"
                "2. Check application logs for patterns\n"
                "3. If errors continue, investigate ChromaDB configuration"
            )
        elif level == AlertLevel.WARNING:
            return (
                "1. Monitor warning frequency\n"
                "2. Expected during migration transition period\n"
                "3. No immediate action required unless count increases rapidly"
            )
        else:
            return "No action required - informational alert only"
    
    def reset_counters(self):
        """Reset error/warning counters (call after successful operations)"""
        self.error_count = 0
        self.warning_count = 0
        logger.info("📊 Monitoring counters reset")
    
    def get_stats(self) -> Dict:
        """Get current monitoring statistics"""
        return {
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "last_alert_time": self.last_alert_time.isoformat() if self.last_alert_time else None
        }


# Global monitor instance
chromadb_monitor = ChromaDBMonitor()
