import os
import sys
import logging
import uuid
import json
import threading
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Optional, Union

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
import google.generativeai as genai
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
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
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
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Initialize Multi-Provider Chatbot Components
try:
    response_cache = ResponseCache(max_size=100, ttl_seconds=3600)
    rate_limiter = RateLimiter(max_requests_per_minute=20)
    chatbot_provider = ChatbotProvider()
    conversation_sessions = {}  # {session_id: [messages]}
    logger.info("Multi-provider chatbot components initialized")
except Exception as e:
    logger.error(f"Failed to initialize chatbot components: {e}")
    response_cache = None
    rate_limiter = None
    chatbot_provider = None
    conversation_sessions = {}

# --- EMBEDDING FUNCTION FOR SERVER ---
class GeminiEmbeddingFunction(EmbeddingFunction):
    def __init__(self):
        pass

    def __call__(self, input: Documents) -> Embeddings:
        try:
            return [
                genai.embed_content(
                    model='models/text-embedding-004',
                    content=text,
                    task_type="retrieval_query" 
                )['embedding']
                for text in input
            ]
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

def is_greeting_or_conversational(text: str) -> tuple:
    """
    Detect if message is a greeting or conversational (skip database for these).
    Returns (is_greeting, sentiment)
    """
    text = text.lower().strip()
    
    # Greetings - simple short messages
    greetings = ['hi', 'hello', 'hey', 'good morning', 'good evening', 'hola', 'greetings', 'namaste']
    if any(text.startswith(g) for g in greetings) and len(text.split()) < 5:
        return True, "neutral"
    
    # Conversational closings
    closings = ['bye', 'goodbye', 'see you', 'thanks', 'thank you', 'ok', 'okay', 'good', 'great']
    if any(text == c for c in closings):
        return True, "neutral"
        
    # Frustration/negative sentiment
    frustration = ['stupid', 'dumb', 'useless', 'bad', 'worst', 'hate', 'wrong', 'incorrect', 'hallucinating']
    if any(w in text for w in frustration):
        return False, "frustrated"  # Still need database, but sentiment detected
        
    return False, "neutral"

async def get_portfolio_context(query: str) -> str:
    """
    Smart RAG retrieval with keyword-based collection routing.
    """
    all_context = []
    query_lower = query.lower()
    
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
        
    def detect_intent(q: str) -> str:
        """
        Classify user query intent to optimize RAG retrieval scope.
        Returns: 'projects', 'aws_projects', 'blogs', or 'profile'
        """
        q = q.lower()
        
        # 1. AWS / Cloud Projects (Specific Subset)
        if any(k in q for k in ["aws", "cloud", "terraform", "infrastructure", "devops", "deploy"]):
            return "aws_projects"
            
        # 2. General Projects
        if any(k in q for k in ["project", "projects", "built", "worked on", "developed", "portfolio", "showcase"]):
            return "projects"
            
        # 3. Blogs / Writing
        if any(k in q for k in ["blog", "article", "write-up", "post", "writing", "published"]):
            return "blogs"
            
        # 4. Default: Profile / Personal Info
        return "profile"

    # --- INTENT-BASED ROUTING ---
    intent = detect_intent(query)
    logger.info(f"🧠 Detected Intent: {intent.upper()}")
    
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
        
        for collection_name in collections_to_query:
            try:
                collection = chroma_client.get_collection(
                    name=collection_name,
                    embedding_function=GeminiEmbeddingFunction()
                )
                
                # Intent-Specific Retrieval Parameters (Task 2)
                limit = 2
                search_query = query
                
                if intent == "aws_projects":
                    limit = 2
                    # Boost relevance for AWS queries
                    search_query = f"AWS Cloud Infrastructure {query}"
                elif intent == "projects":
                    limit = 3
                elif intent == "blogs":
                    limit = 2
                elif intent == "profile":
                    limit = 2  # Focus on key bio/skills ONLY
                
                logger.info(f"Querying {collection_name} | Limit: {limit} | Query: {search_query}")
                
                results = collection.query(query_texts=[search_query], n_results=limit)
                docs = results.get('documents', [[]])[0]
                
                if docs:
                    # Pre-Summarization Layer (Task 3)
                    summarized_docs = []
                    for d in docs:
                        if chatbot_provider:
                            # Compress raw doc into bullet points
                            summary = chatbot_provider.summarize_content(d)
                            summarized_docs.append(f"[Source: {collection_name}]\n{summary}")
                        else:
                            # Fallback if provider unavailable
                            summarized_docs.append(f"[Source: {collection_name}]\n{d[:800]}...")
                            
                    all_context.extend(summarized_docs)
            except Exception as e:
                logger.warning(f"Skipping collection {collection_name}: {e}")
                continue
        
        context_text = '\n\n'.join(all_context)
        logger.info(f"Retrieved context length: {len(context_text)} characters")
        return context_text
        
    except Exception as e:
        logger.error(f"ChromaDB Error: {e}")
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

# --- PUT (UPDATE) PROJECT ---
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

@api_router.get("/blogs")
async def get_blogs():
    try:
        from backend.read_local_blogs import get_local_blogs
        return get_local_blogs()
    except Exception:
        return []

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
        
        # Detect if greeting (skip RAG for simple greetings)
        is_greeting, sentiment = is_greeting_or_conversational(message)
        
        portfolio_context = ""
        if not is_greeting:
            portfolio_context = await get_portfolio_context(message)
            context_length = len(portfolio_context)
            logger.info(f"Retrieved context length: {context_length} characters")
        
        # Generate response using multi-provider system
        response_text = chatbot_provider.generate_response(
            query=message,
            context=portfolio_context,
            history=history
        )
        
        # Update conversation history (keep last 4 messages = 2 turns)
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": response_text})
        if len(history) > 4:
            history = history[-4:]
        conversation_sessions[session_id] = history
        
        # Cache successful response
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)