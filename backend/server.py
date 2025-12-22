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

# Local imports
try:
    from backend import agent_service
    from backend.ai_service import gemini_service
    from backend.notification_service import notification_service
    from backend.security_utils import sanitize_html
    from backend.models import ChatbotQuery
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

# --- EMBEDDING FUNCTION FOR SERVER ---
class GeminiEmbeddingFunction(EmbeddingFunction):
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

# --- SCHEDULED BLOG GENERATION ---
async def scheduled_blog_generation():
    try:
        logger.info("Starting scheduled blog generation")
        topic = "Latest Trends in AI and Machine Learning"
        content = gemini_service.generate_blog_post(topic)
        
        if content:
            blog_data = {
                "title": content["title"],
                "content": content["content"],
                "author": "Allu Bot",
                "createdAt": datetime.now(timezone.utc),
                "tags": content.get("tags", ["AI", "Technology"]),
                "_id": "auto-" + datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
            }
            await notification_service.send_blog_notification(True, blog_data)
            logger.info("✅ Blog posted successfully!")
        else:
            logger.error("❌ Blog generation failed - no content")
    except Exception as e:
        logger.error(f"Error in blog generation: {e}")

# --- LIFESPAN MANAGER ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting Scheduler...")
    production_cron = CronTrigger(hour=1, minute=0, timezone=timezone.utc)
    scheduler.add_job(scheduled_blog_generation, production_cron)
    scheduler.start()
    
    if HAS_AGENT_SERVICE:
        threading.Thread(target=agent_service.initialize_agent, daemon=True).start()
    
    yield
    print("🛑 Shutting down Scheduler...")
    scheduler.shutdown()

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
    key_outcomes: Optional[str] = ""
    github_url: Optional[str] = None
    live_url: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class BlogPostRequest(BaseModel):
    topic: Optional[str] = None

# --- HELPER FUNCTIONS ---
async def get_portfolio_context(query: str) -> str:
    all_context = []
    try:
        chroma_api_key = os.getenv('CHROMA_API_KEY')
        chroma_tenant = os.getenv('CHROMA_TENANT') or os.getenv('CHROMA_TENANT_ID')
        chroma_database = os.getenv('CHROMA_DATABASE')
        
        if not (chroma_api_key and chroma_tenant and chroma_database):
            return ""
            
        chroma_client = chromadb.CloudClient(
            api_key=chroma_api_key,
            tenant=chroma_tenant,
            database=chroma_database
        )
        
        collection_names = ['portfolio', 'Blogs_data', 'Projects_data']
        
        for collection_name in collection_names:
            try:
                collection = chroma_client.get_collection(
                    name=collection_name,
                    embedding_function=GeminiEmbeddingFunction()
                )
                results = collection.query(query_texts=[query], n_results=5)
                docs = results.get('documents', [[]])[0]
                all_context.extend(docs)
            except Exception as e:
                logger.warning(f"Skipping collection {collection_name}: {e}")
                continue
        
        return '\n\n'.join(all_context)
    except Exception as e:
        logger.error(f"ChromaDB Error: {e}")
        return ""

# --- ENDPOINTS ---

@app.get("/")
def welcome():
    return {"message": "Server is running. API is at /api"}

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
                    from bson import ObjectId
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
    message = query.get('message', '')
    try:
        portfolio_context = await get_portfolio_context(message)
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        model = genai.GenerativeModel('models/gemma-3-27b-it')
        
        system_instruction = f"""You are Allu Bot, the professional portfolio assistant for Althaf Hussain Syed.
        Use this Context to answer: {portfolio_context}
        If unknown, say you don't have that info."""
        
        response = model.generate_content(f"{system_instruction}\nUser: {message}")
        
        return JSONResponse(status_code=200, content={"reply": response.text, "source": "Portfolio"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"reply": f"Error: {str(e)}", "source": None})

app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)