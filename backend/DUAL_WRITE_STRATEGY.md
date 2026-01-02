# Dual-Write Strategy for ChromaDB Migration

**Document Version:** 1.0  
**Created:** January 2, 2026  
**Migration Target:** Unified `portfolio_master` collection  
**Validation Window:** 48 hours (per component)  
**Status:** PLANNING

---

## Executive Summary

This document outlines the dual-write strategy for safely migrating from 3 separate ChromaDB collections (`portfolio`, `Projects_data`, `Blogs_data`) to a unified `portfolio_master` collection. The strategy ensures **zero downtime** and **data consistency** through parallel write operations during a 48-hour validation window.

### Key Principles
1. ✅ **Write to Both:** All writes go to legacy AND master collections simultaneously
2. ✅ **Read from Legacy:** Continue reading from legacy collections during validation
3. ✅ **Validate Consistency:** Compare data between legacy and master collections
4. ✅ **Graceful Degradation:** Partial write success is acceptable (prioritize availability)
5. ✅ **Instant Rollback:** Environment variable toggle for immediate rollback

---

## 1. Migration Phases

### Phase 0: Pre-Migration Setup (Completed)
- ✅ Audit all ChromaDB dependencies (27 files)
- ✅ Create dependency impact report
- ✅ Implement per-session rate limiting (12 RPM)
- ⏳ Design dual-write strategy (this document)

### Phase 1: Chatbot Dual-Read (48 Hours)
**Timeline:** Day 1-2 of migration  
**Objective:** Deploy unified collection query logic with legacy fallback  
**Rollback:** `USE_LEGACY_COLLECTIONS=true`

**Components:**
- `server.py`: Update `get_portfolio_context()` with unified query
- `chatbot_provider.py`: Token limit updates (6K Mistral, 25K Gemini)
- Monitoring: OpenRouter TPM usage, CloudWatch logs

**Success Criteria:**
- Zero 404 collection not found errors
- Query response time ≤200ms (vs. 600ms baseline)
- Token efficiency: 6 chunks (7200 chars) vs. 28 chunks baseline

### Phase 2: Auto-Blogger Dual-Write (48 Hours)
**Timeline:** Day 3-4 of migration  
**Objective:** Write daily blogs to both `Blogs_data` AND `portfolio_master`  
**Rollback:** Revert `publisher.py` to single write

**Components:**
- `auto_blogger/publisher.py`: Dual-write implementation
- `auto_blogger/cleanup.py`: Continue using `Blogs_data` only
- Monitoring: Email notifications, S3 blog count

**Success Criteria:**
- 100% successful dual writes (2/2 daily blogs)
- Blog data identical in both collections
- No email failure notifications

### Phase 3: Auto-Blogger Master-Only (24 Hours)
**Timeline:** Day 5 of migration  
**Objective:** Switch auto-blogger to write only to `portfolio_master`  
**Rollback:** Re-enable `Blogs_data` writes

**Components:**
- `auto_blogger/publisher.py`: Remove legacy write code
- `auto_blogger/cleanup.py`: Update to use `portfolio_master` with category filter
- Monitoring: Daily blog publish success rate

**Success Criteria:**
- All new blogs have `category='blog'` metadata tag
- Cleanup targets only blogs (not projects/profile)
- Zero publish failures

### Phase 4: Legacy Collection Deletion (After 7 Days)
**Timeline:** Day 12+ of migration  
**Objective:** Delete old collections, finalize migration  
**No Rollback:** Permanent change

**Components:**
- Delete `portfolio`, `Projects_data`, `Blogs_data` collections
- Remove rollback code from `server.py`
- Update all documentation

---

## 2. Dual-Write Implementation Patterns

### 2.1 Auto-Blogger Publisher (Dual-Write)

**File:** `backend/auto_blogger/publisher.py`  
**Validation Window:** 48 hours  
**Write Strategy:** Optimistic (partial success acceptable)

