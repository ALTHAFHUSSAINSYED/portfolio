# Task 19: 48-Hour Validation Monitoring

**Start Time:** January 2, 2026 20:10 IST  
**End Time:** January 4, 2026 20:10 IST  
**Status:** 🟢 IN PROGRESS

---

## Quick Status Check

```bash
# Run this command to get current status
ssh -i "PORTFOLIO.pem" ec2-user@13.233.54.210 "
echo '=== CONTAINER STATUS ==='
docker ps --filter name=portfolio-backend --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
echo ''
echo '=== RESOURCE USAGE ==='
docker stats portfolio-backend --no-stream --format 'table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}'
echo ''
echo '=== RECENT ERRORS (Last 50 lines) ==='
docker logs portfolio-backend 2>&1 | tail -50 | grep -i error | wc -l
echo 'errors found'
echo ''
echo '=== CHROMADB MODE ==='
docker logs portfolio-backend 2>&1 | grep 'ChromaDB Mode' | tail -1
"
```

---

## Initial Validation Results (Jan 2, 20:10 IST)

### ✅ Test 1: Skills Query (Profile Category)
**Query:** "What are your skills?"  
**Result:** ✅ SUCCESS  
**Response:** Comprehensive skills list (580 chars)  
**Provider:** Mistral 7B Instruct (OpenRouter Tier 1)  
**Collection:** portfolio_master (category='profile')

### ✅ Test 2: AWS Projects Query (Project Category)
**Query:** "Tell me about your AWS projects"  
**Result:** ✅ SUCCESS  
**Response:** Detailed AWS project descriptions (850+ chars)  
**Provider:** Mistral 7B Instruct (OpenRouter Tier 1)  
**Collection:** portfolio_master (category='project')

### ⚠️ Test 3: Blog Query (Blog Category)
**Query:** "What are your recent blogs about?"  
**Result:** ⚠️ INCOMPLETE  
**Response:** "I haven't written any recent blogs"  
**Issue:** May need to verify blog data in portfolio_master  
**Action:** Check blog count and metadata

### ✅ Container Health
- **CPU Usage:** 0.34%
- **Memory Usage:** 184.3 MiB / 1.868 GiB (9.63%)
- **Status:** Healthy, running smoothly
- **Uptime:** Stable since restart

### ✅ Log Analysis
- **Critical Errors:** 0
- **Warnings:** 1 (OpenRouter Tier 2 rate limit - expected behavior)
- **404 Errors:** 0
- **Collection Not Found:** 0

---

## Monitoring Schedule

### Hour 0-1 (Jan 2, 20:10 - 21:10) - INTENSIVE
**Check every 10 minutes**

**Commands:**
```bash
# Quick error check
ssh -i "PORTFOLIO.pem" ec2-user@13.233.54.210 "docker logs portfolio-backend 2>&1 | tail -100 | grep -i error"

# Test chatbot
curl -X POST https://www.althafportfolio.site/api/ask-all-u-bot \
  -H "Content-Type: application/json" \
  -d '{"message": "What certifications do you have?", "session_id": "monitor-'$(date +%s)'"}'
```

**Checklist:**
- [ ] 20:20 - Error check ✓
- [ ] 20:30 - Error check + Chatbot test
- [ ] 20:40 - Error check
- [ ] 20:50 - Error check + Chatbot test
- [ ] 21:00 - Error check + Container stats

---

### Hour 1-6 (Jan 2, 21:10 - Jan 3, 02:10) - REGULAR
**Check every 30 minutes**

**Commands:**
```bash
# Comprehensive check
ssh -i "PORTFOLIO.pem" ec2-user@13.233.54.210 "
docker logs portfolio-backend 2>&1 | tail -200 | grep -iE '(error|chromadb|portfolio_master)' | tail -20
docker stats portfolio-backend --no-stream
"
```

**Checklist:**
- [ ] 21:30 - Full check
- [ ] 22:00 - Full check
- [ ] 22:30 - Full check
- [ ] 23:00 - Full check + Test chatbot
- [ ] 23:30 - Full check
- [ ] 00:00 - Full check + Memory check
- [ ] 00:30 - Full check
- [ ] 01:00 - Full check
- [ ] 01:30 - Full check
- [ ] 02:00 - Full check + End of Hour 6

