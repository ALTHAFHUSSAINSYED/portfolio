docker ps 
# Portfolio Project - AI Coding Agent Instructions

**Last Updated:** January 3, 2026  
**Version:** 2.1  
**Status:** Production

## Project Overview
This is an AI-powered portfolio and blogging platform with automated blog generation (4-agent system) and an interactive chatbot (3-tier fallback model system).

### Technology Stack
- **Backend:** Python 3.11 (FastAPI + Uvicorn) with MongoDB Atlas, ChromaDB Cloud, AWS S3
- **Frontend:** React 18 with Shadcn/UI, React Router v6, Context API
- **AI Services:** 
  - **Chatbot:** OpenRouter API (Mistral 7B primary, Llama 3.2 fallback, Gemini emergency)
  - **Auto-Blogger:** OpenRouter API (4-agent system: Mistral Small, DeepSeek R1, Llama 405B, Gemma 2)
  - **Embeddings:** Google Gemini text-embedding-004
- **Search:** Serper.dev API (Google Search API wrapper)
- **Deployment:** AWS EC2 t2.large (backend Docker), AWS Amplify (frontend CDN)
- **Storage:** AWS S3 (blogs), MongoDB Atlas (portfolio data), ChromaDB Cloud (vector embeddings)

## Architecture & Data Flows

### High-Level Architecture
```
User Browser
    ↓
AWS Amplify (Frontend CDN) ←→ AWS S3 (Blog Storage)
    ↓
EC2 Instance (t2.large) → Docker Container (FastAPI App)
    ↓
├── ChromaDB Cloud (Vector Embeddings)
├── MongoDB Atlas (Portfolio Data)
├── AWS S3 (Blog Posts + Index)
├── OpenRouter API (LLM Models)
├── Google Gemini API (Embeddings)
└── SERPER API (Web Search)
```

### Backend Architecture (`backend/server.py`)
FastAPI app with lifespan context manager that:
1. **Auto-Blogger Scheduler:** APScheduler with CronTrigger for daily blog generation (7:00 AM IST)
2. **Chatbot System:** 3-tier fallback model system with rate limiting (10 req/min)
3. **CORS:** Explicit origin list from `CORS_ORIGINS` env var
4. **API Router:** All endpoints registered with `/api` prefix

**Core Active Files (25):**

**API Layer (7):**
1. `server.py` - Main FastAPI app, endpoints, health checks
2. `chatbot_provider.py` - Chatbot state machine & 4-tier LLM fallback logic
3. `ai_service.py` - LLM integration (Gemini embeddings + OpenRouter)
4. `cache_manager.py` - Response caching (chatbot)
5. `rate_limiter.py` - Rate limiting (10 req/min per IP)
6. `notification_service.py` - Email notifications via Resend API
7. `middleware/response_sanitizer.py` - Strip apology phrases from responses

**Auto-Blogger System (13):**
8. `auto_blogger/scheduler.py` - Cron scheduler (7:00 AM daily, category rotation)
9. `auto_blogger/writer.py` - 4-agent blog generation orchestrator (outliner + drafter)
10. `auto_blogger/critic.py` - Quality validation (score ≥90 required)
11. `auto_blogger/publisher.py` - S3 upload + ChromaDB embedding
12. `auto_blogger/researcher.py` - SERPER API web research
13. `auto_blogger/job_state.py` - Resumable job management (MongoDB)
14. `auto_blogger/logger_utils.py` - Structured logging system
15. `auto_blogger/notifier.py` - Email success/failure notifications
16. `auto_blogger/cleanup.py` - Old job cleanup (>7 days)
17. `auto_blogger/watchdog.py` - Process health monitoring
18. `auto_blogger/worker.py` - Background task worker (orchestrates agents + extracts metadata)
19. `auto_blogger/models/model_config.py` - Agent model definitions
20. `auto_blogger/models/model_benchmarker.py` - Model performance testing

**Utilities (5):**
21. `populate_vector_db.py` - Sync portfolio data to ChromaDB (Gemini embeddings)
22. `verify_chroma_state.py` - Verify ChromaDB state
23. `rebuild_s3_index.py` - Rebuild blog index.json from S3 posts
24. `fix_todays_blog.py` - Quick blog patching tool
25. `fetch_free_models.py` - Discover free OpenRouter models

### Data Storage
- **MongoDB (Motor):** Async `motor.motor_asyncio.AsyncIOMotorClient` for blogs/projects. Use `await db.collection.find()` patterns.
- **ChromaDB (Cloud):** `chromadb.CloudClient` for vector search with Gemini embeddings. **MIGRATION COMPLETE (Jan 3, 2026):** Now uses single `portfolio_master` collection with category-based filtering. Legacy collections (portfolio, Projects_data, Blogs_data) deleted.
- **AWS S3:** Blog storage bucket `althaf-blogs-storage` with JSON posts + index.json.
- **Cloudinary:** Image hosting configured in `server.py` with `cloudinary.uploader.upload()`.

