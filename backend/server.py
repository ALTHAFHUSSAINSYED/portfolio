import os
import sys
import logging
import uuid
import json
import threading
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
    HAS_AGENT_SERVICE = True
except ImportError as e:
    HAS_AGENT_SERVICE = False
    print(f"⚠️ Warning: Some backend services could not be imported: {e}")
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
    response_cache = ResponseCache(max_size=100, ttl_seconds=3600)
    rate_limiter = RateLimiter(max_requests_per_minute=20)
    chatbot_provider = ChatbotProvider()
    chatbot_provider = ChatbotProvider()
    conversation_sessions = {}  # {session_id: [messages]}
    session_metadata = {}       # {session_id: {"state": "START", "disengagement_count": 0}}
    logger.info("Multi-provider chatbot components initialized")
except Exception as e:
    logger.error(f"Failed to initialize chatbot components: {e}")
    response_cache = None
    rate_limiter = None
    chatbot_provider = None
    conversation_sessions = {}
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

    # Profile / About (General)
    if any(k in text_clean for k in ["who", "about", "bio", "background", "resume", "experience", "skill", "contact", "email"]):
        scores["profile"] += 5
        scores["info"] += 3
        
    # Projects (General)
    if any(k in text_clean for k in ["project", "built", "work", "develop", "portfolio", "app", "website"]):
        scores["projects"] += 10
        scores["info"] += 3
        
    # AWS / Cloud (Specific)
    if any(k in text_clean for k in ["aws", "cloud", "terraform", "deploy", "infrastructure", "pipeline", "ci/cd"]):
        scores["aws_projects"] += 10 
        scores["info"] += 3
        
    # Blogs
    if any(k in text_clean for k in ["blog", "article", "write", "post", "read"]):
        scores["blogs"] += 10
        scores["info"] += 3

    # 4. DECISION & THRESHOLD
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
        
        collections_to_query = set()
        
        if intent == "aws_projects":
            collections_to_query.add('Projects_data') # Will be filtered for AWS later (Task 2)
        elif intent == "projects":
            collections_to_query.add('Projects_data')
        elif intent == "blogs":
            collections_to_query.add('Blogs_data')
        else: # limit to portfolio only for profile queries
            collections_to_query.add('portfolio')
        
        logger.info(f"Querying collections: {collections_to_query}")
        
        # --- RAG DATE ANCHORING UTILS ---
        from datetime import date
        
        def normalize_blog_query(text: str) -> dict:
            text = text.lower()
            return {
                "is_today": any(k in text for k in ["today", "todays", "posted today"]),
                "is_recent": any(k in text for k in ["recent", "latest", "new"]),
                "explicit_title": None # Placeholder for NLP title extraction
            }
            
        def filter_blogs_by_date(docs, metas, ids, target_date):
            filtered_docs, filtered_metas, filtered_ids = [], [], []
            for d, m, i in zip(docs, metas, ids):
                # Ensure it's a blog and matches date
                if m.get('published_date') == target_date:
                    filtered_docs.append(d)
                    filtered_metas.append(m)
                    filtered_ids.append(i)
            return filtered_docs, filtered_metas, filtered_ids

        # --------------------------------
        
        for collection_name in collections_to_query:
            try:
                collection = chroma_client.get_collection(
                    name=collection_name,
                    embedding_function=GeminiEmbeddingFunction()
                )
                
                # Split Limits Strategy (Visibility vs Safety)
                CANDIDATE_LIMIT = 5  
                INJECTION_LIMIT = 2
                
                # Intent-Specific Configurations
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

                logger.info(f"Querying {collection_name} | Candidates: {CANDIDATE_LIMIT} | Injection: {INJECTION_LIMIT}")
                
                # 1. Fetch Candidates (High Visibility)
                results = collection.query(query_texts=[search_query], n_results=CANDIDATE_LIMIT)
                
                docs = results.get('documents', [[]])[0]
                metas = results.get('metadatas', [[]])[0]
                ids = results.get('ids', [[]])[0]
                
                # 2. Date Anchoring & Scope Logic (Blogs Only)
                if collection_name == "Blogs_data":
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
                continue
        
        context_text = '\n\n'.join(all_context)
        logger.info(f"Retrieved context length: {len(context_text)} characters")
        return context_text, intent
        
    except Exception as e:
        logger.error(f"RAG Error: {e}")
        return ""

# --- ENDPOINTS ---

