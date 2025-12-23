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
        
        # Smart Collection Routing based on keywords
        collections_to_query = set()
        
        # Always query portfolio (general info, skills, experience, contact)
        collections_to_query.add('portfolio')
        
        # Query Projects_data if project-related keywords detected
        project_keywords = ['project', 'projects', 'built', 'developed', 'app', 'application', 'work', 'portfolio']
        if any(keyword in query_lower for keyword in project_keywords):
            collections_to_query.add('Projects_data')
        
        # Query Blogs_data if blog-related keywords detected
        blog_keywords = ['blog', 'blogs', 'article', 'articles', 'write', 'writing', 'post', 'recent']
        if any(keyword in query_lower for keyword in blog_keywords):
            collections_to_query.add('Blogs_data')
        
        # Fallback: If no specific keywords, query all collections lightly
        if len(collections_to_query) == 1:  # Only portfolio
            collections_to_query.add('Projects_data')
            collections_to_query.add('Blogs_data')
        
        for collection_name in collections_to_query:
            try:
                collection = chroma_client.get_collection(
                    name=collection_name,
                    embedding_function=GeminiEmbeddingFunction()
                )
                
                # Limit based on collection type
                if collection_name == 'portfolio':
                    limit = 15  # Comprehensive coverage
                elif collection_name == 'Projects_data':
                    limit = 3   # Top 3 projects
                else:  # Blogs_data
                    limit = 3   # Top 3 blogs
                
                results = collection.query(query_texts=[query], n_results=limit)
                docs = results.get('documents', [[]])[0]
                
                if docs:
                    # Label context with source
                    labeled_docs = [f"[Source: {collection_name}]\n{d}" for d in docs]
                    all_context.extend(labeled_docs)
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
    Enterprise-grade chatbot endpoint with strict no-hallucination rules.
    """
    message = query.get('message', '')
    
    if not message:
        return JSONResponse(
            status_code=400,
            content={"reply": "I'm listening. How can I help you with Althaf's portfolio?"}
        )
    
    try:
        # Detect if message is a greeting or conversational
        is_greeting, sentiment = is_greeting_or_conversational(message)
        
        portfolio_context = ""
        
        # Skip database for simple greetings
        if not is_greeting:
            portfolio_context = await get_portfolio_context(message)
        
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        
        # Enterprise-Grade System Prompt (Based on Flask Template)
        system_instruction = f"""You are **Allu Bot**, a high-end enterprise AI assistant for **Althaf Hussain Syed**.

### CORE IDENTITY:
* **'He', 'Him', or 'The Developer'** ALWAYS refers to **Althaf Hussain Syed**.
* You are an assistant, NOT Althaf. Speak about him in third person.

### CONTEXT & KNOWLEDGE:
{portfolio_context if portfolio_context else "No specific database info retrieved for this query. Handle as conversational turn or inform user you need portfolio-specific questions."}

### USER SENTIMENT: {sentiment.upper()}
* **If FRUSTRATED:** Be deeply empathetic and apologetic. Acknowledge the mistake and try to provide correct information.
* **If NEUTRAL/HAPPY:** Be professional, energetic, and helpful.

### STRICT RULES (NO EXCEPTIONS):

1. **ZERO HALLUCINATION:**
   - Answer ONLY from the 'CONTEXT & KNOWLEDGE' provided above
   - If information is missing from context, say: "I don't have that specific detail in Althaf's portfolio database. Could you rephrase or ask something else?"
   - NEVER invent skills, projects, certifications, or contact details

2. **SPECIFIC ANSWERS:**
   - For skills: List actual tools (Docker, Kubernetes, Terraform, Jenkins, etc.), NOT generic terms like "Cloud Computing"
   - For projects: Give project names and tech stacks from context
   - For certifications: Provide exact count and names (AWS, GCP, Azure certifications)
   - For contact: Provide actual email, phone, LinkedIn from context

3. **GREETING HANDLING:**
   - For simple greetings (Hi, Hello): Respond warmly without needing database data
   - Example: "Hello! I'm Allu Bot, Althaf's portfolio assistant. How can I help you learn about his DevOps experience and projects?"

4. **CONVERSATIONAL CONTEXT:**
   - "What are those?" "Tell me more" "Which ones?" → Infer from previous context in conversation
   - If you cannot infer, ask user to clarify

5. **REFUSAL LOGIC (ONLY for truly irrelevant questions):**
   - Refuse ONLY if user asks completely unrelated factual questions (e.g., "Capital of Mars", "Recipe for pizza")
   - DO NOT refuse valid portfolio questions like: resume, contact number, LinkedIn, certifications list, project details
   - Refusal message: "Sorry, the question asked is not related to the portfolio. I can't answer that question. Try something portfolio-related."

6. **FORMATTING:**
   - Write in smooth, natural paragraphs
   - NO word hyphenation at line ends
   - Use bullet points for lists (skills, certifications, achievements)
   - Keep responses professional but conversational

7. **ROUTING:**
   - Project questions → Focus on technical stack, implementation, outcomes
   - Blog questions → Summarize writing topics and technical content
   - Skills questions → Be specific with tools and technologies
   - Experience questions → Highlight role, responsibilities, achievements

Now, respond to the user's message based on the above rules and context."""

        # Generate Response with Fallback
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(f"{system_instruction}\\nUser: {message}")
        except Exception as e:
            logger.warning(f"Primary model failed ({e}). Using Gemma 12B fallback")
            model = genai.GenerativeModel('gemma-3-12b-it')
            response = model.generate_content(f"{system_instruction}\\nUser: {message}")
        
        return JSONResponse(
            status_code=200,
            content={"reply": response.text, "source": "Portfolio"}
        )
        
    except Exception as e:
        logger.error(f"Error in ask_agent: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"reply": "I apologize, but I encountered a system error. Please try again.", "source": None}
        )

app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)