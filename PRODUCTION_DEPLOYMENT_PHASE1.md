# Production Deployment - Phase 1: ChromaDB Unified Collection

**Date:** January 2, 2026  
**Task:** Deploy unified `portfolio_master` collection to production  
**Status:** ⏳ IN PROGRESS  
**Risk Level:** MEDIUM (Rollback available via env var)

---

## Pre-Deployment Checklist

✅ **Completed:**
- [x] Migration script tested locally (47 items migrated successfully)
- [x] Validation passed (4/4 checks: counts match perfectly)
- [x] Rollback mechanism implemented (USE_LEGACY_COLLECTIONS env var)
- [x] Monitoring system created (chromadb_monitor.py)
- [x] Dual-write enabled in auto-blogger and S3 sync scripts
- [x] Code pushed to GitHub main branch (latest commits)

⏳ **Pending:**
- [ ] SSH to EC2 instance
- [ ] Run migration script on production
- [ ] Verify portfolio_master collection created
- [ ] Update .env to enable unified collection mode
- [ ] Restart Docker container
- [ ] Monitor logs for 48 hours

---

## Deployment Steps

### Step 1: SSH to EC2 Instance

```bash
# Replace with your EC2 details
ssh -i "<path-to-your-pem-file>" ec2-user@<your-ec2-ip-address>

# Example:
# ssh -i "~/portfolio-key.pem" ec2-user@54.123.45.67
```

**Expected Output:**
```
Last login: [timestamp]
       __|  __|_  )
       _|  (     /   Amazon Linux 2 AMI
      ___|\___|___|
```

---

### Step 2: Navigate to Project Directory

```bash
cd portfolio
```

---

### Step 3: Pull Latest Code from GitHub

```bash
# Fetch latest changes
git fetch origin main

# Check current commit
git log -1 --oneline

# Pull latest code
git pull origin main
```

**Expected Output:**
```
Updating [old-hash]..[new-hash]
Fast-forward
 backend/server.py                    | XX ++--
 backend/chatbot_provider.py          | XX ++--
 backend/rate_limiter.py              | XX ++--
 backend/chromadb_monitor.py          | XXX ++++++++++
 backend/notification_service.py      | XX ++--
 ...
```

**Verify Latest Commits:**
```bash
git log -5 --oneline
```

Should show:
- Migration script creation (commit eb7355e)
- Per-session rate limiter (commit f12fa95)
- Token limit updates (commit a947c52)
- Monitoring system (commit 6c16fcc)
- Documentation updates (commit 26b5585)

---

### Step 4: Backup Current .env File

```bash
# Create backup
cp /home/ec2-user/.env /home/ec2-user/.env.backup.$(date +%Y%m%d_%H%M%S)

# Verify backup created
ls -lh /home/ec2-user/.env*
```

---

### Step 5: Run Migration Script on Production

**⚠️ CRITICAL: Run dry-run first!**

```bash
# Activate virtual environment (if applicable)
# source venv/bin/activate

# Run dry-run to preview migration
python backend/migrate_to_master.py --dry-run
```

**Expected Output:**
```
[DRY-RUN] Mode: DRY-RUN
✅ Connected to ChromaDB Cloud
📊 Checking legacy collections...
  ✅ portfolio: 33 items
  ✅ Projects_data: 3 items
  ✅ Blogs_data: 11 items

📊 Total items to migrate: 47

🔍 Checking for existing portfolio_master...
  ✅ portfolio_master does not exist (ready for migration)

📦 Starting data migration...
[... dry-run output ...]

[DRY-RUN] No changes made. Run without --dry-run to execute migration.
```

**Run Actual Migration:**

```bash
# Execute migration (will prompt for confirmation)
python backend/migrate_to_master.py
```

**When prompted, type:** `yes`

