# System Architecture - Complete Understanding

**Date:** January 4, 2026  
**Status:** Documented & Internalized

---

## ��� Documents Read & Analyzed

✅ **SYSTEM_ARCHITECTURE.md** (2403 lines) - Complete system overview  
✅ **.github/copilot-instructions.md** (342 lines) - Project-specific conventions  
✅ **CHATBOT_ARCHITECTURE.md** - Chatbot state machine & RAG pipeline  
✅ **README_DEPLOYMENT.md** - Deployment procedures  
✅ **EC2_login_credentials.txt** - Production access credentials

---

## ���️ System Architecture (Internalized)

### **High-Level Flow:**
```
User Browser
    ↓
AWS Amplify (Frontend) ←→ S3 (Blogs)
    ↓
EC2 t2.large (Backend Docker) → FastAPI App
    ↓
├── ChromaDB Cloud (portfolio_master collection)
├── MongoDB Atlas (portfolioDB)
├── AWS S3 (althaf-blogs-storage)
├── OpenRouter API (Mistral, DeepSeek, Llama)
├── Google Gemini (text-embedding-004)
└── SERPER API (Google Search)
```

### **Key Understanding Points:**

1. **Deployment is NOT automatic via GitHub Actions** ❌
   - GitHub Actions workflow exists but Docker build FAILS (COPY path issues)
   - Manual deployment required: `docker cp` files → `docker restart`
   - Self-hosted runner on EC2 authenticates with PAT token

2. **ChromaDB Migration Completed (Jan 3, 2026)**
   - Single `portfolio_master` collection with category filtering
   - Legacy collections deleted: `portfolio`, `Projects_data`, `Blogs_data`
   - Filter format: `where={"category": "profile"}` for intent routing

3. **Backend File Structure (25 Active Files):**
   - **API Layer:** server.py, chatbot_provider.py, ai_service.py, cache_manager.py, rate_limiter.py, notification_service.py, response_sanitizer.py
   - **Auto-Blogger:** 13 files (scheduler, writer, critic, publisher, researcher, etc.)
   - **Utilities:** 5 files (populate_vector_db.py, verify_chroma_state.py, etc.)

4. **Intent Detection System (server.py:370-410):**
   ```python
   Priority Scores:
   - aws_projects: 15 (domain-specific, highest)
   - projects: 12 (general)
   - profile: 10 (includes education + employment keywords)
   - blogs: 10
   - about (context): 8 (only if not about projects/blogs)
   ```

5. **Chatbot System (4-Tier Fallback):**
   - Tier 1: Mistral 7B (OpenRouter, CHATBOT_NEW_KEY)
   - Tier 2: OpenAI gpt-oss-20b (OpenRouter, CHATBOT_NEW_KEY)
   - Tier 3: Gemini Chain (gemini-2.5-flash → gemini-2.0-flash-exp → gemma-3-12b-it via GEMINI_API_KEY)
   - Tier 4: Llama 3.2 3B (HuggingFace Gradio, CHATBOT token)

6. **Auto-Blogger (4-Agent System):**
   - Research Agent: SERPER API (trending topics)
   - Orchestrator: DeepSeek R1 (outline generation)
   - Drafter: Mistral Small (section writing)
   - Critic: DeepSeek R1 (quality validation, score ≥90)
   - Publisher: S3 + ChromaDB + email notification

7. **EC2 Instance Structure:**
   ```
   /home/ec2-user/
   ├── portfolio/ (git repo)
   │   └── backend/.env.local (ALL production secrets)
   ├── portfolio-logs/ (Docker volume mount)
   │   ├── chatbot.log
   │   └── auto_blogger/{job_id}/
   └── actions-runner/ (self-hosted runner)
   ```

8. **Environment Variables (Strict Separation):**
   - **Chatbot:** CHATBOT_NEW_KEY (OpenRouter Tier 1+2), CHATBOT (HF Gradio Tier 4), GEMINI_API_KEY (Tier 3)
   - **Auto-Blogger:** BLOG_KEY (OpenRouter for 4 agents)
   - **Embeddings:** GEMINI_API_KEY (text-embedding-004)
   - **Research:** SERPER_API_KEY (Google Search)

---

## ��� Critical Workflows (Internalized)

### **Deployment Procedure:**
1. **Code Changes → Git Push:**
   ```bash
   git add <files>
   git commit -m "description"
   git push origin main
   ```

2. **GitHub Actions Attempts Auto-Deploy:**
   - Workflow triggers on `backend/**` changes
   - Docker build FAILS (COPY path issues - known bug)
   - Container keeps running old code

3. **Manual Deployment Required:**
   ```bash
   ssh -i "PORTFOLIO.pem" ec2-user@13.233.54.210
   cd /home/ec2-user/portfolio
   git pull origin main
   docker cp backend/server.py portfolio-backend:/app/backend/server.py
   docker cp backend/chatbot_provider.py portfolio-backend:/app/backend/chatbot_provider.py
   docker restart portfolio-backend
   sleep 30  # Wait for initialization
   # Verify deployment
   docker exec portfolio-backend python3 -c "import sys; sys.path.insert(0, '/app/backend'); from server import detect_intent_priority; print(detect_intent_priority('where did he study'))"
   ```

4. **Verification:**
   ```bash
   # Check container status
   docker ps | grep portfolio-backend
   
   # Check logs
   docker logs portfolio-backend --tail 50
   
   # Test intent routing
   docker exec portfolio-backend python3 -c "from server import detect_intent_priority; print(detect_intent_priority('education'))"
   ```