```python
def publish_to_chromadb(self, blog: Dict[str, Any]) -> bool:
    """
    Dual-write implementation with graceful degradation.
    
    Strategy:
    1. Write to legacy collection (Blogs_data)
    2. Write to master collection (portfolio_master)
    3. Accept partial success (at least one write succeeds)
    4. Log detailed write status for monitoring
    
    Validation:
    - Both writes succeed: ✅ IDEAL (log success)
    - One write succeeds: ⚠️ ACCEPTABLE (log warning)
    - Both writes fail: ❌ CRITICAL (send email notification)
    """
    success_legacy = False
    success_master = False
    
    # Write 1: Legacy collection (Blogs_data)
    try:
        collection_legacy = self.chroma_client.get_collection('Blogs_data')
        collection_legacy.add(
            ids=[blog['id']],
            documents=[blog['content']],
            metadatas=[{
                'title': blog['title'],
                'category': blog['category'],  # DevOps/Cloud/Cybersecurity
                'url': blog['url'],
                'timestamp': blog['timestamp']
            }]
        )
        logger.info(f"✅ [LEGACY] Published blog {blog['id']} to Blogs_data")
        success_legacy = True
        
    except Exception as e:
        logger.error(f"❌ [LEGACY] Failed to publish to Blogs_data: {e}")
        # Continue to master write (don't abort)
    
    # Write 2: Master collection (portfolio_master)
    try:
        collection_master = self.chroma_client.get_collection('portfolio_master')
        collection_master.add(
            ids=[blog['id']],
            documents=[blog['content']],
            metadatas=[{
                'title': blog['title'],
                'category': 'blog',  # Unified category tag
                'subcategory': blog['category'],  # DevOps/Cloud/Cybersecurity
                'url': blog['url'],
                'timestamp': blog['timestamp']
            }]
        )
        logger.info(f"✅ [MASTER] Published blog {blog['id']} to portfolio_master")
        success_master = True
        
    except Exception as e:
        logger.error(f"❌ [MASTER] Failed to publish to portfolio_master: {e}")
    
    # Evaluate write success
    if success_legacy and success_master:
        logger.info(f"✅ [DUAL-WRITE SUCCESS] Blog {blog['id']} written to both collections")
        return True
        
    elif success_legacy or success_master:
        logger.warning(f"⚠️ [PARTIAL SUCCESS] Blog {blog['id']} written to {'legacy' if success_legacy else 'master'} only")
        # Acceptable during dual-write phase (prioritize availability)
        return True
        
    else:
        logger.error(f"❌ [COMPLETE FAILURE] Blog {blog['id']} failed to write to both collections")
        # Send critical failure notification
        asyncio.create_task(
            notification_service.send_blog_notification(
                success=False,
                blog_data=None,
                error=f"Dual-write failure for blog {blog['id']}"
            )
        )
        return False
```

**Validation Steps (48 Hours):**
1. Monitor logs for dual-write success rate (target: 100%)
2. Compare blog counts: `Blogs_data.count() == portfolio_master.query(where={"category": "blog"}).count()`
3. Spot-check 5 random blogs for metadata consistency
4. Verify email notifications sent only on complete failures

---

### 2.2 Chatbot Query Logic (Dual-Read with Rollback)

**File:** `backend/server.py`  
**Validation Window:** 48 hours  
**Read Strategy:** Toggle-based (instant rollback)