**Expected Output:**
```
⚠️ WARNING: This will create portfolio_master collection and migrate all data.
Existing embeddings will be reused (no Gemini API cost).

Continue? (yes/no): yes

🚀 ChromaDB Migration: Legacy → portfolio_master
===================================================================
✅ Connected to ChromaDB Cloud
📊 Checking legacy collections...
  ✅ portfolio: 33 items
  ✅ Projects_data: 3 items
  ✅ Blogs_data: 11 items

🔧 Creating portfolio_master collection...
✅ portfolio_master created successfully

📦 Migrating portfolio → portfolio_master (category='profile')...
  ✅ Batch 1: Migrated 33 items
✅ portfolio migration complete: 33 items

📦 Migrating Projects_data → portfolio_master (category='project')...
  ✅ Batch 1: Migrated 3 items
✅ Projects_data migration complete: 3 items

📦 Migrating Blogs_data → portfolio_master (category='blog')...
  ✅ Batch 1: Migrated 11 items
✅ Blogs_data migration complete: 11 items

🔍 Validating migration integrity...
  ✅ Check 1: Total count matches
  ✅ Check 2: Profile count matches
  ✅ Check 3: Project count matches
  ✅ Check 4: Blog count matches

✅ Validation Summary: 4/4 checks passed
🎉 Migration validated successfully!

📊 MIGRATION SUMMARY
===================================================================
Legacy Collections:
  portfolio: 33 items
  Projects_data: 3 items
  Blogs_data: 11 items

Migration Statistics:
  profile: 33 success, 0 failed (total: 33)
  project: 3 success, 0 failed (total: 3)
  blog: 11 success, 0 failed (total: 11)

Overall:
  Total Success: 47
  Total Failed: 0
  Duration: ~20 seconds

🎉 MIGRATION COMPLETE!
```

---

### Step 6: Verify Migration Success

```bash
# Quick verification script
python -c "
import chromadb
import os
from dotenv import load_dotenv

load_dotenv('/home/ec2-user/.env')

client = chromadb.CloudClient(
    tenant=os.getenv('CHROMA_TENANT_ID'),
    database=os.getenv('CHROMA_DATABASE', 'Development'),
    api_key=os.getenv('CHROMA_API_KEY')
)

# Check portfolio_master exists and has correct count
try:
    collection = client.get_collection('portfolio_master')
    count = collection.count()
    print(f'✅ portfolio_master exists: {count} items')
    
    # Verify category distribution
    profile_count = len(collection.get(where={'category': 'profile'})['ids'])
    project_count = len(collection.get(where={'category': 'project'})['ids'])
    blog_count = len(collection.get(where={'category': 'blog'})['ids'])
    
    print(f'✅ Category distribution:')
    print(f'   - profile: {profile_count} items')
    print(f'   - project: {project_count} items')
    print(f'   - blog: {blog_count} items')
except Exception as e:
    print(f'❌ Error: {e}')
"
```

**Expected Output:**
```
✅ portfolio_master exists: 47 items
✅ Category distribution:
   - profile: 33 items
   - project: 3 items
   - blog: 11 items
```

---

### Step 7: Update .env to Enable Unified Collection Mode

```bash
# Edit .env file
nano /home/ec2-user/.env
```

**Add or update this line:**
```bash
USE_LEGACY_COLLECTIONS=false
```

**Save and exit:**
- Press `Ctrl + O` to save
- Press `Enter` to confirm
- Press `Ctrl + X` to exit

**Verify the change:**
```bash
grep USE_LEGACY_COLLECTIONS /home/ec2-user/.env
```

**Expected Output:**
```
USE_LEGACY_COLLECTIONS=false
```

---

### Step 8: Restart Docker Container

```bash
# Check current container status
docker ps -a

# Restart the backend container
docker restart portfolio-backend

# Wait 10 seconds for container to start
sleep 10

# Check container logs for startup errors
docker logs portfolio-backend --tail 100
```

**Expected Logs (Healthy Startup):**
```
INFO:     Started server process [XX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:PortfolioBackend: Using UNIFIED collection (portfolio_master)
INFO:PortfolioBackend: Per-session rate limiter active (12 RPM)
INFO:PortfolioBackend: Token limits: 6K input, 24K/100K context, 300/800 output
```

**⚠️ Red Flags (If you see these, rollback immediately):**
```
ERROR: Collection [portfolio_master] does not exist
ERROR: Failed to connect to ChromaDB
CRITICAL: Migration validation failed
```

---

### Step 9: Test Chatbot Endpoint

```bash
# Test from EC2 instance
curl -X POST http://localhost:8000/api/ask-all-u-bot \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are your skills?",
    "session_id": "test-session-123"
  }'
```

**Expected Response:**
```json
{
  "reply": "Althaf specializes in DevOps, cloud computing, Python, Terraform, AWS...",
  "session_id": "test-session-123",
  "timestamp": "2026-01-02T..."
}
```

**Test from external browser:**
Visit: `https://www.althafportfolio.site` and open chatbot.

**Test queries (at least 5):**
1. "What are your skills?"
2. "Tell me about your AWS projects"
3. "What are your recent blogs?"
4. "What certifications do you have?"
5. "What is your experience?"

---

### Step 10: Monitor Docker Logs (First Hour)

```bash
# Stream logs in real-time
docker logs -f portfolio-backend

# In another terminal, monitor for errors
docker logs portfolio-backend | grep -i error | tail -20
docker logs portfolio-backend | grep -i chromadb | tail -20
```

