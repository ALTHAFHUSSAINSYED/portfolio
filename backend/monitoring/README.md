# ChromaDB Migration Monitoring System

**Created:** January 2, 2026 (Task 16)  
**Status:** Ready for deployment  
**Purpose:** Track ChromaDB operations, detect errors, and send alerts during migration

## Overview

The monitoring system provides:
- **Operation tracking**: Success/failure metrics for all ChromaDB operations
- **Error classification**: CRITICAL/HIGH/MEDIUM/LOW severity levels
- **Alert system**: Slack webhooks and email notifications
- **Rate limiting**: Prevents alert spam (5-minute threshold)
- **Metrics export**: JSON export for analysis

## Quick Start

### 1. Environment Variables

Add to `.env` on EC2:

```bash
# Monitoring & Alerts (Optional - enables notifications)
ENABLE_SLACK_ALERTS=true
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

ENABLE_EMAIL_ALERTS=true
ALERT_EMAIL=your-email@example.com
```

**Note:** If these are not set, monitoring still tracks operations but doesn't send external alerts.

### 2. Integration

The monitoring system is already integrated into:
- [backend/server.py](../server.py) - Chatbot RAG pipeline
- [backend/auto_blogger/publisher.py](../auto_blogger/publisher.py) - Blog publishing

No additional setup needed - it works automatically.

### 3. Usage in Code

```python
from backend.monitoring import chromadb_monitor

# Track operation with context manager
with chromadb_monitor.track_operation("query", "portfolio_master"):
    results = collection.query(...)

# Manually log errors
chromadb_monitor.log_error(
    operation="query",
    collection="portfolio_master",
    error_type="CollectionNotFound",
    error_message="Collection 'portfolio_master' does not exist",
    severity="CRITICAL",
    context={"session_id": "abc123", "query": "What are his projects?"}
)

# Get metrics
metrics = chromadb_monitor.get_metrics()
print(json.dumps(metrics, indent=2))

# Export metrics to file
chromadb_monitor.export_metrics_to_file("metrics.json")
```

## Error Severity Levels

| Severity | When to Use | Alert Sent? |
|----------|-------------|-------------|
| **CRITICAL** | Collection not found, RAG pipeline failure | ✅ Yes (Slack + Email) |
| **HIGH** | Query failures, embedding failures | ✅ Yes (Slack + Email) |
| **MEDIUM** | Partial sync failures, retry exhausted | ❌ No |
| **LOW** | Warning-level issues | ❌ No |

## Monitored Operations

### Chatbot (server.py)
- `get_collection`: Get ChromaDB collection handle
- `query`: RAG retrieval queries
- `rag_pipeline`: Overall RAG pipeline execution

### Auto-Blogger (publisher.py)
- `add`: Blog embedding to ChromaDB
- `upsert`: Update existing blog embeddings

## Alert Examples

### Slack Alert
```
🚨 ChromaDB Alert [CRITICAL]
CollectionNotFound on collection `portfolio_master`

Operation: query
Collection: portfolio_master
Error: Collection 'portfolio_master' does not exist
Timestamp: 2026-01-02 15:30:00 UTC
Severity: CRITICAL
```

### Email Alert
HTML-formatted email with:
- Severity-based color coding (red for CRITICAL, orange for HIGH)
- Structured table with error details
- Timestamp in UTC
- Automated footer

## Metrics Dashboard

View metrics with:

```python
from backend.monitoring import chromadb_monitor

# Get all metrics
metrics = chromadb_monitor.get_metrics()

# Get specific collection
metrics = chromadb_monitor.get_metrics(collection="portfolio_master")

# Get error summary (last 24 hours)
error_summary = chromadb_monitor.get_error_summary(last_n_hours=24)
```

**Metrics include:**
- Success count
- Failure count
- Success rate (%)
- Average operation duration (ms)
- Last success/failure timestamps

## Migration Monitoring

### Pre-Migration (Legacy Mode)
```bash
# On EC2
export USE_LEGACY_COLLECTIONS=true
docker restart portfolio-backend

# Monitor operations on 3 collections
# - portfolio
# - Projects_data
# - Blogs_data
```

### Post-Migration (Unified Mode)
```bash
# On EC2
export USE_LEGACY_COLLECTIONS=false
docker restart portfolio-backend

# Monitor operations on 1 collection
# - portfolio_master
```

