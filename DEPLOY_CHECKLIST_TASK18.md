# Task 18 Deployment Checklist - ChromaDB Migration

**Date:** January 2, 2026  
**Status:** Ready for Execution

---

## Pre-Flight Check

```bash
# Verify all commits are on GitHub
cd /c/portfolio/portfolio
git log -5 --oneline
```

**Expected commits:**
- ✅ fc22cc0: Production deployment guide
- ✅ 6c16fcc: Monitoring system
- ✅ 73ff132: Test suites updated
- ✅ c115a90: S3 sync dual-write
- ✅ 57ba2c3: Auto-blogger dual-write

---

## Step 1: SSH to EC2

```bash
ssh -i "<path-to-pem-file>" ec2-user@<ec2-ip-address>
```

---

## Step 2: Verify GitHub Actions Deployment

```bash
# Check current directory
cd portfolio

# Verify latest commits pulled
git log -3 --oneline

# Check Docker container status
docker ps -a | grep portfolio-backend
```

**If commits NOT up to date:**
```bash
git pull origin main
docker restart portfolio-backend
```

---

## Step 3: Run Migration Script

```bash
# Dry-run first (SAFE - no changes)
python backend/migrate_to_master.py --dry-run
```

**Expected output:**
```
[DRY-RUN] Mode: DRY-RUN
✅ Connected to ChromaDB Cloud
📊 Checking legacy collections...
  ✅ portfolio: 33 items
  ✅ Projects_data: 3 items
  ✅ Blogs_data: 11 items
```

**Run actual migration:**
```bash
python backend/migrate_to_master.py
# Type "yes" when prompted
```

**Expected output:**
```
✅ portfolio migration complete: 33 items
✅ Projects_data migration complete: 3 items
✅ Blogs_data migration complete: 11 items
✅ Validation Summary: 4/4 checks passed
🎉 MIGRATION COMPLETE!
Total Success: 47
Total Failed: 0
```

---

## Step 4: Verify Migration Success

```bash
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

collection = client.get_collection('portfolio_master')
print(f'✅ portfolio_master: {collection.count()} items')

profile = len(collection.get(where={'category': 'profile'})['ids'])
project = len(collection.get(where={'category': 'project'})['ids'])
blog = len(collection.get(where={'category': 'blog'})['ids'])

print(f'  - profile: {profile}')
print(f'  - project: {project}')
print(f'  - blog: {blog}')
"
```

**Expected output:**
```
✅ portfolio_master: 47 items
  - profile: 33
  - project: 3
  - blog: 11
```

---

## Step 5: Update .env for Unified Collection

```bash
# Backup current .env
cp /home/ec2-user/.env /home/ec2-user/.env.backup.$(date +%Y%m%d_%H%M%S)

# Edit .env
nano /home/ec2-user/.env
```

**Add this line:**
```bash
USE_LEGACY_COLLECTIONS=false
```

**Save:** `Ctrl+O` → `Enter` → `Ctrl+X`

**Verify:**
```bash
grep USE_LEGACY_COLLECTIONS /home/ec2-user/.env
```

---

## Step 6: Restart Docker Container

```bash
docker restart portfolio-backend

# Wait 10 seconds
sleep 10

# Check logs for startup
docker logs portfolio-backend --tail 100
```

**Look for:**
```
✅ INFO:PortfolioBackend: Using UNIFIED collection (portfolio_master)
✅ INFO:PortfolioBackend: Per-session rate limiter active (12 RPM)
✅ INFO:PortfolioBackend: Token limits: 6K input, 24K/100K context
```

**Red flags (ROLLBACK if seen):**
```
❌ ERROR: Collection [portfolio_master] does not exist
❌ CRITICAL: Migration validation failed
```

---

## Step 7: Test Chatbot Endpoint

```bash
# Test from EC2
curl -X POST http://localhost:8000/api/ask-all-u-bot \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are your skills?",
    "session_id": "deployment-test-'$(date +%s)'"
  }'
```

**Expected:** JSON response with skills information

---

## Step 8: Monitor Logs (30 minutes)

```bash
# Stream logs
docker logs -f portfolio-backend

# In another terminal, check for errors
docker logs portfolio-backend | grep -i error | tail -20
docker logs portfolio-backend | grep -i chromadb | tail -30
```

**Success indicators:**
- ✅ No "collection not found" errors
- ✅ Queries return results from portfolio_master
- ✅ Per-session rate limiting working
- ✅ No timeout errors

---

## Emergency Rollback (If Needed)

```bash
# Step 1: Edit .env
nano /home/ec2-user/.env

# Step 2: Change to:
USE_LEGACY_COLLECTIONS=true

# Step 3: Save and restart
docker restart portfolio-backend

# Step 4: Verify rollback
docker logs portfolio-backend --tail 50 | grep "LEGACY"
```

**Expected:** `INFO:PortfolioBackend: Using LEGACY collections (3 separate)`

---

## Post-Deployment Validation

**Test from browser:**
1. Visit: https://www.althafportfolio.site
2. Open chatbot
3. Test queries:
   - "What are your skills?"
   - "Tell me about your AWS projects"
   - "What are your recent blogs?"
   - "What certifications do you have?"
   - "What is your experience?"

**All responses should be accurate and complete.**

---

## 48-Hour Monitoring Schedule

**Hours 0-1:** Check logs every 10 minutes
**Hours 1-6:** Check logs every 30 minutes
**Hours 6-24:** Check logs every 2 hours
**Hours 24-48:** Check logs every 4 hours

**Commands:**
```bash
# Check for errors
docker logs portfolio-backend | grep -i error | tail -50

# Check ChromaDB operations
docker logs portfolio-backend | grep -i chromadb | tail -50

# Check container health
docker stats portfolio-backend --no-stream
```

---

## Success Criteria (Before Task 19)

- [ ] Migration completed: 47 items in portfolio_master
- [ ] No "collection not found" errors in 48 hours
- [ ] Chatbot responds correctly to all query types
- [ ] Container stable (no crashes/restarts)
- [ ] Per-session rate limiting working
- [ ] No timeout errors

**If all checks pass after 48 hours → Proceed to Task 19**

---

**Deployment Time:** ~15-20 minutes  
**Rollback Time:** ~2 minutes (env var change + restart)
