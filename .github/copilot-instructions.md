# Portfolio Project - AI Coding Agent Instructions

## Project Overview
This is an AI-powered portfolio and blogging platform with automated blog generation and an interactive chatbot.
- **Backend:** Python (FastAPI) with MongoDB, ChromaDB, Motor async driver
- **Frontend:** React (Create React App) with Radix UI, Tailwind CSS
- **AI:** Google Gemini (primary) via `gemini_service`, OpenAI (fallback)
- **Search:** Serper.dev API (primary, cached), DuckDuckGo (fallback)
- **Deployment:** AWS EC2 (backend), AWS Amplify (frontend, auto-deploys on `main` push)

## Architecture & Data Flows

### Backend (`backend/server.py`)
FastAPI app with lifespan context manager that:
1. Starts `APScheduler` with `CronTrigger` for daily blog generation (1 AM UTC)
2. Initializes `agent_service` in daemon thread for background AI processing
3. Configures CORS with explicit origin list from `CORS_ORIGINS` env var (not `*`)
4. Registers `api_router` with `/api` prefix for all endpoints

**Key Service Layers:**
- **AI Generation:** `gemini_service.py` (`GeminiClient.ChatCompletions.create()`) mimics OpenAI interface
- **Agent Logic:** `agent_service.py` (`WebSearchEngine` class) orchestrates search → AI response pipeline
- **Search Optimization:** `search_utils.py` (`SearchCache`, `RateLimiter`, `QueryOptimizer`) caches results 24h, enforces rate limits
- **Security:** `security_utils.py` (`sanitize_html`, `SecurityHeadersMiddleware`) uses `bleach` for XSS prevention
- **Notifications:** `notification_service.py` sends email via Resend API on blog success/failure

### Data Storage
- **MongoDB (Motor):** Async `motor.motor_asyncio.AsyncIOMotorClient` for blogs/projects. Use `await db.collection.find()` patterns.
- **ChromaDB (Cloud):** `chromadb.CloudClient` for vector search. Monitor usage via `chromadb_monitor.py` (50 queries/day limit, 900MB storage cap).
- **Cloudinary:** Image hosting configured in `server.py` with `cloudinary.uploader.upload()`.

### Frontend (`frontend/src/`)
- **Routing:** React Router v7 with `Outlet`, `ScrollRestoration`, programmatic navigation via `location.state.scrollTo`
- **UI:** Shadcn/Radix components in `components/ui/`, custom `Chatbot` component
- **API Client:** Axios calls to `REACT_APP_BACKEND_URL` (set in Amplify env vars)
- **Build:** Managed by `amplify.yml` (`yarn install --ignore-engines`, output to `build/`)

## Critical Workflows

### Running Locally
**Backend:**
```bash
cd backend
# Ensure .env has GEMINI_API_KEY, MONGO_URL, SERPER_API_KEY
uvicorn server:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm start  # Runs on localhost:3000
```

### Blog Generation System
1. **Scheduled:** `APScheduler` calls `scheduled_blog_generation()` → `gemini_service.generate_blog_post(topic)`
2. **Manual:** POST `/trigger-blog-generation` (calls same function)
3. **Pipeline:** Generate content → Insert to MongoDB → Send email via `notification_service.send_blog_notification()`
4. **Logging:** Prints formatted success/failure boxes to stdout + writes to `agent.log`

### Testing Strategy
- **Test Files:** `backend/test_*.py` (pytest-based, no classes)
- **Run Tests:** `pytest backend/test_<name>.py` (e.g., `test_gemini_service.py`, `test_serper.py`)
- **Key Checks:**
  - `test_blog_generator.py`: End-to-end blog creation
  - `test_api.py`: FastAPI endpoint responses
  - `test_chatbot_connectivity.py`: AI agent query flow
  - `test_serper_utils.py`: Cache/rate limiter logic

### Deployment
- **Frontend:** Push to `main` → Amplify auto-deploys (no GitHub Action needed)
- **Backend:** GitHub Actions workflow deploys to EC2 on `backend/` changes. Manual restart: SSH to EC2 → `sudo systemctl restart portfolio-backend`
- **Environment Sync:** Update `.env` on EC2 for production secrets (NEVER commit `.env` to repo)

## Project-Specific Conventions

