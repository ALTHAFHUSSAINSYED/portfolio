"""
ChromaDB Migration Monitoring & Alerting System

Purpose: Track ChromaDB operations, detect errors, and send alerts during migration
Created: January 2, 2026 (Task 16)
Status: Ready for deployment

Features:
- Collection operation tracking (queries, writes, deletes)
- Error detection and classification (CRITICAL/HIGH/MEDIUM/LOW)
- Alert aggregation with rate limiting
- Slack/Email notification support
- Metrics collection for analysis
"""

import logging
import time
import os
from typing import Dict, List, Optional, Literal
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
import json

# Configure logger
logger = logging.getLogger('ChromaDBMonitor')
logger.setLevel(logging.INFO)

# Severity levels
Severity = Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"]

@dataclass
class ChromaDBError:
    """Represents a ChromaDB operation error"""
    timestamp: float
    operation: str  # query, add, delete, get, etc.
    collection: str
    error_type: str  # CollectionNotFound, QueryFailed, AddFailed, etc.
    error_message: str
    severity: Severity
    context: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp,
            "timestamp_iso": datetime.fromtimestamp(self.timestamp).isoformat(),
            "operation": self.operation,
            "collection": self.collection,
            "error_type": self.error_type,
            "error_message": self.error_message,
            "severity": self.severity,
            "context": self.context
        }


@dataclass
class OperationMetrics:
    """Tracks success/failure metrics for ChromaDB operations"""
    success_count: int = 0
    failure_count: int = 0
    total_duration_ms: float = 0.0
    last_success_time: Optional[float] = None
    last_failure_time: Optional[float] = None
    
    @property
    def success_rate(self) -> float:
        total = self.success_count + self.failure_count
        return (self.success_count / total * 100) if total > 0 else 0.0
    
    @property
    def avg_duration_ms(self) -> float:
        total_ops = self.success_count + self.failure_count
        return (self.total_duration_ms / total_ops) if total_ops > 0 else 0.0
    
    def to_dict(self) -> Dict:
        return {
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "success_rate": round(self.success_rate, 2),
            "avg_duration_ms": round(self.avg_duration_ms, 2),
            "last_success_time": self.last_success_time,
            "last_failure_time": self.last_failure_time
        }


