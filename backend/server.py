import os
import sys
import logging
import uuid
import json
import threading
import boto3
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Optional, Union, Tuple

# Third-party imports
from fastapi import FastAPI, APIRouter, UploadFile, File, Form, HTTPException, status, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field, EmailStr
import bleach
import subprocess
import cloudinary
import cloudinary.uploader
from google import genai
from google.genai import types
import chromadb
from chromadb import EmbeddingFunction, Documents, Embeddings
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from bson import ObjectId

# Local imports
try:
    from backend import agent_service
    from backend.ai_service import gemini_service
    from backend.notification_service import notification_service
    from backend.security_utils import sanitize_html
    from backend.models import ChatbotQuery
    from backend.cache_manager import ResponseCache
    from backend.rate_limiter import RateLimiter
    from backend.chatbot_provider import ChatbotProvider
    from backend.monitoring import chromadb_monitor
    HAS_AGENT_SERVICE = True
except ImportError as e:
    HAS_AGENT_SERVICE = False
    print(f"⚠️ Warning: Some backend services could not be imported: {e}")
    chromadb_monitor = None  # Monitoring disabled if import fails
    ResponseCache = None  # Fallback for cache
    RateLimiter = None  # Fallback for rate limiter
    ChatbotProvider = None  # Fallback for chatbot
    def sanitize_html(text):
        return bleach.clean(text)

# Security middleware with fallback
try:
    from backend.security_utils import SecurityHeadersMiddleware
    HAS_SECURITY_MIDDLEWARE = True
except ImportError:
    SecurityHeadersMiddleware = None
    HAS_SECURITY_MIDDLEWARE = False

# --- CONFIGURATION ---
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure Logging
log_dir = ROOT_DIR / 'logs'
log_dir.mkdir(exist_ok=True)
log_file_path = log_dir / 'chatbot.log'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(str(log_file_path), encoding='utf-8')
    ]
)
logger = logging.getLogger('PortfolioBackend')

# Database Setup
mongo_url = os.environ.get('MONGO_URL')
db_name = os.environ.get('DB_NAME', 'portfolioDB')
client = None
db = None

# ChromaDB Migration Toggle (Task 15)
USE_LEGACY_COLLECTIONS = os.environ.get('USE_LEGACY_COLLECTIONS', 'false').lower() == 'true'
logger.info(f"ChromaDB Mode: {'LEGACY (3 collections)' if USE_LEGACY_COLLECTIONS else 'UNIFIED (portfolio_master)'}")

if mongo_url:
    try:
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        print(f"✅ Connected to MongoDB: {db_name}")
    except Exception as e:
        print(f"❌ MongoDB Connection Error: {e}")

# Cloudinary Setup
cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key=os.environ.get('CLOUDINARY_API_KEY'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET'),
    secure=True
)

# Configure Gemini
# Configure Gemini Client
# genai.configure(api_key=os.getenv('GEMINI_API_KEY')) # Legacy
try:
    genai_client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
except Exception as e:
    print(f"Warning: Failed to init global Gemini Client: {e}")
    genai_client = None

# Initialize Multi-Provider Chatbot Components
try:
    if ResponseCache and RateLimiter and ChatbotProvider:
        response_cache = ResponseCache(max_size=100, ttl_seconds=3600)
        rate_limiter = RateLimiter(max_requests_per_minute=12)  # Per-session limit: 12 RPM
        chatbot_provider = ChatbotProvider()
        conversation_sessions = {}  # {session_id: [messages]}
        session_metadata = {}       # {session_id: {"state": "START", "disengagement_count": 0}}
        logger.info("Multi-provider chatbot components initialized (per-session rate limiting: 12 RPM)")
    else:
        raise ImportError("Chatbot dependencies not available")
except Exception as e:
    logger.error(f"Failed to initialize chatbot components: {e}")
    response_cache = None
    rate_limiter = None
    chatbot_provider = None
    conversation_sessions = {}
    session_metadata = {}
    session_metadata = {}

def determine_next_state(current_state: str, scores: dict, disengagement_count: int) -> str:
    """
    Finite-State Machine Transition Logic
    """
    # HARD EXIT — terminal
    if scores.get("exit", 0) >= 3:
        return "EXIT"

    # Repeated disengagement escalates to EXIT
    if disengagement_count >= 2 and scores.get("conversation", 0) > 0:
        return "EXIT"

    # START → first interpretation
    if current_state == "START":
        if scores.get("info", 0) >= 2:
            return "INFO"
        return "AMBIGUOUS" # Default to Hold/Ambiguous instead of Conversational

    # AMBIGUOUS → wait or escalate
    if current_state == "AMBIGUOUS":
        if scores.get("info", 0) >= 2:
            return "INFO"
        return "AMBIGUOUS" # Loop until specific

    # INFO → continue, soften, or exit
    if current_state == "INFO":
        if scores.get("info", 0) >= 2:
            return "INFO"
        if scores.get("conversation", 0) >= 1:
            return "AMBIGUOUS" # Fallback to hold

    # EXIT is terminal (unless reset implicitly by new session which handles START)
    if current_state == "EXIT":
        return "EXIT"

    # Fallback safety (Treat as Ambiguous/Conversation)
    return "AMBIGUOUS"