```python
# Environment variable for instant rollback
USE_LEGACY_COLLECTIONS = os.getenv('USE_LEGACY_COLLECTIONS', 'false').lower() == 'true'

async def get_portfolio_context_unified(query: str) -> str:
    """
    Unified collection query with intelligent metadata filtering.
    
    Strategy:
    - Single query to portfolio_master
    - Metadata filters based on query intent
    - Global limit: 6 chunks (reduced from 28)
    """
    collection = chroma_client.get_collection(
        'portfolio_master',
        embedding_function=GeminiEmbeddingFunction()
    )
    
    query_lower = query.lower()
    
    # Intelligent filtering based on query keywords
    if 'blog' in query_lower:
        # Strict blog filter
        results = collection.query(
            query_texts=[query],
            n_results=6,
            where={"category": "blog"}
        )
    elif 'project' in query_lower:
        # Mixed query: projects + profile context
        results = collection.query(
            query_texts=[query],
            n_results=6,
            where={"$or": [{"category": "project"}, {"category": "profile"}]}
        )
    else:
        # Global query: all categories
        results = collection.query(
            query_texts=[query],
            n_results=6
        )
    
    return format_results(results)

async def get_portfolio_context_legacy(query: str) -> str:
    """
    Legacy multi-collection query (ROLLBACK FALLBACK).
    
    Strategy:
    - Query all 3 collections separately
    - Collection-specific limits (portfolio=20, projects=3, blogs=5)
    - Total: 28 chunks (baseline behavior)
    """
    collections = ['portfolio', 'Projects_data', 'Blogs_data']
    context_parts = []
    
    for collection_name in collections:
        collection = chroma_client.get_collection(
            name=collection_name,
            embedding_function=GeminiEmbeddingFunction()
        )
        
        if collection_name == 'portfolio':
            limit = 20
        elif collection_name == 'Projects_data':
            limit = 3
        else:  # Blogs_data
            limit = 5
        
        results = collection.query(query_texts=[query], n_results=limit)
        context_parts.append(format_results(results, collection_name))
    
    return "\n\n".join(context_parts)

async def get_portfolio_context(query: str) -> str:
    """
    Router function with instant rollback capability.
    
    Toggle: USE_LEGACY_COLLECTIONS env var
    - true: Use legacy multi-collection query
    - false: Use unified portfolio_master query (default)
    """
    if USE_LEGACY_COLLECTIONS:
        logger.warning("⚠️ Using LEGACY collections (rollback mode)")
        return await get_portfolio_context_legacy(query)
    else:
        logger.info("✅ Using UNIFIED portfolio_master collection")
        return await get_portfolio_context_unified(query)
```

**Rollback Procedure:**
```bash
# On EC2 instance
ssh ec2-user@<ec2-ip>

# Set rollback flag
echo "USE_LEGACY_COLLECTIONS=true" >> /home/ec2-user/.env

# Restart Docker container (instant rollback)
docker restart portfolio-backend

# Verify rollback
docker logs portfolio-backend --tail 50 | grep "Using LEGACY collections"
```

**Expected Output:** `⚠️ Using LEGACY collections (rollback mode)`

**Validation Steps (48 Hours):**
1. Test 20+ chatbot queries (profile, projects, blogs, mixed)
2. Monitor OpenRouter TPM usage (should be 48K-72K at 8-12 RPM)
3. Verify query response times ≤200ms
4. Check CloudWatch for collection not found errors (should be zero)
5. Test rollback toggle (set `USE_LEGACY_COLLECTIONS=true`, restart, verify legacy mode)

---

### 2.3 Cleanup Script (Category-Filtered Delete)

**File:** `backend/auto_blogger/cleanup.py`  
**Validation Window:** N/A (cutover with Phase 3)  
**Delete Strategy:** Safety-first (requires category filter)