---

### Hour 6-24 (Jan 3, 02:10 - 20:10) - MODERATE
**Check every 2 hours**

**Commands:**
```bash
# Morning check
ssh -i "PORTFOLIO.pem" ec2-user@13.233.54.210 "
echo 'Errors in last 2 hours:'
docker logs portfolio-backend --since 2h 2>&1 | grep -i error | wc -l
echo ''
echo 'Container uptime:'
docker ps --filter name=portfolio-backend --format '{{.Status}}'
echo ''
echo 'Resource usage:'
docker stats portfolio-backend --no-stream --format 'CPU: {{.CPUPerc}} | Memory: {{.MemUsage}}'
"
```

**Checklist:**
- [ ] 04:00 - Morning check
- [ ] 06:00 - Morning check
- [ ] 08:00 - Morning check + Test chatbot
- [ ] 10:00 - Morning check (Auto-blogger scheduled at 10 AM)
- [ ] 12:00 - Afternoon check
- [ ] 14:00 - Afternoon check
- [ ] 16:00 - Afternoon check + Test chatbot
- [ ] 18:00 - Evening check
- [ ] 20:00 - Evening check + Day 1 summary

---

### Hour 24-48 (Jan 3, 20:10 - Jan 4, 20:10) - LIGHT
**Check every 4 hours**

**Commands:**
```bash
# Extended period check
ssh -i "PORTFOLIO.pem" ec2-user@13.233.54.210 "
echo '=== Last 4 Hours Summary ==='
echo 'Total errors:'
docker logs portfolio-backend --since 4h 2>&1 | grep -i error | wc -l
echo ''
echo 'ChromaDB queries:'
docker logs portfolio-backend --since 4h 2>&1 | grep 'portfolio_master' | wc -l
echo ''
echo 'Chatbot requests:'
docker logs portfolio-backend --since 4h 2>&1 | grep 'ask-all-u-bot' | wc -l
"
```

**Checklist:**
- [ ] Jan 4, 00:00 - Midnight check
- [ ] Jan 4, 04:00 - Late night check
- [ ] Jan 4, 08:00 - Morning check
- [ ] Jan 4, 12:00 - Noon check
- [ ] Jan 4, 16:00 - Afternoon check
- [ ] Jan 4, 20:00 - **FINAL VALIDATION** ✓

---

## Comprehensive Test Queries

### Profile Category (10 queries)
```bash
# Test these via browser or API
1. "What are your skills?"
2. "Tell me about your experience"
3. "What certifications do you have?"
4. "What is your educational background?"
5. "What soft skills do you have?"
6. "Tell me about your DevOps experience"
7. "What programming languages do you know?"
8. "Describe your leadership experience"
9. "What are your technical strengths?"
10. "Tell me about your career summary"
```

### Project Category (5 queries)
```bash
11. "What are your AWS projects?"
12. "Tell me about your Terraform projects"
13. "What Kubernetes projects have you worked on?"
14. "Show me your CI/CD projects"
15. "What cloud projects have you completed?"
```

### Blog Category (5 queries)
```bash
16. "What are your recent blogs?"
17. "Tell me about your DevOps blogs"
18. "What have you written about AWS?"
19. "Show me your technical articles"
20. "What blog topics do you cover?"
```

### Mixed Queries (5 queries)
```bash
21. "Tell me about your skills and projects"
22. "What AWS experience and certifications do you have?"
23. "Show me everything about DevOps"
24. "What have you built with Kubernetes?"
25. "Tell me about your cloud expertise"
```

---

## Success Criteria Checklist

### Critical (Must Pass)
- [ ] Zero "collection not found" errors in 48 hours
- [ ] Zero critical ChromaDB errors
- [ ] Container uptime = 48 hours (no crashes)
- [ ] Profile queries return accurate results
- [ ] Project queries return accurate results
- [ ] Per-session rate limiting working (12 RPM)

### Important (Should Pass)
- [ ] Blog queries return results (if blog data exists)
- [ ] Memory usage stable (<50% of 5GB limit)
- [ ] No timeout errors
- [ ] OpenRouter Tier 1 (Mistral 7B) handling 90%+ requests
- [ ] Response times acceptable (300-500ms)