class ChromaDBMonitor:
    """
    Centralized monitoring system for ChromaDB operations
    
    Usage:
        monitor = ChromaDBMonitor()
        
        # Track operation
        with monitor.track_operation("query", "portfolio_master"):
            results = collection.query(...)
        
        # Log error
        monitor.log_error("query", "portfolio_master", "CollectionNotFound", 
                         "Collection portfolio_master does not exist", "CRITICAL")
        
        # Get metrics
        metrics = monitor.get_metrics()
    """
    
    def __init__(self, alert_threshold_minutes: int = 5):
        """
        Initialize monitor
        
        Args:
            alert_threshold_minutes: Minimum time between duplicate alerts
        """
        self.errors: List[ChromaDBError] = []
        self.metrics_by_collection: Dict[str, Dict[str, OperationMetrics]] = defaultdict(
            lambda: defaultdict(OperationMetrics)
        )
        self.alert_threshold_seconds = alert_threshold_minutes * 60
        self.last_alert_time: Dict[str, float] = {}
        
        # Load environment config
        self.enable_slack_alerts = os.getenv('ENABLE_SLACK_ALERTS', 'false').lower() == 'true'
        self.enable_email_alerts = os.getenv('ENABLE_EMAIL_ALERTS', 'false').lower() == 'true'
        self.slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL', '')
        self.alert_email = os.getenv('ALERT_EMAIL', os.getenv('TO_EMAIL', ''))
        
        logger.info("ChromaDBMonitor initialized")
        logger.info(f"Slack alerts: {'ENABLED' if self.enable_slack_alerts else 'DISABLED'}")
        logger.info(f"Email alerts: {'ENABLED' if self.enable_email_alerts else 'DISABLED'}")
    
    def log_error(self, operation: str, collection: str, error_type: str, 
                  error_message: str, severity: Severity, context: Optional[Dict] = None):
        """
        Log a ChromaDB error and send alerts if needed
        
        Args:
            operation: Type of operation (query, add, delete, etc.)
            collection: Collection name
            error_type: Error classification (CollectionNotFound, QueryFailed, etc.)
            error_message: Detailed error message
            severity: CRITICAL, HIGH, MEDIUM, or LOW
            context: Additional context (session_id, query, etc.)
        """
        error = ChromaDBError(
            timestamp=time.time(),
            operation=operation,
            collection=collection,
            error_type=error_type,
            error_message=error_message,
            severity=severity,
            context=context or {}
        )
        
        self.errors.append(error)
        
        # Log to standard logger
        log_msg = (f"ChromaDB Error [{severity}] - {operation} on {collection}: "
                   f"{error_type} - {error_message}")
        
        if severity == "CRITICAL":
            logger.critical(log_msg)
        elif severity == "HIGH":
            logger.error(log_msg)
        elif severity == "MEDIUM":
            logger.warning(log_msg)
        else:
            logger.info(log_msg)
        
        # Send alerts for CRITICAL and HIGH severity
        if severity in ["CRITICAL", "HIGH"]:
            self._send_alert(error)
        
        return error
    
    def track_success(self, operation: str, collection: str, duration_ms: float):
        """Track successful operation"""
        metrics = self.metrics_by_collection[collection][operation]
        metrics.success_count += 1
        metrics.total_duration_ms += duration_ms
        metrics.last_success_time = time.time()
        
        logger.debug(f"✅ {operation} on {collection} succeeded ({duration_ms:.2f}ms)")
    
    def track_failure(self, operation: str, collection: str, duration_ms: float):
        """Track failed operation"""
        metrics = self.metrics_by_collection[collection][operation]
        metrics.failure_count += 1
        metrics.total_duration_ms += duration_ms
        metrics.last_failure_time = time.time()
        
        logger.debug(f"❌ {operation} on {collection} failed ({duration_ms:.2f}ms)")
    
    def track_operation(self, operation: str, collection: str):
        """
        Context manager for tracking operation duration and success/failure
        
        Usage:
            with monitor.track_operation("query", "portfolio_master"):
                results = collection.query(...)
        """
        from contextlib import contextmanager
        
        @contextmanager
        def _track():
            start_time = time.time()
            try:
                yield
                duration_ms = (time.time() - start_time) * 1000
                self.track_success(operation, collection, duration_ms)
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                self.track_failure(operation, collection, duration_ms)
                raise
        
        return _track()
    
    def _send_alert(self, error: ChromaDBError):
        """Send alert via configured channels (Slack, Email)"""
        # Rate limiting: Don't send duplicate alerts too frequently
        alert_key = f"{error.collection}:{error.error_type}"
        now = time.time()
        
        if alert_key in self.last_alert_time:
            time_since_last = now - self.last_alert_time[alert_key]
            if time_since_last < self.alert_threshold_seconds:
                logger.debug(f"Alert suppressed (rate limit): {alert_key}")
                return
        
        self.last_alert_time[alert_key] = now
        
        # Send to Slack
        if self.enable_slack_alerts and self.slack_webhook_url:
            self._send_slack_alert(error)
        
        # Send to Email
        if self.enable_email_alerts and self.alert_email:
            self._send_email_alert(error)
    
    def _send_slack_alert(self, error: ChromaDBError):
        """Send alert to Slack webhook"""
        try:
            import requests
            
            # Color coding by severity
            color_map = {
                "CRITICAL": "#ff0000",  # Red
                "HIGH": "#ff9900",      # Orange
                "MEDIUM": "#ffcc00",    # Yellow
                "LOW": "#00ccff"        # Blue
            }
            
            # Format timestamp
            timestamp_str = datetime.fromtimestamp(error.timestamp).strftime("%Y-%m-%d %H:%M:%S UTC")
            
            payload = {
                "attachments": [{
                    "color": color_map.get(error.severity, "#cccccc"),
                    "title": f"🚨 ChromaDB Alert [{error.severity}]",
                    "text": f"*{error.error_type}* on collection `{error.collection}`",
                    "fields": [
                        {"title": "Operation", "value": error.operation, "short": True},
                        {"title": "Collection", "value": error.collection, "short": True},
                        {"title": "Error", "value": error.error_message, "short": False},
                        {"title": "Timestamp", "value": timestamp_str, "short": True},
                        {"title": "Severity", "value": error.severity, "short": True}
                    ],
                    "footer": "ChromaDB Migration Monitor",
                    "ts": int(error.timestamp)
                }]
            }
            
            response = requests.post(self.slack_webhook_url, json=payload, timeout=5)
            
            if response.status_code == 200:
                logger.info(f"✅ Slack alert sent: {error.error_type}")
            else:
                logger.warning(f"⚠️ Slack alert failed: {response.status_code}")
        
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")
    
    def _send_email_alert(self, error: ChromaDBError):
        """Send alert via email using notification_service"""
        try:
            from backend.notification_service import notification_service
            
            timestamp_str = datetime.fromtimestamp(error.timestamp).strftime("%Y-%m-%d %H:%M:%S UTC")
            
            subject = f"🚨 ChromaDB Alert [{error.severity}] - {error.error_type}"
            
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif;">
                <h2 style="color: {'#d32f2f' if error.severity == 'CRITICAL' else '#f57c00'};">
                    ChromaDB Migration Alert
                </h2>
                <table style="border-collapse: collapse; width: 100%;">
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Severity</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{error.severity}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Error Type</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{error.error_type}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Operation</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{error.operation}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Collection</td>
                        <td style="padding: 8px; border: 1px solid #ddd;"><code>{error.collection}</code></td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Timestamp</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{timestamp_str}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Error Message</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{error.error_message}</td>
                    </tr>
                </table>
                <p style="margin-top: 20px; color: #666;">
                    This is an automated alert from the ChromaDB Migration Monitor.
                </p>
            </body>
            </html>
            """
            
            # Send via existing notification service
            notification_service.send_email(
                to_email=self.alert_email,
                subject=subject,
                html_content=html_content
            )
            
            logger.info(f"✅ Email alert sent to {self.alert_email}")
        
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
    
    def get_metrics(self, collection: Optional[str] = None) -> Dict:
        """
        Get operation metrics
        
        Args:
            collection: Filter by specific collection (None = all collections)
        
        Returns:
            Dictionary with metrics per collection and operation
        """
        if collection:
            # Single collection metrics
            if collection in self.metrics_by_collection:
                return {
                    "collection": collection,
                    "operations": {
                        op: metrics.to_dict()
                        for op, metrics in self.metrics_by_collection[collection].items()
                    }
                }
            return {"collection": collection, "operations": {}}
        
        # All collections metrics
        return {
            coll: {
                op: metrics.to_dict()
                for op, metrics in ops.items()
            }
            for coll, ops in self.metrics_by_collection.items()
        }
    
    def get_error_summary(self, last_n_hours: int = 24) -> Dict:
        """
        Get summary of errors in the last N hours
        
        Args:
            last_n_hours: Time window for error summary
        
        Returns:
            Error summary with counts by severity and type
        """
        cutoff_time = time.time() - (last_n_hours * 3600)
        recent_errors = [e for e in self.errors if e.timestamp >= cutoff_time]
        
        summary = {
            "total_errors": len(recent_errors),
            "time_window_hours": last_n_hours,
            "by_severity": defaultdict(int),
            "by_error_type": defaultdict(int),
            "by_collection": defaultdict(int),
            "recent_errors": []
        }
        
        for error in recent_errors:
            summary["by_severity"][error.severity] += 1
            summary["by_error_type"][error.error_type] += 1
            summary["by_collection"][error.collection] += 1
        
        # Get last 10 errors
        summary["recent_errors"] = [e.to_dict() for e in recent_errors[-10:]]
        
        # Convert defaultdicts to regular dicts
        summary["by_severity"] = dict(summary["by_severity"])
        summary["by_error_type"] = dict(summary["by_error_type"])
        summary["by_collection"] = dict(summary["by_collection"])
        
        return summary
    
    def export_metrics_to_file(self, filepath: str = "chromadb_metrics.json"):
        """Export metrics to JSON file for analysis"""
        try:
            data = {
                "timestamp": datetime.now().isoformat(),
                "metrics": self.get_metrics(),
                "error_summary": self.get_error_summary(last_n_hours=24),
                "total_errors": len(self.errors)
            }
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"✅ Metrics exported to {filepath}")
            return filepath
        
        except Exception as e:
            logger.error(f"Failed to export metrics: {e}")
            return None


# Global monitor instance
chromadb_monitor = ChromaDBMonitor()


# Helper function for easy integration
def monitor_chromadb_operation(operation: str, collection: str):
    """
    Decorator/context manager for monitoring ChromaDB operations
    
    Usage:
        @monitor_chromadb_operation("query", "portfolio_master")
        def my_query_function():
            return collection.query(...)
        
        # OR as context manager:
        with monitor_chromadb_operation("add", "portfolio_master"):
            collection.add(...)
    """
    return chromadb_monitor.track_operation(operation, collection)


if __name__ == "__main__":
    # Test monitoring system
    print("ChromaDB Monitor - Test Mode\n")
    
    monitor = ChromaDBMonitor(alert_threshold_minutes=1)
    
    # Simulate operations
    print("Simulating successful query...")
    monitor.track_success("query", "portfolio_master", duration_ms=250.5)
    
    print("Simulating failed query...")
    monitor.track_failure("query", "portfolio_master", duration_ms=1500.0)
    
    print("Logging CRITICAL error...")
    monitor.log_error(
        operation="query",
        collection="portfolio_master",
        error_type="CollectionNotFound",
        error_message="Collection 'portfolio_master' does not exist",
        severity="CRITICAL",
        context={"session_id": "test-123", "query": "What are his projects?"}
    )
    
    print("\nMetrics Summary:")
    metrics = monitor.get_metrics()
    print(json.dumps(metrics, indent=2))
    
    print("\nError Summary (last 24 hours):")
    error_summary = monitor.get_error_summary(last_n_hours=24)
    print(json.dumps(error_summary, indent=2))
    
    print("\nExporting metrics to file...")
    filepath = monitor.export_metrics_to_file("test_chromadb_metrics.json")
    if filepath:
        print(f"✅ Metrics exported to {filepath}")