**What to Look For:**
- ✅ `Using UNIFIED collection (portfolio_master)` on startup
- ✅ Successful ChromaDB queries (no 404 errors)
- ✅ Per-session rate limiting working (12 RPM per session)
- ✅ No "Collection not found" errors
- ⚠️ Any ChromaDB API errors
- ⚠️ Timeout errors
- ❌ CRITICAL: Migration validation failures

---

## Rollback Procedure (If Needed)

**If you encounter issues, rollback immediately:**

```bash
# Step 1: Update .env to use legacy collections
nano /home/ec2-user/.env

# Change this line:
USE_LEGACY_COLLECTIONS=true

# Save and exit (Ctrl+O, Enter, Ctrl+X)

# Step 2: Restart Docker container
docker restart portfolio-backend

# Step 3: Verify rollback
docker logs portfolio-backend --tail 50 | grep "LEGACY"
```

**Expected Rollback Log:**
```
INFO:PortfolioBackend: Using LEGACY collections (3 separate)
```

**Rollback completed!** System now uses old 3-collection architecture.

---

## 48-Hour Monitoring Plan

**Day 1 (Hours 0-24):**
- **Hour 0-1:** Intensive monitoring (stream logs, test chatbot every 10 minutes)
- **Hour 1-6:** Check logs every 30 minutes
- **Hour 6-24:** Check logs every 2 hours

**Day 2 (Hours 24-48):**
- **Hour 24-36:** Check logs every 2 hours
- **Hour 36-48:** Check logs every 4 hours

**Monitoring Commands:**

```bash
# Check for errors
docker logs portfolio-backend | grep -i error | tail -50

# Check ChromaDB operations
docker logs portfolio-backend | grep -i chromadb | tail -50

# Check rate limiter activity
docker logs portfolio-backend | grep -i "rate limit" | tail -20

# Check disk space (ensure not full)
df -h

# Check container resource usage
docker stats portfolio-backend --no-stream
```

**Alert Thresholds:**
- ❌ **ROLLBACK IMMEDIATELY:** >10 ChromaDB errors in 1 hour
- ⚠️ **Investigate:** >5 errors in 1 hour
- ✅ **Healthy:** 0-2 errors per hour (acceptable noise)

---

## Success Criteria (After 48 Hours)

✅ **All must pass before proceeding to Task 19:**
- [ ] Zero critical ChromaDB errors
- [ ] No "Collection not found" errors
- [ ] Chatbot responds correctly to profile/project/blog queries
- [ ] Per-session rate limiting working (12 RPM per session)
- [ ] No timeout errors
- [ ] OpenRouter TPM usage within expected range (48K-72K TPM)
- [ ] Container uptime = 48 hours (no crashes)

---

## Deployment Timeline

**Phase 1 (Current):** Chatbot unified collection deployment
- **Start:** January 2, 2026 [NOW]
- **End:** January 4, 2026 (after 48-hour validation)

**Phase 2:** Auto-blogger dual-write (Task 20)
- **Start:** January 4, 2026
- **End:** January 6, 2026

**Phase 3:** Cutover to master-only (Task 21)
- **Start:** January 6, 2026
- **End:** January 7, 2026

**Final Phase:** Delete legacy collections (Task 22)
- **Start:** January 10, 2026 (after 7-day validation)

---

## Contact Information

**If issues arise:**
1. Check `CHROMADB_MIGRATION_AUDIT.md` for dependency reference
2. Check `DUAL_WRITE_STRATEGY.md` for migration strategy
3. Check `CHATBOT_ARCHITECTURE.md` for architecture details
4. Check Docker logs: `docker logs portfolio-backend --tail 500`
5. Rollback immediately if >10 errors in 1 hour

**Monitoring Email Alerts:**
- Configured via `backend/chromadb_monitor.py`
- Alerts sent to `TO_EMAIL` env var
- Cooldown: 5 minutes between alerts
- Threshold: 5 errors trigger alert

---

## Post-Deployment Verification Checklist

After 48 hours, verify:
- [ ] Chatbot responds correctly to all query types
- [ ] No ChromaDB errors in logs
- [ ] Rate limiting working (12 RPM per session)
- [ ] OpenRouter TPM usage reasonable
- [ ] Container stable (no restarts)
- [ ] Memory usage stable
- [ ] Disk space sufficient
- [ ] Auto-blogger still functioning (dual-write)

If all checks pass → Proceed to **Task 19** (Validate Chatbot Performance)

---

**Deployment Script Version:** 1.0  
**Last Updated:** January 2, 2026  
**Status:** ⏳ AWAITING EXECUTION