### Frontend (`frontend/src/`)
- **Routing:** React Router v6 with `Outlet`, `ScrollRestoration`, programmatic navigation via `location.state.scrollTo`
- **UI:** Shadcn/Radix components in `components/ui/` (46 files), custom `Chatbot` component
- **API Client:** Axios calls to `REACT_APP_BACKEND_URL` (set in Amplify env vars)
- **Build:** Managed by `amplify.yml` (monorepo format: `appRoot: frontend`, `yarn install --ignore-engines`, output to `build/`)
- **Deployment:** AWS Amplify (auto-deploy on push to `main` when frontend changes detected)

## Critical Workflows

### Running Locally
**Backend:**
```bash
cd backend
# Ensure .env has GEMINI_API_KEY, MONGO_URL, SERPER_API_KEY, CHATBOT_NEW_KEY, BLOG_KEY
uvicorn server:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm start  # Runs on localhost:3000
```

### Chatbot System (4-Tier Fallback)
**Architecture:**
- **Tier 1 (Primary):** `mistralai/mistral-7b-instruct:free` via OpenRouter (`CHATBOT_NEW_KEY`)
- **Tier 2 (OpenAI Fallback):** `openai/gpt-oss-20b:free` via OpenRouter (`CHATBOT_NEW_KEY`)
- **Tier 3 (Gemini Chain):** `gemini-2.5-flash` → `gemini-2.0-flash-exp` → `gemma-3-12b-it` via Google AI (`GEMINI_API_KEY`)
- **Tier 4 (Last Resort):** `meta-llama/llama-3.2-3b-instruct` via Hugging Face Gradio (`CHATBOT` token)

**State Machine:**
```python
def detect_conversation_state(text: str) -> str:
    # States: GREETING, EXIT, SILENT, ABUSE, AMBIGUOUS, INFO
    # INFO state triggers RAG pipeline (ChromaDB query → LLM generation)
```

**Rate Limiting:** 10 requests/minute per IP (enforced by `rate_limiter.py`)

### Blog Generation System (4-Agent Pipeline)
**Daily Schedule:** 7:00 AM IST (APScheduler CronTrigger)
**Category Rotation:** DevOps → Cloud Computing → Cybersecurity → AI and ML → Low-Code/No-Code → Software Development
**IMPORTANT:** Category names use spaces/slashes (not underscores) to match frontend filter: "Cloud Computing", "AI and ML", "Low-Code/No-Code"

**Agent System:**
1. **Researcher** (`researcher.py`): SERPER API web research → trending topics
2. **Writer** (`writer.py`): `mistralai/mistral-small-3.1-24b-instruct:free` → generate outline + sections
3. **Critic** (`critic.py`): `deepseek/deepseek-r1-0528:free` → quality validation (score ≥90)
4. **Publisher** (`publisher.py`): S3 upload + ChromaDB embedding (portfolio_master only) + email notification

**Pipeline:**
```
1. Research (SERPER) → 2. Outline (Mistral Small) → 3. Draft Sections (Mistral Small)
   ↓
4. Quality Check (DeepSeek R1) → Score ≥90? → 5. Publish (S3 + ChromaDB)
   ↓ (if failed)
Reject blog + log failure
```

**Metadata Extraction Flow:**
- `writer.py` returns dict: `{"title": "...", "summary": "...", "content": "...", "category": "..."}`
- `worker.py` extracts title/summary from dict before passing to publisher
- **CRITICAL:** Never use category name as title (e.g., "Cloud_Computing" → actual blog title)
- Validation rejects outlines with generic "Technical Deep Dive" titles

**Job Management:**
- Resumable jobs with `job_state.py` (stores outline, sections, metadata)
- Logs in `/app/backend/logs/auto_blogger/{job_id}/`
- Cleanup after 7 days (`cleanup.py`)

### Testing Strategy
- **Test Files:** `backend/test_*.py` (pytest-based, no classes)
- **Run Tests:** `pytest backend/test_<name>.py` (e.g., `test_gemini_service.py`, `test_serper.py`)
- **Key Checks:**
  - `test_blog_generator.py`: End-to-end blog creation
  - `test_api.py`: FastAPI endpoint responses
  - `test_chatbot_connectivity.py`: AI agent query flow
  - `test_serper_utils.py`: Cache/rate limiter logic
  - `test_chatbot_fixes.py`: Chatbot 3-tier fallback system
  - `test_rag_pipeline.py`: RAG retrieval accuracy