# --- EMBEDDING FUNCTION FOR SERVER ---
class GeminiEmbeddingFunction(EmbeddingFunction):
    def __init__(self):
        pass

    def __call__(self, input: Documents) -> Embeddings:
        try:
            # New SDK Embedding logic
            if not genai_client:
                return [[0.0] * 768 for _ in input]
                
            embeddings = []
            for text in input:
                response = genai_client.models.embed_content(
                    model='text-embedding-004',
                    contents=text,
                    config=types.EmbedContentConfig(
                        task_type="RETRIEVAL_QUERY"
                    )
                )
                embeddings.append(response.embeddings[0].values)
            return embeddings
        except Exception as e:
            logger.error(f"Embedding failed: {e}")
            return [[0.0] * 768 for _ in input]
            
# Scheduler Setup
scheduler = AsyncIOScheduler()



# --- LIFESPAN MANAGER ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize & Start New Auto-Blogger Scheduler
    print("🚀 Starting Auto-Blogger Scheduler...")
    try:
        def run_scheduler_thread():
            """Run the BlogScheduler in a dedicated thread with its own event loop"""
            import asyncio
            from backend.auto_blogger.scheduler import BlogScheduler
            
            # Create and set a new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                scheduler_instance = BlogScheduler()
                # Production mode: use scheduled times only (6AM, 7AM, 10AM IST)
                # Set run_now=True only for testing
                scheduler_instance.start(run_now=False)
            except Exception as e:
                print(f"❌ Scheduler thread error: {e}")
            finally:
                loop.close()
        
        scheduler_thread = threading.Thread(target=run_scheduler_thread, daemon=True, name="AutoBloggerScheduler")
        scheduler_thread.start()
        logger.info("✅ Auto-Blogger Scheduler started in background thread")

    except Exception as e:
        logger.error(f"❌ Failed to start Auto-Blogger Scheduler: {e}")
    
    yield
    print("🛑 Shutting down Server...")

# --- APP INSTANCE ---
app = FastAPI(title="Portfolio API", version="1.0.0", lifespan=lifespan)
api_router = APIRouter(prefix="/api")

# --- MIDDLEWARE ---
if HAS_SECURITY_MIDDLEWARE and SecurityHeadersMiddleware:
    app.add_middleware(SecurityHeadersMiddleware)

# Register Apology Sanitizer Middleware (Phase 9)
from backend.middleware.response_sanitizer import ResponseSanitizerMiddleware
app.add_middleware(ResponseSanitizerMiddleware)

# Explicitly define allowed origins
default_origins = [
    "http://localhost:3000",
    "https://www.althafportfolio.site",
    "https://althafportfolio.site",
    "https://api.althafportfolio.site"
]

origins_env = os.environ.get('CORS_ORIGINS')
if origins_env:
    origins = [origin.strip() for origin in origins_env.split(',') if origin.strip()]
else:
    origins = default_origins