```python
def cleanup_old_blogs(cutoff_days: int = 60):
    """
    Delete blogs older than 60 days from portfolio_master.
    
    ⚠️ CRITICAL SAFETY: Always include category='blog' filter to prevent
    accidental deletion of projects/profile data.
    
    Strategy:
    1. Query portfolio_master with double filter (category + timestamp)
    2. Count affected blogs before deletion (verification)
    3. Execute deletion with $and operator
    4. Verify deletion success (count should be zero)
    """
    cutoff_timestamp = (datetime.now() - timedelta(days=cutoff_days)).isoformat()
    
    collection = chroma_client.get_collection('portfolio_master')
    
    # Step 1: Count blogs to be deleted (pre-deletion verification)
    blogs_to_delete = collection.count(where={
        "$and": [
            {"category": "blog"},
            {"timestamp": {"$lt": cutoff_timestamp}}
        ]
    })
    
    logger.info(f"📊 Found {blogs_to_delete} blogs older than {cutoff_days} days")
    
    if blogs_to_delete == 0:
        logger.info("✅ No old blogs to delete")
        return
    
    # Step 2: Execute deletion with safety filter
    try:
        collection.delete(where={
            "$and": [
                {"category": "blog"},  # ⚠️ CRITICAL: Prevents deleting projects/profile
                {"timestamp": {"$lt": cutoff_timestamp}}
            ]
        })
        logger.info(f"🗑️ Deleted {blogs_to_delete} blogs older than {cutoff_days} days")
        
    except Exception as e:
        logger.error(f"❌ Cleanup failed: {e}")
        raise
    
    # Step 3: Post-deletion verification (safety check)
    remaining = collection.count(where={
        "$and": [
            {"category": "blog"},
            {"timestamp": {"$lt": cutoff_timestamp}}
        ]
    })
    
    if remaining > 0:
        logger.warning(f"⚠️ {remaining} old blogs still exist after cleanup (retry needed)")
        raise Exception(f"Cleanup incomplete: {remaining} old blogs remaining")
    else:
        logger.info("✅ Cleanup verification passed (0 old blogs remaining)")
    
    # Step 4: Verify no projects/profile deleted (paranoid check)
    total_items = collection.count()
    blog_items = collection.count(where={"category": "blog"})
    project_items = collection.count(where={"category": "project"})
    profile_items = collection.count(where={"category": "profile"})
    
    expected_total = blog_items + project_items + profile_items
    
    if total_items != expected_total:
        logger.error(f"❌ Data integrity error: {total_items} != {expected_total}")
        raise Exception("Data integrity check failed after cleanup")
    
    logger.info(f"✅ Data integrity verified: {blog_items} blogs, {project_items} projects, {profile_items} profile")
```

**Safety Checks:**
1. ✅ Always use `$and` operator for double filtering
2. ✅ Count before deletion (verification step)
3. ✅ Count after deletion (safety check)
4. ✅ Verify total item count matches sum of categories

---

## 3. Validation Metrics

### 3.1 Chatbot (Phase 1)
**Metric** | **Target** | **Baseline** | **Monitoring**
-----------|------------|--------------|---------------
Query Response Time | ≤200ms | 600ms | CloudWatch Logs
Collection Not Found Errors | 0 | N/A | Error logs
Token Usage (per query) | 7200 chars (6 chunks) | 33600 chars (28 chunks) | OpenRouter dashboard
TPM Usage | 48K-72K TPM | N/A | OpenRouter dashboard (at 8-12 RPM)
Rate Limit Errors (429) | <1% | N/A | API error logs
Cache Hit Rate | ≥30% | N/A | Response cache stats

### 3.2 Auto-Blogger (Phase 2)
**Metric** | **Target** | **Baseline** | **Monitoring**
-----------|------------|--------------|---------------
Dual-Write Success Rate | 100% | N/A | Email notifications
Partial Write Failures | ≤2 per week | N/A | CloudWatch warnings
Complete Write Failures | 0 | N/A | Email alerts
Blog Count Consistency | Legacy == Master | N/A | Daily count comparison
Metadata Consistency | 100% match | N/A | Spot-check 5 blogs/day
Publish Time | ≤5 seconds | N/A | APScheduler logs

### 3.3 Data Integrity (All Phases)
**Metric** | **Target** | **Validation**
-----------|------------|--------------
Total Item Count | `portfolio_master.count() == portfolio + Projects_data + Blogs_data` | Migration script verification
Category Distribution | blogs=580, projects=15, profile=5 | Post-migration count
Embedding Dimensions | 768 (Gemini text-embedding-004) | Sample 10 embeddings
Metadata Completeness | 100% (all items have `category` tag) | Query all items, verify `category` field