### API Patterns
- **Endpoints:** Use `@api_router.<method>` decorators (not `@app.<method>` directly)
- **Models:** Define Pydantic models in `models.py` or inline (e.g., `ContactForm`, `Project`)
- **Error Handling:** Raise `HTTPException` with appropriate `status_code` (from `status` module)
- **CORS:** Origins list must be explicit (no `*`), loaded from `CORS_ORIGINS` env var

### AI Service Usage
```python
# Correct way to use Gemini service
from backend.ai_service import gemini_service

response = gemini_service.chat.completions.create(
    model="gpt-4",  # Maps to gemini-pro-latest
    messages=[{"role": "user", "content": "..."}],
    temperature=0.7,
    max_tokens=2048
)
content = response.choices[0].message.content
```
- **Fallback:** If `gemini_service.is_available == False`, implement OpenAI fallback or graceful degradation
- **Safety:** Gemini configured with `BLOCK_MEDIUM_AND_ABOVE` for all harm categories

### Search & Caching
```python
from backend.search_utils import search_cache, rate_limiter

# Always check cache first
cached = search_cache.get(query)
if cached:
    return cached

# Rate limit check before API call
if not rate_limiter.allow_request():
    raise HTTPException(status_code=429, detail="Rate limit exceeded")

# Make API call and cache
results = serper_search(query)
search_cache.set(query, results)
```
- **Cache TTL:** 24 hours (configurable in `SearchCache.__init__`)
- **Rate Limits:** Track in `rate_limiter.request_timestamps` (default: max requests per time window)
- **Admin Tool:** Use `python backend/serper_admin.py --help` for cache management

### Security Patterns
- **Input Sanitization:** Always use `sanitize_html()` for user-generated content before DB storage
- **Middleware Order:** SecurityHeadersMiddleware → CORSMiddleware (order matters!)
- **Guardrails:** `guardrails.py` defines blocked topics, greeting patterns for chatbot

### Error Handling & Logging
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

## Integration Points & External Dependencies

### Required Environment Variables
```bash
# AI Services
GEMINI_API_KEY="<get from makersuite.google.com>"  # Primary
OPENAI_API_KEY="<optional fallback>"

# Search APIs
SERPER_API_KEY="<get from serper.dev>"  # Primary (paid)
NEWS_API_KEY="<optional for news>"

# Databases
MONGO_URL="mongodb+srv://..."
DB_NAME="portfolioDB"
CHROMA_API_KEY="<ChromaDB cloud key>"
CHROMA_TENANT="<ChromaDB tenant ID>"
CHROMA_DATABASE="Development"

# Email & Notifications
RESEND_KEY="<from resend.com>"
TO_EMAIL="your@email.com"

# Image Hosting
CLOUDINARY_CLOUD_NAME="..."
CLOUDINARY_API_KEY="..."
CLOUDINARY_API_SECRET="..."

# Security
CORS_ORIGINS="http://localhost:3000,https://www.althafportfolio.site,https://althafportfolio.site"
```

### Key File References
- **Main Entry:** [backend/server.py](backend/server.py) (FastAPI app, scheduler setup)
- **AI Wrapper:** [backend/gemini_service.py](backend/gemini_service.py) (OpenAI-compatible interface)
- **Agent Orchestration:** [backend/agent_service.py](backend/agent_service.py) (search + AI pipeline)
- **Search Utils:** [backend/search_utils.py](backend/search_utils.py) (cache, rate limiter)
- **Security:** [backend/security_utils.py](backend/security_utils.py) (sanitization, middleware)
- **DB Monitor:** [backend/chromadb_monitor.py](backend/chromadb_monitor.py) (usage tracking)
- **Frontend Router:** [frontend/src/App.js](frontend/src/App.js) (React Router setup)

### Common Pitfalls
1. **CORS Errors:** Ensure `CORS_ORIGINS` includes the exact frontend URL (no trailing slash mismatches)
2. **ChromaDB Quotas:** Monitor `query_tracking_log.json` - free tier has 50 queries/day limit
3. **Serper.dev Credits:** Use cache aggressively to avoid burning API credits (check `cache/` directory)
4. **Motor Async:** Always `await` MongoDB operations (`await db.collection.find_one()`)
5. **Scheduler Conflicts:** Only one `APScheduler` instance should run (lifespan manager ensures this)
6. **Import Errors:** Use `from backend import <module>` (not relative imports) due to package structure