print(f"🌍 CORS Allowed Origins: {origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MODELS ---
class ContactForm(BaseModel):
    name: str
    email: EmailStr
    subject: Optional[str] = None
    message: str

class Project(BaseModel):
    id: str
    name: str
    title: str
    summary: str
    description: str
    details: str = ""
    image_url: str
    technologies: List[str] = []
    key_outcomes: Optional[str] = None
    github_url: Optional[str] = None
    live_url: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class BlogPostRequest(BaseModel):
    topic: Optional[str] = None

# --- HELPER FUNCTIONS ---

import re  # Ensure re is available

def detect_intent_priority(text: str) -> Tuple[str, str, dict]:
    """
    CONFIDENCE-BASED INTENT ROUTER
    Normalize -> Score -> Decide (Thresholding)
    Prevents guessing on ambiguous inputs.
    Returns: (intent_key, sentiment, scores)
    """
    # 1. NORMALIZE
    text = text.lower().strip()
    text_clean = re.sub(r'[^a-z0-9\s]', '', text)  # Remove punctuation
    text_clean = re.sub(r'\s+', ' ', text_clean)   # Collapse spaces
    
    scores = {
        "conversation": 0, # Covers Ambiguous/Start
        "info": 0,         # Aggregates Projects/Blogs/AWS/Profile
        "exit": 0,
        # Keep specific intents for downstream routing if INFO wins
        "aws_projects": 0,
        "projects": 0,
        "blogs": 0,
        "profile": 0
    }
    
    # 2. SENTIMENT DETECTION (FIRST - HIGHEST PRIORITY)
    
    # HIGH SEVERITY PROFANITY (Direct abuse)
    high_profanity = ["fuck you", "fuck off", "go to hell", "fucking stupid"]
    if any(p in text for p in high_profanity):
        return "conversation", "hostile", scores
    
    # LOW SEVERITY PROFANITY (Frustration, not abuse)
    low_profanity = ["shit", "damn", "crap", "oh shit"]
    if any(p in text for p in low_profanity):
        return "conversation", "frustrated", scores
    
    # FRUSTRATION SIGNALS (No profanity but clear frustration)
    frustration_signals = ["i havent asked", "i haven't asked", "i didnt ask", "i didn't ask", 
                          "this is wrong", "not what i meant", "you are wrong", "annoying", 
                          "irritated", "irritating"]
    if any(sig in text for sig in frustration_signals):
        return "conversation", "frustrated", scores
    
    # CONFUSION SIGNALS
    confusion_signals = ["what?", "about what", "what do you mean", "i don't understand", 
                        "i dont understand", "why", "how come", "confused"]
    if any(sig in text for sig in confusion_signals):
        return "conversation", "confused", scores
    
    # 3. SCORING RULES (Only if sentiment is neutral)
    
    # Conversational / Ambiguous / Fillers
    ambiguous_triggers = ["ok", "fine", "hmm", "is it", "are you sure", "oh", "ah", "got it", "right", "good"]
    if any(t == text_clean or text_clean.startswith(t + " ") for t in ambiguous_triggers):
        scores["conversation"] += 2

    # Strong Exit Triggers (Terminal)
    exit_triggers = ["bye", "goodbye", "stop", "end", "nothing else", "done", "thank you bye", "cancel"]
    if any(t == text_clean or text_clean.startswith(t + " ") for t in exit_triggers):
        scores["exit"] += 3

    # Repeated/Weak Disengagement
    if text_clean in ["nothing", "no", "nope", "nah"]:
        scores["exit"] += 1
        scores["conversation"] += 1 # Serves as ambiguous filler too until threshold met
        
    # Feedback detection (relevance complaints)
    if "relev" in text_clean or "relav" in text_clean:
        scores["conversation"] += 3
        return "conversation", "frustrated", scores

    # Projects - check FIRST with higher priority to avoid "about projects" routing to profile
    if any(k in text_clean for k in ["project", "built", "develop", "portfolio", "app", "website", "created", "made"]):
        scores["projects"] += 12  # Higher than profile base score
        scores["info"] += 3
    
    # Profile / About (General) - includes work/employment questions
    if any(k in text_clean for k in ["who", "bio", "background", "resume", "experience", "skill", "contact", "email", "working", "employed", "job", "position", "role", "company", "current"]):
        scores["profile"] += 10
        scores["info"] += 3
        
    # "about" keyword - context-dependent (about him = profile, about projects = already scored above)
    if "about" in text_clean and not any(k in text_clean for k in ["project", "blog", "app", "website"]):
        scores["profile"] += 8  # Only add if not about projects/blogs
        
    # AWS / Cloud (Specific)
    if any(k in text_clean for k in ["aws", "cloud", "terraform", "deploy", "infrastructure", "pipeline", "ci/cd"]):
        scores["aws_projects"] += 10 
        scores["info"] += 3
        
    # Blogs
    if any(k in text_clean for k in ["blog", "article", "write", "post", "read"]):
        scores["blogs"] += 10
        scores["info"] += 3

    # 4. PURE GREETING DETECTION (After scoring, before decision)
    # Only trigger for standalone greetings with no real query
    greeting_triggers = ["hi", "hello", "hey", "hy", "hai", "hii", "hola", "greetings", "good morning", "good evening"]
    words = text_clean.split()
    
    # Pure greeting: 1-2 words max, starts with greeting, no strong intent detected
    if len(words) <= 2 and any(words[0] == t for t in greeting_triggers):
        best_intent, score = max(scores.items(), key=lambda x: x[1])
        # Only return greeting if no strong intent (score < 3)
        if score < 3:
            scores["greeting"] = 5
            return "greeting", "neutral", scores
    
    # 5. DECISION & THRESHOLD
    # Get highest scoring intent
    best_intent, score = max(scores.items(), key=lambda x: x[1])
    
    # LOGIC: If we aren't confident (score < 2), stay safe -> Conversation
    if score < 2:
        return "conversation", "neutral", scores
        
    return best_intent, "neutral", scores


async def get_portfolio_context(query: str, intent: str) -> str:
    """
    Smart RAG retrieval executed based on PRE-CALCULATED intent.
    Returns: context_string
    """
    all_context = []
    
    try:
        chroma_api_key = os.getenv('CHROMA_API_KEY')
        chroma_tenant = os.getenv('CHROMA_TENANT') or os.getenv('CHROMA_TENANT_ID')
        chroma_database = os.getenv('CHROMA_DATABASE') or os.getenv('CHROMA_DB_NAME')
        
        if not (chroma_api_key and chroma_tenant and chroma_database):
            logger.warning("ChromaDB credentials missing")
            return ""
            
        chroma_client = chromadb.CloudClient(
            api_key=chroma_api_key,
            tenant=chroma_tenant,
            database=chroma_database
        )

        # --- EXECUTING RAG ROUTING ---
        # Use passed intent
        logger.info(f"🧠 Routing Intent: {str(intent).upper()}")
        
        # Unified Collection Logic (Task 11)
        if USE_LEGACY_COLLECTIONS:
            # Rollback Mode: Use 3 separate collections
            collections_to_query = set()
            
            if intent == "aws_projects":
                collections_to_query.add('Projects_data') # Will be filtered for AWS later (Task 2)
            elif intent == "projects":
                collections_to_query.add('Projects_data')
            elif intent == "blogs":
                collections_to_query.add('Blogs_data')
            else: # limit to portfolio only for profile queries
                collections_to_query.add('portfolio')
            
            logger.info(f"[LEGACY MODE] Querying collections: {collections_to_query}")
        else:
            # Production Mode: Use unified portfolio_master with metadata filters
            collections_to_query = None  # Will use unified logic below
            logger.info(f"[UNIFIED MODE] Using portfolio_master with metadata filtering")
        
        # --- RAG DATE ANCHORING UTILS ---
        from datetime import date
        
        def normalize_blog_query(text: str) -> dict:
            text = text.lower()
            return {
                "is_today": any(k in text for k in ["today", "todays", "posted today"]),
                "is_recent": any(k in text for k in ["recent", "latest", "new"]),
                "explicit_title": None # Placeholder for NLP title extraction
            }

            
        def filter_blogs_by_date(docs, metas, ids, target_date=None, mode="exact"):
            """
            Filter blogs by date logic.
            mode="exact": strict match (e.g., today)
            mode="recent": sort by date DESC, take top 1
            """
            # Combine into objects for sorting
            combined = []
            for d, m, i in zip(docs, metas, ids):
                pub_date = m.get('published_date', '1970-01-01')
                combined.append({"doc": d, "meta": m, "id": i, "date": pub_date})
            
            if mode == "exact" and target_date:
                # Filter strict
                filtered = [c for c in combined if c['date'] == target_date]
                return ([c['doc'] for c in filtered], 
                        [c['meta'] for c in filtered], 
                        [c['id'] for c in filtered])
                        
            if mode == "recent":
                # Sort DESC string comparison works for ISO dates
                combined.sort(key=lambda x: x['date'], reverse=True)
                # Take top 1 (The latest blog)
                # But keep list structure
                if not combined:
                    return [], [], []
                top = combined[0]
                return [top['doc']], [top['meta']], [top['id']]
                
            return docs, metas, ids

        # --------------------------------
        
        # Unified Collection Query Logic
        if USE_LEGACY_COLLECTIONS:
            # Legacy Mode: Iterate 3 collections
            collection_iterator = collections_to_query
        else:
            # Unified Mode: Query portfolio_master once with metadata filters
            collection_iterator = ['portfolio_master']
        
        for collection_name in collection_iterator:
            try:
                # Prepare metadata filter for unified collection
                metadata_filter = None
                
                if not USE_LEGACY_COLLECTIONS:
                    # Intelligent filtering based on intent (Task 11)
                    if intent == "blogs":
                        # Strict blog filter
                        metadata_filter = {"category": "blog"}
                    elif intent == "projects" or intent == "aws_projects":
                        # Mixed query: project + profile data
                        metadata_filter = {"$or": [{"category": "project"}, {"category": "profile"}]}
                    elif intent == "profile":
                        # Profile only
                        metadata_filter = {"category": "profile"}
                    # else: No filter (query all categories)
                    
                    logger.info(f"Metadata filter: {metadata_filter}")
                
                collection = chroma_client.get_collection(
                    name=collection_name,
                    embedding_function=GeminiEmbeddingFunction()
                )
                
                # Monitor ChromaDB operation success
                if chromadb_monitor:
                    chromadb_monitor.track_success("get_collection", collection_name, duration_ms=0)
                
                # Split Limits Strategy (Visibility vs Safety)
                # Unified collection uses GLOBAL_LIMIT = 6 (Task 11)
                if USE_LEGACY_COLLECTIONS:
                    CANDIDATE_LIMIT = 5  
                    INJECTION_LIMIT = 2
                    
                    # Intent-Specific Configurations (Legacy)
                    search_query = query
                    
                    if intent == "aws_projects":
                        CANDIDATE_LIMIT = 5
                        INJECTION_LIMIT = 2
                        search_query = f"AWS Cloud Infrastructure {query}"
                    elif intent == "projects":
                        CANDIDATE_LIMIT = 5
                        INJECTION_LIMIT = 3
                    elif intent == "blogs":
                        CANDIDATE_LIMIT = 6 # Higher visibility for blogs
                        INJECTION_LIMIT = 2
                    elif intent == "profile":
                        CANDIDATE_LIMIT = 3
                        INJECTION_LIMIT = 2
                else:
                    # Unified Mode: GLOBAL_LIMIT = 6
                    CANDIDATE_LIMIT = 6
                    INJECTION_LIMIT = 6  # Return all candidates in unified mode
                    search_query = query
                    
                    if intent == "aws_projects":
                        search_query = f"AWS Cloud Infrastructure {query}"

                logger.info(f"Querying {collection_name} | Candidates: {CANDIDATE_LIMIT} | Injection: {INJECTION_LIMIT}")
                
                # 1. Fetch Candidates (High Visibility)
                # Apply metadata filter for unified collection
                query_kwargs = {"query_texts": [search_query], "n_results": CANDIDATE_LIMIT}
                if metadata_filter and not USE_LEGACY_COLLECTIONS:
                    query_kwargs["where"] = metadata_filter
                
                # Monitor query operation
                if chromadb_monitor:
                    with chromadb_monitor.track_operation("query", collection_name):
                        results = collection.query(**query_kwargs)
                else:
                    results = collection.query(**query_kwargs)
                
                docs = results.get('documents', [[]])[0]
                metas = results.get('metadatas', [[]])[0]
                ids = results.get('ids', [[]])[0]
                
                # 2. Date Anchoring & Scope Logic (Blogs Only)
                # Works for both legacy (Blogs_data) and unified (portfolio_master with category='blog')
                is_blog_query = (USE_LEGACY_COLLECTIONS and collection_name == "Blogs_data") or \
                                (not USE_LEGACY_COLLECTIONS and intent == "blogs")
                
                if is_blog_query:
                    filters = normalize_blog_query(query)
                    today_iso = date.today().isoformat()
                    
                    if filters['is_today']:
                        # Prioritize temporal match over semantic rank
                        f_docs, f_metas, f_ids = filter_blogs_by_date(docs, metas, ids, today_iso)
                        if f_docs:
                            logger.info(f"📅 Date Anchor Hit: Found {len(f_docs)} blogs for {today_iso}")
                            docs, metas, ids = f_docs, f_metas, f_ids
                            # SCOPE LOCK: Force exactly 1 source for specific date queries
                            INJECTION_LIMIT = 1 
                        else:
                            logger.info(f"📅 Date Anchor Miss: No blogs found for {today_iso}")
                            
                    elif filters['is_recent']:
                        # NEW PHASE 9 LOGIC: "Recent" means TIME, not RELEVANCE
                        # Re-sort by date DESC and take top 1
                        logger.info("📅 Temporal Logic: Sorting by 'Recent' (Date DESC)")
                        f_docs, f_metas, f_ids = filter_blogs_by_date(docs, metas, ids, mode="recent")
                        if f_docs:
                            docs, metas, ids = f_docs, f_metas, f_ids
                            INJECTION_LIMIT = 1
                            logger.info(f"✅ Found most recent blog: {metas[0].get('title')} ({metas[0].get('published_date')})")
                        else:
                            logger.info("⚠️ Recent filter failed, falling back to semantic.")
                            
                            # Fallback to semantic recent (already sorted by similarity)
                            pass
                            
                # 3. Injection Clamping (Safety)
                limit = INJECTION_LIMIT  # Safety clamp explicitly named 'limit' (Gate Requirement)
                docs = docs[:limit]
                metas = metas[:limit]
                
                if docs:
                    summarized_docs = []
                    for i, d in enumerate(docs):
                        meta = metas[i] if i < len(metas) else {}
                        source_label = meta.get('title', collection_name)
                        
                        if chatbot_provider:
                            summary = chatbot_provider.summarize_content(d)
                            summarized_docs.append(f"[Source: {source_label}] (Date: {meta.get('published_date', 'N/A')})\n{summary}")
                        else:
                            summarized_docs.append(f"[Source: {source_label}]\n{d[:800]}...")
                            
                    all_context.extend(summarized_docs)
            except Exception as e:
                logger.warning(f"Skipping collection {collection_name}: {e}")
                
                # Log error to monitoring system
                if chromadb_monitor:
                    # Classify error severity
                    if "not found" in str(e).lower() or "does not exist" in str(e).lower():
                        severity = "CRITICAL"
                        error_type = "CollectionNotFound"
                    elif "query" in str(e).lower() or "failed" in str(e).lower():
                        severity = "HIGH"
                        error_type = "QueryFailed"
                    else:
                        severity = "MEDIUM"
                        error_type = "UnknownError"
                    
                    chromadb_monitor.log_error(
                        operation="query",
                        collection=collection_name,
                        error_type=error_type,
                        error_message=str(e),
                        severity=severity,
                        context={
                            "query": query[:200] if query else "",
                            "intent": intent,
                            "use_legacy": USE_LEGACY_COLLECTIONS
                        }
                    )
                
                continue
        
        context_text = '\n\n'.join(all_context)
        logger.info(f"Retrieved context length: {len(context_text)} characters")
        return context_text, intent
        
    except Exception as e:
        logger.error(f"RAG Error: {e}")
        
        # Log critical RAG pipeline failure
        if chromadb_monitor:
            chromadb_monitor.log_error(
                operation="rag_pipeline",
                collection="multiple" if USE_LEGACY_COLLECTIONS else "portfolio_master",
                error_type="RAGPipelineFailure",
                error_message=str(e),
                severity="CRITICAL",
                context={
                    "query": query[:200] if query else "",
                    "intent": intent,
                    "use_legacy": USE_LEGACY_COLLECTIONS
                }
            )
        
        return "", ""

# --- ENDPOINTS ---

@app.get("/")
def welcome():
    return {"message": "Server is running. API is at /api"}

# --- SITEMAP ENDPOINT ---
@app.get("/sitemap.xml")
async def serve_sitemap():
    """Serve sitemap from S3 with proper XML content-type to bypass Amplify SPA routing."""
    import boto3
    from fastapi.responses import Response
    
    try:
        # Fetch sitemap from S3
        s3 = boto3.client('s3')
        response = s3.get_object(
            Bucket='althaf-blogs-storage',
            Key='sitemap.xml'
        )
        sitemap_content = response['Body'].read()
        
        # Return with XML content-type
        return Response(
            content=sitemap_content,
            media_type="application/xml",
            headers={
                "Cache-Control": "max-age=3600",
                "X-Content-Type-Options": "nosniff"
            }
        )
    except Exception as e:
        logger.error(f"Failed to fetch sitemap from S3: {e}")
        raise HTTPException(status_code=500, detail="Sitemap unavailable")

# --- GET SINGLE PROJECT ---
@api_router.get("/projects/{project_id}", response_model=Project)
async def get_project_details(project_id: str):
    """Fetch a single project by ID with safe defaults."""
    # 1. Try MongoDB
    if db is not None:
        try:
            # Try finding by 'id' string field
            project = await db.projects.find_one({"id": project_id})
            
            # If not found, try 'slug' or '_id' if valid objectid
            if not project:
                try:
                    if ObjectId.is_valid(project_id):
                        project = await db.projects.find_one({"_id": ObjectId(project_id)})
                except:
                    pass

            if project:
                # SAFE RETURN: Manually build dict to ensure no missing fields cause 500
                return {
                    "id": str(project.get("id", project_id)),
                    "name": project.get("name", project.get("title", "Untitled")),
                    "title": project.get("title", project.get("name", "Untitled")),
                    "summary": project.get("summary", project.get("description", "")),
                    "description": project.get("description", ""),
                    "details": project.get("details", project.get("content", "")),
                    "image_url": project.get("image_url", ""),
                    "technologies": project.get("technologies", []),
                    "key_outcomes": project.get("key_outcomes", ""),
                    "github_url": project.get("github_url", ""),
                    "live_url": project.get("live_url", ""),
                    "timestamp": project.get("timestamp", datetime.utcnow())
                }
        except Exception as e:
            logger.error(f"MongoDB error: {e}")

    # 2. Fallback to Local JSON
    for filename in ['portfolio_data_complete.json', 'portfolio_data.json']:
        try:
            json_path = ROOT_DIR / filename
            if not json_path.exists():
                json_path = Path(f'backend/{filename}')
            
            if json_path.exists():
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for p in data.get('projects', []):
                        if str(p.get("id")) == project_id:
                            return {
                                "id": str(p.get("id")),
                                "name": p.get("name", p.get("title", "Untitled")),
                                "title": p.get("title", p.get("name", "Untitled")),
                                "summary": p.get("summary", p.get("description", "")),
                                "description": p.get("description", ""),
                                "details": p.get("details", p.get("content", "")),
                                "image_url": p.get("image_url", ""),
                                "technologies": p.get("technologies", []),
                                "key_outcomes": p.get("key_outcomes", ""),
                                "github_url": p.get("github_url", ""),
                                "live_url": p.get("live_url", ""),
                                "timestamp": p.get("timestamp", datetime.utcnow())
                            }
        except Exception:
            continue

    raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

@api_router.get("/projects", response_model=List[Project])
async def get_projects():
    # 1. Try fetching from MongoDB first (Priority)
    mongo_projects = []
    if db is not None:
        try:
            cursor = db.projects.find({})
            async for p in cursor:
                # Normalize fields
                mongo_projects.append({
                    "id": str(p.get("id", uuid.uuid4())),
                    "name": p.get("name", p.get("title", "Untitled")),
                    "title": p.get("title", p.get("name", "Untitled")),
                    "summary": p.get("summary", p.get("description", "")),
                    "description": p.get("description", ""),
                    "details": p.get("details", ""),
                    "image_url": p.get("image_url", ""),
                    "technologies": p.get("technologies", []),
                    "key_outcomes": p.get("key_outcomes", ""),
                    "github_url": p.get("github_url", ""),
                    "live_url": p.get("live_url", ""),
                    "timestamp": p.get("timestamp", datetime.utcnow())
                })
            if mongo_projects:
                return mongo_projects
        except Exception as e:
            logger.error(f"Error fetching from MongoDB: {e}")

    # 2. Fallback to Local JSON (Only if Mongo is empty or fails)
    try:
        json_path = ROOT_DIR / 'portfolio_data_complete.json'
        if not json_path.exists():
            json_path = Path('backend/portfolio_data_complete.json')
        if not json_path.exists():
            return []

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        raw_projects = data.get('projects', [])
        clean_projects = []

        for p in raw_projects:
            clean_projects.append({
                "id": str(p.get("id", uuid.uuid4())),
                "name": p.get("name", p.get("title", "Untitled")),
                "title": p.get("title", p.get("name", "Untitled")),
                "summary": p.get("summary", p.get("description", "")),
                "description": p.get("description", ""),
                "details": p.get("details", ""),
                "image_url": p.get("image_url", ""),
                "technologies": p.get("technologies", []),
                "key_outcomes": p.get("key_outcomes", ""),
                "github_url": p.get("github_url", ""),
                "live_url": p.get("live_url", ""),
                "timestamp": p.get("timestamp", datetime.utcnow())
            })
        return clean_projects
    except Exception as e:
        logger.error(f"Error reading projects: {e}")
        return []

@api_router.post("/projects", status_code=status.HTTP_201_CREATED)
async def create_project(
    name: str = Form(...),
    summary: str = Form(...),
    details: str = Form(...),
    technologies: str = Form(...),
    key_outcomes: str = Form(...),
    file: UploadFile = File(...)
):
    if db is None:
        raise HTTPException(status_code=503, detail="Database unavailable")
    try:
        upload_result = cloudinary.uploader.upload(file.file, folder="portfolio_projects")
        image_url = upload_result.get("secure_url")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image upload failed: {str(e)}")

    project_data = {
        "id": str(uuid.uuid4()),
        "name": bleach.clean(name),
        "title": bleach.clean(name),
        "summary": bleach.clean(summary),
        "description": bleach.clean(summary),
        "details": sanitize_html(details),
        "image_url": image_url,
        "technologies": [t.strip() for t in bleach.clean(technologies).split(',')],
        "key_outcomes": bleach.clean(key_outcomes),
        "timestamp": datetime.utcnow()
    }
    await db.projects.insert_one(project_data)
    # Background sync removed to prevent OOM
    return project_data

# --- GET /api/blogs (Merged: Local + S3) ---
@api_router.get("/blogs")
async def get_blogs():
    """
    Serve ALL blogs: existing local blogs + new S3 auto-generated blogs
    Returns merged list sorted by creation date (newest first)
    """
    all_blogs = []
    
    try:
        # 1. Load existing local blogs (original 10 blogs)
        try:
            from backend.read_local_blogs import get_local_blogs
            local_blogs = get_local_blogs()
            if local_blogs:
                logger.info(f"Loaded {len(local_blogs)} local blogs")
                all_blogs.extend(local_blogs)
        except Exception as e:
            logger.warning(f"Could not load local blogs: {e}")
        
        # 2. Load new auto-generated blogs from S3
        try:
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent))
            from auto_blogger.publisher import S3BlogStorage
            
            s3_bucket = os.getenv("S3_BLOG_BUCKET", "althaf-blogs-storage")
            storage = S3BlogStorage(bucket_name=s3_bucket)
            index_data = storage.read_index()
            s3_blogs = index_data.get('blogs', [])
            
            if s3_blogs:
                logger.info(f"Loaded {len(s3_blogs)} S3 blogs")
                all_blogs.extend(s3_blogs)
        except Exception as e:
            logger.warning(f"Could not load S3 blogs: {e}")
        
        # 3. Remove duplicates (in case a blog exists in both sources)
        seen_ids = set()
        unique_blogs = []
        for blog in all_blogs:
            blog_id = blog.get('id') or blog.get('_id')
            if blog_id and blog_id not in seen_ids:
                seen_ids.add(blog_id)
                unique_blogs.append(blog)
        
        # 4. Sort by creation date (newest first)
        unique_blogs.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        logger.info(f"Total blogs served: {len(unique_blogs)} (local + S3, deduplicated)")
        return {"blogs": unique_blogs}
        
    except Exception as e:
        logger.error(f"Error loading blogs: {e}")
        return {"blogs": []}