---

## 4. Monitoring & Alerting

### 4.1 CloudWatch Logs (Real-Time)
**Alert Condition** | **Severity** | **Action**
--------------------|--------------|----------
Collection not found error | 🔴 CRITICAL | Instant rollback (`USE_LEGACY_COLLECTIONS=true`)
Dual-write complete failure | 🔴 CRITICAL | Email notification + manual investigation
Query response time >500ms | 🟡 WARNING | Review query optimization
Rate limit errors >10/hour | 🟡 WARNING | Increase per-session limit to 15 RPM
Partial write failure | 🟢 INFO | Log for post-migration analysis

### 4.2 Email Notifications (Daily Summary)
**Trigger** | **Recipient** | **Content**
------------|---------------|------------
Auto-blogger publish success | User (TO_EMAIL) | Blog title, category, URL, collection status
Auto-blogger publish failure | User (TO_EMAIL) | Error details, affected blog, retry instructions
Dual-write failure | User (TO_EMAIL) | Failed collection, timestamp, rollback instructions

### 4.3 Manual Checks (Daily)
1. **OpenRouter Dashboard:** Verify TPM usage is 48K-72K (at 8-12 RPM)
2. **ChromaDB Cloud:** Check collection counts match expected values
3. **GitHub Actions:** Verify backend deployment succeeded (no errors)
4. **Docker Logs:** `docker logs portfolio-backend --tail 100` - check for errors

---

## 5. Rollback Procedures

### 5.1 Instant Rollback (Environment Variable)
**Scenario:** Chatbot errors, collection not found, query failures  
**Duration:** <5 minutes  
**Impact:** Zero downtime

```bash
# Step 1: SSH to EC2
ssh ec2-user@<ec2-ip>

# Step 2: Enable legacy mode
echo "USE_LEGACY_COLLECTIONS=true" >> /home/ec2-user/.env

# Step 3: Restart Docker
docker restart portfolio-backend

# Step 4: Verify rollback
docker logs portfolio-backend --tail 50 | grep "Using LEGACY collections"
```

### 5.2 Code Rollback (GitHub Revert)
**Scenario:** Critical bugs in dual-write logic, data corruption  
**Duration:** 5-10 minutes  
**Impact:** Brief deployment window

```bash
# Step 1: Identify last working commit
git log --oneline

# Step 2: Revert to previous version
git revert <commit-hash>

# Step 3: Push to trigger GitHub Actions deployment
git push origin main

# Step 4: Monitor deployment
# GitHub Actions will auto-deploy to EC2 (~5 minutes)
```

### 5.3 Data Recovery (Nuclear Option)
**Scenario:** Master collection corrupted, legacy collections deleted  
**Duration:** 30-60 minutes  
**Impact:** Chatbot downtime during recovery

```bash
# Step 1: Run populate_vector_db.py to recreate legacy collections
python backend/populate_vector_db.py

# Step 2: Verify counts
# portfolio: ~5 items
# Projects_data: ~15 items
# Blogs_data: ~580 items

# Step 3: Enable legacy mode (see 5.1)

# Step 4: Test chatbot queries
```

---

## 6. Success Criteria (Go/No-Go Decision Points)

### Phase 1 Go-Live Criteria (Chatbot)
- ✅ Zero collection not found errors during 48-hour validation
- ✅ Query response time ≤200ms (vs. 600ms baseline)
- ✅ OpenRouter TPM usage 48K-72K (at 8-12 RPM)
- ✅ Rollback tested and verified working
- ✅ No rate limit errors (429) exceeding 1% threshold

**Decision:** Proceed to Phase 2 if all criteria met

### Phase 2 Go-Live Criteria (Auto-Blogger Dual-Write)
- ✅ 100% successful dual writes (4 blogs over 48 hours)
- ✅ Blog counts match: `Blogs_data.count() == portfolio_master.query(where={"category": "blog"}).count()`
- ✅ Metadata consistency verified (spot-checked 5 blogs)
- ✅ No email failure notifications sent
- ✅ Zero complete write failures