### Deployment
- **Frontend:** Push to `main` → Amplify auto-deploys (no GitHub Action needed)
- **Backend:** GitHub Actions workflow deploys to EC2 on `backend/` changes. Manual restart: SSH to EC2 → `docker restart portfolio-backend`
- **Environment File:** `/home/ec2-user/portfolio/backend/.env.local` contains all production secrets (NEVER commit to repo)
- **Docker Container:** Runs on port 8000, memory limit 5GB, auto-restart enabled, uses `--env-file /home/ec2-user/portfolio/backend/.env.local`
- **Log Persistence:** Docker volume mounts `/home/ec2-user/portfolio-logs` to `/app/backend/logs`

### EC2 Instance Access
**SSH Connection:**
```bash
ssh -i "<path-to-pem-file>" ec2-user@<ec2-ip-address>
```

**Common Operations:**
- **Check Docker status:** `docker ps -a`
- **View logs:** `docker logs portfolio-backend --tail 100`
- **Restart container:** `docker restart portfolio-backend`
- **Access container shell:** `docker exec -it portfolio-backend bash`
- **Check disk usage:** `df -h`
- **Clean unused images:** `docker image prune -a`
- **Update .env.local:** `nano /home/ec2-user/portfolio/backend/.env.local` (then restart container)
- **Verify env loaded:** `docker exec portfolio-backend printenv | grep -E '(CHATBOT|BLOG_KEY|GEMINI)'`

**Important Notes:**
- PEM file must have correct permissions: `chmod 400 <pem-file>`
- Always backup `.env` before modifications
- Container logs are persisted in `/home/ec2-user/portfolio-logs`

## Project-Specific Conventions

### API Patterns
- **Endpoints:** Use `@api_router.<method>` decorators (not `@app.<method>` directly)
- **Models:** Define Pydantic models in `models.py` or inline (e.g., `ContactForm`, `Project`)
- **Error Handling:** Raise `HTTPException` with appropriate `status_code` (from `status` module)
- **CORS:** Origins list must be explicit (no `*`), loaded from `CORS_ORIGINS` env var

### AI Service Usage
```python
# Correct way to use OpenRouter for chatbot
from backend.chatbot_provider import ChatbotProvider

chatbot = ChatbotProvider()
response = await chatbot.get_response(message="What are your projects?")
# Returns: {"response": "...", "intent": "projects", "cached": false}

# For auto-blogger (4-agent system)
from backend.auto_blogger.writer import BlogWriter

writer = BlogWriter()
blog = await writer.generate_blog(category="DevOps", research_data={...})
# Returns: {"title": "...", "content": "...", "metadata": {...}}

# For embeddings
import google.generativeai as genai

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
embedding = genai.embed_content(
    model='models/text-embedding-004',
    content=text,
    task_type="retrieval_query"
)['embedding']
```

**Important Notes:**
- **Chatbot:** Uses `CHATBOT_NEW_KEY` (OpenRouter) for Tier 1 (Mistral 7B) + Tier 2 (OpenAI gpt-oss-20b)
- **Chatbot Gemini:** Uses `GEMINI_API_KEY` (Google AI) for Tier 3 (gemini-2.5-flash, gemini-2.0-flash-exp, gemma-3-12b-it)
- **Chatbot HF:** Uses `CHATBOT` (HuggingFace) for Tier 4 last resort (Llama 3.2 3B)
- **Auto-Blogger:** Uses `BLOG_KEY` (OpenRouter) for Mistral Small, DeepSeek R1, Llama 405B
- **Embeddings:** Uses `GEMINI_API_KEY` (Google) for text-embedding-004
- **Fallback:** 4-tier system ensures 99.9% uptime (Mistral → OpenAI → Gemini Chain → HF Gradio)

### Search & Caching
```python
# Chatbot caching (in-memory)
from backend.cache_manager import cache_manager

cached = cache_manager.get(query)
if cached:
    return cached

response = await chatbot.get_response(query)
cache_manager.set(query, response, ttl=3600)  # 1 hour

# SERPER API research (auto-blogger)
from backend.auto_blogger.researcher import BlogResearcher

researcher = BlogResearcher()
research_data = researcher.analyze_trends(category="DevOps")
# Returns: {"trending_topics": [...], "recent_advances": [...]}
```

**Key Points:**
- **Chatbot Cache:** In-memory, 1-hour TTL, per-user isolation
- **SERPER Usage:** Only for auto-blogger research (daily), ~30 searches/month
- **Rate Limits:** 10 req/min for chatbot (enforced by `rate_limiter.py`)
- **No DuckDuckGo:** Removed fallback, SERPER is primary for research