@api_router.get("/blogs/{blog_id}")
async def get_blog_post(blog_id: str):
    """
    Serve individual blog post JSON from S3
    """
    try:
        # Import S3BlogStorage dynamically
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent))
        from auto_blogger.publisher import S3BlogStorage
        
        s3_bucket = os.getenv("S3_BLOG_BUCKET", "althaf-blogs-storage")
        storage = S3BlogStorage(bucket_name=s3_bucket)
        
        blog = storage.read_blog(blog_id)
        
        if not blog:
             raise HTTPException(status_code=404, detail="Blog not found")
             
        return blog
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading blog {blog_id} from S3: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@api_router.put("/projects/{project_id}", response_model=Project)
async def update_project(
    project_id: str,
    name: Optional[str] = Form(None),
    summary: Optional[str] = Form(None),
    details: Optional[str] = Form(None),
    technologies: Optional[str] = Form(None),
    key_outcomes: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    """Update an existing project."""
    if db is None:
        raise HTTPException(status_code=503, detail="Database unavailable")

    # Find the project
    project = await db.projects.find_one({"id": project_id})
    if not project:
         if ObjectId.is_valid(project_id):
            project = await db.projects.find_one({"_id": ObjectId(project_id)})
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    update_data = {}
    if name: update_data["name"] = bleach.clean(name); update_data["title"] = bleach.clean(name)
    if summary: update_data["summary"] = bleach.clean(summary); update_data["description"] = bleach.clean(summary)
    if details: update_data["details"] = sanitize_html(details)
    if technologies: update_data["technologies"] = [t.strip() for t in bleach.clean(technologies).split(',')]
    if key_outcomes: update_data["key_outcomes"] = bleach.clean(key_outcomes)

    if file:
        try:
            upload_result = cloudinary.uploader.upload(file.file, folder="portfolio_projects")
            update_data["image_url"] = upload_result.get("secure_url")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Image upload failed: {str(e)}")

    if update_data:
        update_data["timestamp"] = datetime.utcnow()
        await db.projects.update_one({"_id": project["_id"]}, {"$set": update_data})
        
    # Return updated project
    updated_project = await db.projects.find_one({"_id": project["_id"]})
    if "_id" in updated_project: del updated_project["_id"]
    
    # Safe return manual construction
    return {
        "id": str(updated_project.get("id", project_id)),
        "name": updated_project.get("name", ""),
        "title": updated_project.get("title", ""),
        "summary": updated_project.get("summary", ""),
        "description": updated_project.get("description", ""),
        "details": updated_project.get("details", ""),
        "image_url": updated_project.get("image_url", ""),
        "technologies": updated_project.get("technologies", []),
        "key_outcomes": updated_project.get("key_outcomes", ""),
        "github_url": updated_project.get("github_url", ""),
        "live_url": updated_project.get("live_url", ""),
        "timestamp": updated_project.get("timestamp", datetime.utcnow())
    }

# --- DELETE PROJECT ---
@api_router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: str):
    """Delete a project by ID."""
    if db is None:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    # Try deleting by custom 'id' string first
    result = await db.projects.delete_one({"id": project_id})
    
    # If not found, try deleting by MongoDB '_id'
    if result.deleted_count == 0:
        if ObjectId.is_valid(project_id):
            result = await db.projects.delete_one({"_id": ObjectId(project_id)})
            
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    
    return None