### Optional (Nice to Have)
- [ ] OpenRouter TPM usage: 48K-72K TPM range
- [ ] Auto-blogger runs successfully (Jan 3, 7 AM)
- [ ] No duplicate embedding warnings
- [ ] Cache hit rate >30%

---

## Alert Thresholds

| Severity | Condition | Action |
|----------|-----------|--------|
| 🟢 HEALTHY | 0-2 errors/hour | Continue monitoring |
| 🟡 WARNING | 3-5 errors/hour | Investigate logs, increase check frequency |
| 🟠 ELEVATED | 6-10 errors/hour | Check container health, test chatbot manually |
| 🔴 CRITICAL | >10 errors/hour | **ROLLBACK IMMEDIATELY** |

### Rollback Command (Emergency)
```bash
ssh -i "PORTFOLIO.pem" ec2-user@13.233.54.210 "
nano /home/ec2-user/portfolio/backend/.env.local
# Change: USE_LEGACY_COLLECTIONS=true
docker restart portfolio-backend
docker logs portfolio-backend --tail 50 | grep 'LEGACY'
# Should show: 'ChromaDB Mode: LEGACY (3 separate collections)'
"
```

---

## Known Issues (Non-Critical)

### 1. OpenRouter Tier 2 Rate Limit Warning
**Message:** `OpenRouter failed (openai/gpt-oss-20b:free): 429`  
**Impact:** Low - Tier 1 (Mistral 7B) handles primary traffic  
**Action:** None required - expected fallback behavior

### 2. Blog Query Incomplete Response
**Message:** "I haven't written any recent blogs"  
**Impact:** Medium - May indicate blog data retrieval issue  
**Action:** Verify blog count in portfolio_master collection  
**Status:** Investigating

---

## Progress Log

### January 2, 2026 20:10 IST - Monitoring Started
- ✅ Container restarted with .env.local
- ✅ Initial tests passed (2/3 successful)
- ✅ Mistral 7B Tier 1 working
- ✅ portfolio_master collection active
- ⚠️ Blog query needs investigation
- 📊 Memory: 184MB / 1.8GB (9.63%)
- 📊 CPU: 0.34%

### January 2, 2026 20:30 IST - Hour 0 Check
- [ ] Pending

### January 2, 2026 21:00 IST - Hour 1 Check
- [ ] Pending

---

## Monitoring Commands Reference

### Quick Health Check
```bash
ssh -i "PORTFOLIO.pem" ec2-user@13.233.54.210 "docker ps && docker stats portfolio-backend --no-stream"
```

### Error Analysis
```bash
ssh -i "PORTFOLIO.pem" ec2-user@13.233.54.210 "docker logs portfolio-backend 2>&1 | grep -i error | tail -50"
```

### ChromaDB Activity
```bash
ssh -i "PORTFOLIO.pem" ec2-user@13.233.54.210 "docker logs portfolio-backend 2>&1 | grep 'portfolio_master' | tail -20"
```

### Chatbot Test (Local)
```bash
ssh -i "PORTFOLIO.pem" ec2-user@13.233.54.210 'curl -X POST http://localhost:8000/api/ask-all-u-bot -H "Content-Type: application/json" -d "{\"message\": \"Test query\", \"session_id\": \"monitor-test\"}"'
```

### Container Restart (If Needed)
```bash
ssh -i "PORTFOLIO.pem" ec2-user@13.233.54.210 "docker restart portfolio-backend && sleep 10 && docker logs portfolio-backend --tail 30"
```

---

## Next Actions After 48 Hours

If all success criteria pass:
1. Mark Task 19 as completed
2. Proceed to Task 20 (Auto-Blogger Dual-Write Validation)
3. Document findings in final report

If any critical issues found:
1. Execute rollback procedure
2. Investigate root cause
3. Fix issues and restart 48-hour validation

---

**Last Updated:** January 2, 2026 20:10 IST  
**Monitoring By:** GitHub Copilot Agent  
**Next Check:** January 2, 2026 20:30 IST