### Security Patterns
- **Input Sanitization:** Always use `sanitize_html()` for user-generated content before DB storage
- **Middleware Order:** SecurityHeadersMiddleware → CORSMiddleware (order matters!)
- **Guardrails:** `guardrails.py` defines blocked topics, greeting patterns for chatbot
- **Rate Limiting:** 10 requests/minute per IP for chatbot (enforced by `slowapi`)
- **Response Sanitizer:** Strips apology phrases ("I apologize", "I'm sorry") via middleware


### Error Handling, Logging & Commit Policy
```python
logger = logging.getLogger('PortfolioBackend')  # or 'AlluAgent' for agent service
try:
    # risky operation
except Exception as e:
    logger.error(f"Operation failed: {e}")
    # Send notification for critical failures
    await notification_service.send_blog_notification(False, None, str(e))
```
- **Log Files:** `agent.log` (for agent service), stdout (for server logs)
- **Structured Logging:** Use formatted strings with context (timestamps, function names)

### Commit & Push Policy
- All error fixes, code changes, and corrections must be committed and pushed directly to the remote repository immediately after validation.
- Do not leave local changes uncommitted; always ensure the remote repository is up to date after any fix.
- This applies to syntax errors, logic errors, and any other corrections made during development or troubleshooting.

## Integration Points & External Dependencies

### Required Environment Variables
```bash
# AI Services
GEMINI_API_KEY="<your-gemini-api-key>"  # Primary embeddings from Google AI Studio
CHATBOT_NEW_KEY="<your-openrouter-key>"  # OpenRouter for chatbot (Mistral 7B)
BLOG_KEY="<your-openrouter-key>"  # OpenRouter for auto-blogger (4 agents)
CHATBOT="<your-huggingface-token>"  # HuggingFace Gradio fallback
GEMINI_BLOG_API_KEY="<your-gemini-api-key>"  # Backup embeddings

# Search APIs
SERPER_API_KEY="<your-serper-key>"  # Primary (Google Search)

# Databases
MONGO_URL="<your-mongodb-connection-string>"
DB_NAME="portfolioDB"
CHROMA_API_KEY="<your-chromadb-key>"
CHROMA_TENANT="<your-chromadb-tenant>"
CHROMA_DATABASE="Development"

# Email & Notifications
RESEND_KEY="<your-resend-key>"
TO_EMAIL="<your-email>"

# Image Hosting
CLOUDINARY_CLOUD_NAME="<your-cloudinary-name>"
CLOUDINARY_API_KEY="<your-cloudinary-key>"
CLOUDINARY_API_SECRET="<your-cloudinary-secret>"

# Security & Logging
CORS_ORIGINS="http://localhost:3000,https://www.althafportfolio.site,https://althafportfolio.site"
LOG_LEVEL="INFO"
```

### Key File References
- **Main Entry:** [backend/server.py](backend/server.py) (FastAPI app, scheduler setup)
- **Chatbot Logic:** [backend/chatbot_provider.py](backend/chatbot_provider.py) (state machine, 3-tier fallback)
- **AI Service:** [backend/ai_service.py](backend/ai_service.py) (OpenRouter + Gemini embeddings)
- **Cache Manager:** [backend/cache_manager.py](backend/cache_manager.py) (in-memory caching)
- **Rate Limiter:** [backend/rate_limiter.py](backend/rate_limiter.py) (10 req/min enforcement)
- **Notifications:** [backend/notification_service.py](backend/notification_service.py) (Resend email)
- **Auto-Blogger:** [backend/auto_blogger/](backend/auto_blogger/) (4-agent system)
- **Frontend Router:** [frontend/src/App.js](frontend/src/App.js) (React Router setup)

### Common Pitfalls
1. **CORS Errors:** Ensure `CORS_ORIGINS` includes the exact frontend URL (no trailing slash mismatches)
2. **ChromaDB Quotas:** Monitor `query_tracking_log.json` - free tier has 1000 documents limit
3. **Serper.dev Credits:** Use SERPER only for auto-blogger (daily), ~30 searches/month budget
4. **Motor Async:** Always `await` MongoDB operations (`await db.collection.find_one()`)
5. **Scheduler Conflicts:** Only one `APScheduler` instance should run (lifespan manager ensures this)
6. **Import Errors:** Use `from backend import <module>` (not relative imports) due to package structure
7. **API Keys:** Separate keys for chatbot (`CHATBOT_NEW_KEY`) and auto-blogger (`BLOG_KEY`)