@api_router.post("/contact")
async def send_contact_email(form: ContactForm):
    try:
        response = await notification_service.send_contact_email(form)
        return response
    except Exception as e:
        logger.error(f"Contact error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/generate-blog")
async def generate_blog(request: BlogPostRequest):
    if not HAS_AGENT_SERVICE:
        return JSONResponse(status_code=503, content={"error": "Agent service unavailable"})
    try:
        blog = agent_service.generate_blog_now(request.topic)
        return blog
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@api_router.post("/ask-all-u-bot")
async def ask_agent(query: dict):
    """
    Multi-provider chatbot with intelligent routing and caching
    """
    message = query.get('message', '')
    session_id = query.get('session_id', 'default')  # Optional session tracking
    
    if not message:
        return JSONResponse(
            status_code=400,
            content={"reply": "I'm listening. How can I help you with Althaf's portfolio?"}
        )
    
    try:
        # Per-session rate limiting check
        if not rate_limiter.check_limit(session_id):
            wait_time = rate_limiter.get_wait_time(session_id)
            logger.warning(f"Rate limit exceeded for session {session_id}. Wait time: {wait_time:.1f}s")
            return JSONResponse(
                status_code=429,
                content={
                    "reply": f"Please wait {int(wait_time)} seconds before sending another message.",
                    "wait_time": wait_time
                }
            )
        
        # Get conversation history
        history = conversation_sessions.get(session_id, [])
        
        # Check cache first
        cached_response = response_cache.get(message, history)
        if cached_response:
            logger.info("Returning cached response")
            return JSONResponse(
                status_code=200,
                content={"reply": cached_response, "source": "Cache"}
            )
        
        # Record request for per-session rate limiting
        rate_limiter.record_request(session_id)
        
        # Start timer for telemetry
        start_time = datetime.now()
        
        # --- STATE MACHINE RECOVERY ---
        if session_id not in session_metadata:
            session_metadata[session_id] = {
                "state": "ACTIVE", 
                "greeting_count": 0,
                "history": []
            }
        
        # Track conversation history
        history = session_metadata[session_id].get("history", [])
        history.append({"role": "user", "content": message})
        session_metadata[session_id]["history"] = history[-10:]  # Keep last 10 messages
        logger.info(f"🧠 Processing message: {message[:50]}...")

        # LLM HANDLES EVERYTHING NATURALLY - No predefined rules
        response_text = ""
        portfolio_context = ""
        
        # A. Intent Detection for Retrieval (only for RAG, not response control)
        intent, _, intent_scores = detect_intent_priority(message)
        
        # B. Smart RAG retrieval based on intent
        if intent == "conversation":
            # For casual talk, provide general profile context
            rag_intent = "profile"
        else:
            rag_intent = intent
            
        portfolio_context, _ = await get_portfolio_context(message, rag_intent)
        
        # C. Check if first interaction for personalized greeting
        is_first_interaction = session_metadata[session_id].get("greeting_count", 0) == 0
        
        # D. Let LLM handle everything naturally
        response_text = chatbot_provider.generate_response(
            query=message,
            context=portfolio_context,
            history=history,
            sentiment="neutral",
            is_first_interaction=is_first_interaction
        )
        
        # E. Track interaction count
        if is_first_interaction:
            session_metadata[session_id]["greeting_count"] = 1

        duration = (datetime.now() - start_time).total_seconds()
        
        # 5. UPDATE STATE (simplified - just track conversation flow)
        session_metadata[session_id]["state"] = "ACTIVE"
        session_metadata[session_id]["disengagement_count"] = 0
        
        # 6. TELEMETRY LOGGING
        est_input_tok = (len(message) + len(portfolio_context)) / 4
        est_output_tok = len(response_text) / 4
        
        telemetry_log = {
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat(),
            "normalized_input": message.lower().strip()[:50],
            "intent": intent,
            "input_tokens": int(est_input_tok),
            "output_tokens": int(est_output_tok),
            "latency_ms": int(duration * 1000)
        }
        logger.info(json.dumps(telemetry_log))
        
        # Update conversation history
        history.append({"role": "assistant", "content": response_text})
        session_metadata[session_id]["history"] = history[-10:]
        
        return JSONResponse(
            status_code=200,
            content={"reply": response_text, "source": "AI Assistant"}
        )
        
    except Exception as e:
        logger.error(f"Error in ask_agent: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"reply": "I'm having technical difficulties. Please try again in a moment."}
        )

# Include router
app.include_router(api_router)

# Health/Version Endpoint
from datetime import timezone # Added for timezone.utc
@app.get("/version")
async def get_version():
    return {"version": "1.0.0", "status": "active", "timestamp": datetime.now(timezone.utc).isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)