### During Dual-Write Phase
Both legacy and unified collections are monitored. Partial failures are logged as **HIGH** severity (not CRITICAL) to allow graceful degradation.

## Testing

Run the test suite:

```bash
cd backend/monitoring
python chromadb_monitor.py
```

Output includes:
- Simulated operations (success/failure)
- Error logging (CRITICAL severity)
- Metrics summary (JSON format)
- Error summary (24-hour window)
- Metrics export to file

## Alert Rate Limiting

**Default:** 5 minutes between duplicate alerts

Prevents spam when the same error occurs repeatedly. Alerts are keyed by:
```python
alert_key = f"{collection}:{error_type}"
```

Example:
- First `CollectionNotFound` on `portfolio_master` → Alert sent
- Second occurrence within 5 min → Alert suppressed
- Third occurrence after 5 min → Alert sent again

## Deployment Checklist

- [x] **Task 16.1:** Create monitoring module ([chromadb_monitor.py](chromadb_monitor.py))
- [x] **Task 16.2:** Integrate into server.py (chatbot RAG pipeline)
- [x] **Task 16.3:** Integrate into auto_blogger/publisher.py (blog embedding)
- [ ] **Task 16.4:** Configure Slack webhook URL (manual)
- [ ] **Task 16.5:** Configure alert email (manual)
- [ ] **Task 16.6:** Test alerts on staging environment
- [ ] **Task 16.7:** Deploy to production EC2
- [ ] **Task 16.8:** Monitor for 48 hours during Phase 1 deployment

## Files

| File | Purpose | Lines |
|------|---------|-------|
| [chromadb_monitor.py](chromadb_monitor.py) | Core monitoring system | ~450 |
| [__init__.py](__init__.py) | Package exports | ~15 |
| [README.md](README.md) | This documentation | ~200 |

## Example Metrics Output

```json
{
  "portfolio_master": {
    "query": {
      "success_count": 125,
      "failure_count": 2,
      "success_rate": 98.43,
      "avg_duration_ms": 285.6,
      "last_success_time": 1704211800.0,
      "last_failure_time": 1704208200.0
    },
    "add": {
      "success_count": 8,
      "failure_count": 0,
      "success_rate": 100.0,
      "avg_duration_ms": 450.2
    }
  }
}
```

## Troubleshooting

### No alerts received

1. Check environment variables:
   ```bash
   echo $ENABLE_SLACK_ALERTS
   echo $SLACK_WEBHOOK_URL
   ```

2. Check logs:
   ```bash
   docker logs portfolio-backend | grep "ChromaDBMonitor"
   ```

3. Test Slack webhook manually:
   ```bash
   curl -X POST -H 'Content-type: application/json' \
     --data '{"text":"Test alert"}' \
     $SLACK_WEBHOOK_URL
   ```

### Monitoring not working

1. Check import in logs:
   ```bash
   docker logs portfolio-backend | grep "ChromaDBMonitor initialized"
   ```

2. Verify module exists:
   ```bash
   docker exec -it portfolio-backend ls /app/backend/monitoring/
   ```

3. Check for import errors:
   ```bash
   docker exec -it portfolio-backend python -c "from backend.monitoring import chromadb_monitor; print('OK')"
   ```

## CloudWatch Integration (Future)

For AWS CloudWatch integration:

1. Install boto3 (already available)
2. Configure AWS credentials on EC2
3. Add CloudWatch client to monitoring module:
   ```python
   import boto3
   cloudwatch = boto3.client('cloudwatch', region_name='us-east-1')
   ```
4. Push metrics to CloudWatch:
   ```python
   cloudwatch.put_metric_data(
       Namespace='Portfolio/ChromaDB',
       MetricData=[{
           'MetricName': 'QuerySuccessRate',
           'Value': success_rate,
           'Unit': 'Percent'
       }]
   )
   ```

## Support

For issues or questions:
- Check logs: `/home/ec2-user/portfolio-logs/`
- Review metrics: Run `chromadb_monitor.export_metrics_to_file()`
- Contact: ALERT_EMAIL from environment variables

---

**Status:** ✅ Ready for deployment (code complete)  
**Next Step:** Configure Slack/Email webhooks and deploy to staging for validation