@app.get("/")
def welcome():
    return {"message": "Server is running. API is at /api"}

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
        # Rate limiting check
        if not rate_limiter.check_limit():
            wait_time = rate_limiter.get_wait_time()
            logger.warning(f"Rate limit exceeded. Wait time: {wait_time:.1f}s")
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
        
        # Record request for rate limiting
        rate_limiter.record_request()
        
        
        # Record request for rate limiting
        rate_limiter.record_request()
        
        # Start timer for telemetry
        start_time = datetime.now()
        
        # --- STATE MACHINE RECOVERY ---
        if session_id not in session_metadata:
            session_metadata[session_id] = {
                "state": "START", 
                "disengagement_count": 0,
                "response_mode": "ANSWER_ONLY"  # Default: answer only what was asked
            }
            
        current_state = session_metadata[session_id]["state"]
        disengagement_count = session_metadata[session_id]["disengagement_count"]
        
        # 1. INTENT & SCORING
        intent, sentiment, intent_scores = detect_intent_priority(message)
        
        # ========================================
        # SENTIMENT GATE (ABSOLUTE PRIORITY)
        # Sentiment overrides ALL downstream logic
        # ========================================
        
        if sentiment == "hostile":
            # HARD STOP - Direct abuse
            session_metadata[session_id]["state"] = "EXIT"
            session_metadata[session_id]["exit_acknowledged"] = True
            logger.warning(f"🚨 HOSTILE sentiment detected: {message[:50]}")
            return JSONResponse(
                status_code=200,
                content={
                    "reply": "I'm here to help, but I can't continue this conversation if the language stays disrespectful.",
                    "source": "SentimentGate"
                }
            )
        
        if sentiment == "frustrated":
            # SOFT RESET - User is annoyed/frustrated
            session_metadata[session_id]["state"] = "AMBIGUOUS"
            session_metadata[session_id]["disengagement_count"] = 0
            logger.info(f"⚠️ FRUSTRATED sentiment detected: {message[:50]}")
            return JSONResponse(
                status_code=200,
                content={
                    "reply": "It sounds like this wasn't what you expected. What would you like me to clarify?",
                    "source": "SentimentGate"
                }
            )
        
        if sentiment == "confused":
            # CLARIFICATION MODE - User doesn't understand
            session_metadata[session_id]["state"] = "AMBIGUOUS"
            logger.info(f"❓ CONFUSED sentiment detected: {message[:50]}")
            return JSONResponse(
                status_code=200,
                content={
                    "reply": "It seems I may not have explained that clearly. What would you like me to clarify?",
                    "source": "SentimentGate"
                }
            )
        
        # ========================================
        # END SENTIMENT GATE
        # Only neutral/positive sentiment reaches here
        # ========================================
        
        # 2. UPDATE DISENGAGEMENT COUNTER
        # Track consecutive "nothing/no" to allow gentle exit escalation
        if message.lower().strip() in ["nothing", "no", "nope", "nah"]:
            disengagement_count += 1
        else:
            disengagement_count = 0 # Reset on engagement
        
        # ========================================
        # POST-EXIT SILENCE CHECK (BEFORE STATE DETECTION)
        # If user already exited, ignore all further input
        # ========================================
        if session_metadata.get(session_id, {}).get("exit_acknowledged"):
            logger.info(f"Post-exit input ignored (silence): {message}")
            return JSONResponse(status_code=200, content={"reply": "", "source": "System"})
        # ========================================

        # 3. CONVERSATION STATE MACHINE (The "Gods' Logic")
        # Deterministic control before AI capabilities
        next_state = chatbot_provider.detect_conversation_state(message)
        
        # ========================================
        # RESPONSE MODE MAPPING (Phase 2)
        # Determines HOW to respond based on state
        # ========================================
        if next_state in ["START", "AMBIGUOUS", "SILENT"]:
            response_mode = "CONVERSATION"  # Casual, minimal
        elif next_state == "INFO":
            response_mode = "ANSWER_ONLY"   # Answer what was asked, nothing more
        else:
            response_mode = "ANSWER_ONLY"   # Default safe mode
        
        session_metadata[session_id]["response_mode"] = response_mode
        logger.info(f"📝 Response Mode: {response_mode}")
        # ========================================
        
        # Session Persistence Logic for EXIT
        if next_state == "EXIT":
            session_metadata[session_id]["exit_acknowledged"] = True

        logger.info(f"🧠 State: {next_state.upper()} (Prev: {current_state}) | Mode: {response_mode}")

        # 4. EXECUTE RESPONSE STRATEGY
        response_text = ""
        portfolio_context = "" # Only used for telemetry/logging
        
        if next_state != "INFO":
            # MICRO-RESPONSES (Fast path, no LLM)
            response_text = chatbot_provider.generate_response_by_state(next_state, message)
            
        else:
            # INFO STATE -> FULL RAG PIPELINE
            
            # A. Intent Detection for Retrieval
            intent, _, intent_scores = detect_intent_priority(message)
            
            # B. Retrieval
            rag_intent = intent
            if rag_intent == "conversation": 
                 # Fallback if INFO state triggered by generic keywords but intent classifier was weak
                 rag_intent = "projects" if intent_scores.get("projects", 0) > 0 else "profile"
                 
            portfolio_context = await get_portfolio_context(message, rag_intent)
            
            # C. LLM Generation
            response_text = chatbot_provider.generate_response(
                query=message,
                context=portfolio_context,
                history=history,
                sentiment="neutral" # Context is already filtered/safe
            )

        duration = (datetime.now() - start_time).total_seconds()
        
        # 5. UPDATE STATE PERSISTENCE
        session_metadata[session_id]["state"] = next_state
        session_metadata[session_id]["disengagement_count"] = disengagement_count
        
        # 6. TELEMETRY LOGGING
        est_input_tok = (len(message) + len(portfolio_context)) / 4
        est_output_tok = len(response_text) / 4
        
        telemetry_log = {
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat(),
            "normalized_input": message.lower().strip()[:50],
            "intent_scores": intent_scores if next_state == "INFO" else {},
            "final_state": next_state,
            "rag_used": next_state == "INFO",
            "model_used": "multi-tier-chain" if next_state == "INFO" else "deterministic",
            "input_tokens": int(est_input_tok),
            "output_tokens": int(est_output_tok),
            "latency_ms": int(duration * 1000)
        }
        logger.info(json.dumps(telemetry_log))
        
        # Update conversations
        # Only append valid interactions (Skip SILENT if needed, but keeping for continuity is safer)
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": response_text})
        if len(history) > 4:
            history = history[-4:]
        conversation_sessions[session_id] = history
        
        # Cache active interactions (Only INFO/RAG)
        if next_state == "INFO":
            response_cache.set(message, response_text, history)
        
        return JSONResponse(
            status_code=200,
            content={"reply": response_text, "source": "Multi-Provider AI"}
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