**Decision:** Proceed to Phase 3 if all criteria met

### Phase 3 Go-Live Criteria (Auto-Blogger Master-Only)
- ✅ All new blogs have `category='blog'` metadata tag
- ✅ Cleanup script targets only blogs (not projects/profile)
- ✅ Zero publish failures during 24-hour validation
- ✅ Data integrity checks pass (category distribution correct)

**Decision:** Schedule Phase 4 (legacy deletion) after 7 days if all criteria met

### Phase 4 Go-Live Criteria (Legacy Deletion)
- ✅ Zero errors for 7 consecutive days
- ✅ All systems operating on `portfolio_master` only
- ✅ Rollback code no longer needed (verified)
- ✅ Documentation updated to reflect new architecture

**Decision:** Delete legacy collections permanently

---

## 7. Communication Plan

### Pre-Migration (Day -1)
- 📧 Email user: Migration timeline, expected behavior, rollback instructions
- 📝 Update GitHub README: Add migration status badge
- 📊 Baseline metrics: Document current query times, TPM usage, blog counts

### During Migration (Day 1-7)
- 📧 Daily email: Validation status, metrics, any issues encountered
- 📝 Update GitHub Issues: Migration progress, blockers, next steps
- 📊 Dashboard: Real-time metrics (OpenRouter, CloudWatch, ChromaDB)

### Post-Migration (Day 8+)
- 📧 Email user: Migration complete, new architecture summary, lessons learned
- 📝 Update docs: CHATBOT_ARCHITECTURE.md, CHROMADB_MIGRATION_AUDIT.md
- 📊 Final report: Before/after metrics, performance improvements, cost savings

---

## 8. Risk Mitigation

### Risk 1: Chatbot 404 Errors (CRITICAL)
**Likelihood:** LOW (rollback toggle available)  
**Impact:** HIGH (user-facing downtime)  
**Mitigation:**
- ✅ Instant rollback via `USE_LEGACY_COLLECTIONS=true`
- ✅ 48-hour validation window before Phase 2
- ✅ CloudWatch alerts for collection errors

### Risk 2: Auto-Blogger Dual-Write Failures (HIGH)
**Likelihood:** MEDIUM (network issues, quota limits)  
**Impact:** MEDIUM (delayed blog publishing)  
**Mitigation:**
- ✅ Graceful degradation (partial success acceptable)
- ✅ Email notifications on complete failures
- ✅ Retry logic with exponential backoff

### Risk 3: Data Inconsistency (MEDIUM)
**Likelihood:** LOW (embedding reuse, verified migration)  
**Impact:** HIGH (incorrect chatbot responses)  
**Mitigation:**
- ✅ Daily count comparisons (legacy vs. master)
- ✅ Spot-check 5 blogs/day for metadata consistency
- ✅ Data integrity checks in cleanup script

### Risk 4: Memory Leaks (LOW)
**Likelihood:** LOW (per-session cleanup implemented)  
**Impact:** MEDIUM (container restarts needed)  
**Mitigation:**
- ✅ Inactive session cleanup (5-minute window)
- ✅ Memory monitoring via Docker stats
- ✅ Container auto-restart on OOM

---

## 9. Lessons Learned Template (Post-Migration)

### What Went Well
- TBD after Phase 4 completion

### What Could Be Improved
- TBD after Phase 4 completion

### Unexpected Issues
- TBD after Phase 4 completion

### Recommendations for Future Migrations
- TBD after Phase 4 completion

---

## 10. Approval & Sign-Off

**Strategy Author:** AI Coding Agent (GitHub Copilot)  
**Strategy Date:** January 2, 2026  
**Review Date:** Post-Phase 1 (estimated January 4, 2026)  

**Approved By:** ___________________________  
**Date:** ___________________________

---

**End of Dual-Write Strategy Document**