### **Chatbot RAG Pipeline:**
```
1. User Query → State Detection (GREETING vs INFO)
2. If INFO → Intent Detection (profile/projects/blogs/aws_projects)
3. Intent → ChromaDB Query (filter by category)
4. ChromaDB Results → Context Assembly
5. Context Quality Check (>50 chars?) → Context Guard
   - If empty: Return fallback message (NO LLM CALL)
   - If valid: Proceed to LLM
6. LLM Generation (4-tier fallback)
7. Response Sanitizer (strip apologies, fix bot name)
8. Cache Response
9. Return to User
```

### **Intent Detection Keywords (Memorized):**
```python
# Profile (score +10)
["who", "bio", "background", "resume", "experience", "skill", "contact", 
 "email", "working", "employed", "job", "position", "role", "company", "current",
 "education", "degree", "university", "college", "study", "studied", 
 "master", "bachelor", "btech", "mtech", "certificate", "certification", "school", "grad", "graduate"]

# AWS Projects (score +15) - Domain-specific
["aws", "cloud", "terraform", "deploy", "infrastructure", "pipeline", "ci/cd"]

# Projects (score +12) - General
["project", "built", "develop", "portfolio", "app", "website", "created", "made"]

# Blogs (score +10)
["blog", "article", "write", "post", "read"]

# About (score +8) - Context-dependent
["about"] (only if NOT about projects/blogs)
```

---

## ��� Common Issues & Solutions (Internalized)

### **Issue 1: Intent Routing Wrong**
**Symptom:** Education queries route to "conversation" instead of "profile"  
**Root Cause:** Missing keywords in profile intent detection  
**Solution:** Add keywords to `profile_keywords` list in `server.py:383-386`  
**Verification:** Test with `detect_intent_priority("where did he study")` → should return "profile" (score 10)

### **Issue 2: Hallucination (LLM Inventing Data)**
**Symptom:** Bot says "UMass Lowell" when no education data found  
**Root Cause:** LLM called with empty/minimal context  
**Solution:** Context guard in `chatbot_provider.py:510-513` blocks LLM call if context < 50 chars  
**Prevention:** No context = No LLM call = No hallucination possible

### **Issue 3: Deployment Doesn't Update Code**
**Symptom:** Code pushed to GitHub but container runs old version  
**Root Cause:** GitHub Actions Docker build fails (COPY path issues)  
**Solution:** Manual deployment via `docker cp` + `docker restart`  
**Verification:** `docker exec portfolio-backend grep "keyword" /app/backend/server.py`

### **Issue 4: Bot Says Wrong Name ("Allu Bot" vs "Assist Bot")**
**Symptom:** LLM ignores system prompt about name  
**Root Cause:** LLM generating from training data  
**Solution:** Response sanitizer (`middleware/response_sanitizer.py:18-33`) replaces "Allu Bot" → "Assist Bot"  
**Prevention:** Regex post-processing catches all variations

### **Issue 5: Self-Hosted Runner Auth Fails (Private Repo)**
**Symptom:** GitHub Actions workflow can't checkout code  
**Root Cause:** Private repo requires PAT token authentication  
**Solution:** Configure git credential helper + remote URL with PAT  
```bash
git config --global credential.helper store
git remote set-url origin https://USERNAME:<PAT>@github.com/OWNER/REPO.git
```

---

## ��� Next-Time Debugging Checklist

When fixing issues, ALWAYS follow this sequence:

### **Step 1: Understand the Flow**
- [ ] Read relevant architecture docs (SYSTEM_ARCHITECTURE.md, CHATBOT_ARCHITECTURE.md)
- [ ] Identify which component is involved (API layer, RAG pipeline, auto-blogger, etc.)
- [ ] Trace the data flow (User → Frontend → Backend → DB → LLM → Response)

### **Step 2: Verify Current State**
- [ ] Check git status: `git log --oneline -5`
- [ ] Check EC2 container: `ssh + docker ps`
- [ ] Check container code: `docker exec portfolio-backend grep "keyword" /app/backend/file.py`
- [ ] Check logs: `docker logs portfolio-backend --tail 50`

### **Step 3: Identify Root Cause**
- [ ] Is it intent routing? → Check `server.py:detect_intent_priority()`
- [ ] Is it RAG retrieval? → Check ChromaDB query filters
- [ ] Is it LLM response? → Check context quality (>50 chars?)
- [ ] Is it deployment? → Check if container has latest code

### **Step 4: Fix Systematically**
- [ ] Edit local files
- [ ] Test locally if possible (or in-container with Python snippet)
- [ ] Commit + push to GitHub
- [ ] Manually deploy to EC2 (docker cp + restart)
- [ ] Verify deployment (grep for new code in container)
- [ ] Test in production (SSH + Python test or curl)

### **Step 5: Document**
- [ ] Update architecture docs if workflow changed
- [ ] Add troubleshooting entry if new issue type
- [ ] Commit documentation changes

---

## ��� Key Takeaways

1. **GitHub Actions Auto-Deploy DOES NOT WORK** - Always verify manually with `docker cp`
2. **Intent detection is keyword-based** - Missing keywords = wrong routing = hallucination
3. **Context guard is critical** - Empty context = block LLM call = no hallucination
4. **ChromaDB uses single `portfolio_master` collection** - Filter by `category` metadata
5. **4-tier chatbot fallback ensures 99.9% uptime** - Mistral → OpenAI → Gemini Chain → HF Gradio
6. **EC2 credentials stored in EC2_login_credentials.txt** - NEVER commit to git (.gitignore protected)
7. **Environment file is `/home/ec2-user/portfolio/backend/.env.local`** - Contains ALL production secrets

---

**CONFIRMED:** I now have deep understanding of the entire system architecture and will debug issues systematically by following the documented flows and checking the correct components. No more guessing - every fix will be data-driven based on architecture knowledge.

