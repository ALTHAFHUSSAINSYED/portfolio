import google.generativeai as genai
from chromadb import EmbeddingFunction, Documents, Embeddings
# Configure Gemini for the Server
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# --- EMBEDDING FUNCTION FOR SERVER ---
class GeminiEmbeddingFunction(EmbeddingFunction):
    def __call__(self, input: Documents) -> Embeddings:
        # Note: We use 'retrieval_query' here because the user is ASKING a question
        return [
            genai.embed_content(
                model='models/text-embedding-004',
                content=text,
                task_type="retrieval_query" 
            )['embedding']
            for text in input
        ]
# backend/server.py - Cleaned & Fixed
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
from fastapi import Request
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
    # Define fallback for sanitize_html if import fails
    def sanitize_html(text):
        return bleach.clean(text)

# Security middleware with fallback
try:
    from backend.security_utils import SecurityHeadersMiddleware, HTTPSRedirectMiddleware
    HAS_SECURITY_MIDDLEWARE = True
except ImportError:
    SecurityHeadersMiddleware = None
    HTTPSRedirectMiddleware = None
    HAS_SECURITY_MIDDLEWARE = False
    print("⚠️ Warning: Security middleware not available")

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

# AI / Embedding Setup
embedding_model = None  # Disabled as per your previous config to save RAM

# Scheduler Setup
scheduler = AsyncIOScheduler()

# --- SCHEDULED BLOG GENERATION ---
async def scheduled_blog_generation():
    try:
        print("\n" + "="*50)
        print("🚀 Starting scheduled blog generation at", datetime.now(timezone.utc))
        print("="*50 + "\n")
        logger.info("Starting scheduled blog generation at %s", datetime.now(timezone.utc))
        
        # Generate blog content
        topic = "Latest Trends in AI and Machine Learning"
        content = gemini_service.generate_blog_post(topic)
        
        if content:
            # Add metadata
            blog_data = {
                "title": content["title"],
                "content": content["content"],
                "author": "Allu Bot",
                "createdAt": datetime.now(timezone.utc),
                "tags": content.get("tags", ["AI", "Machine Learning", "Technology"]),
                "_id": "auto-" + datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
            }
            
            # Send success notification
            await notification_service.send_blog_notification(True, blog_data)
            logger.info("Blog generation and notification successful")
            
            # Display success message
            print("\n" + "="*50)
            print("✅ BLOG POSTED SUCCESSFULLY!")
            print(f"📝 Title: {blog_data['title']}")
            print(f"📧 Email sent to: {notification_service.to_email}")
            print(f"🔗 Blog ID: {blog_data['_id']}")
            print("="*50 + "\n")
        else:
            await notification_service.send_blog_notification(False, None, "Blog generation failed - no content generated")
            logger.error("Blog generation failed - no content generated")
            
            # Display error message
            print("\n" + "="*50)
            print("❌ BLOG GENERATION FAILED!")
            print("Reason: No content was generated")
            print("="*50 + "\n")
    except Exception as e:
        error_msg = f"Error in scheduled blog generation: {str(e)}"
        logger.error(error_msg)
        await notification_service.send_blog_notification(False, None, error_msg)
        
        # Display error message
        print("\n" + "="*50)
        print("❌ BLOG GENERATION FAILED!")
        print(f"Reason: {error_msg}")
        print("="*50 + "\n")

# --- LIFESPAN MANAGER (Startup/Shutdown) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting Scheduler...")
    
    # Schedule blog generation job
    production_cron = CronTrigger(hour=1, minute=0, timezone=timezone.utc)
    scheduler.add_job(scheduled_blog_generation, production_cron)
    scheduler.start()
    
    # Start Agent Thread
    if HAS_AGENT_SERVICE:
        threading.Thread(target=agent_service.initialize_agent, daemon=True).start()
    
    yield
    # Shutdown
    print("🛑 Shutting down Scheduler...")
    scheduler.shutdown()

# --- APP INSTANCE ---
app = FastAPI(title="Portfolio API", version="1.0.0", lifespan=lifespan)
api_router = APIRouter(prefix="/api")

# --- MIDDLEWARE (Order Matters!) ---
# 1. Security Headers (if available)
if HAS_SECURITY_MIDDLEWARE and SecurityHeadersMiddleware:
    app.add_middleware(SecurityHeadersMiddleware)

# 2. CORS (CRITICAL FIX: Explicitly handle origins)
# Get origins from env, defaulting to your known domains if missing
default_origins = "http://localhost:3000,https://www.althafportfolio.site,https://althafportfolio.site,https://api.althafportfolio.site"
origins_env = os.environ.get('CORS_ORIGINS', default_origins)
origins = [origin.strip() for origin in origins_env.split(',') if origin.strip()]

print(f"🌍 CORS Allowed Origins: {origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Explicit list instead of '*'
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
    challenges: List[str] = []
    solutions: List[str] = []
    outcomes: List[str] = []
    github_url: Optional[str] = None
    live_url: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class BlogPostRequest(BaseModel):
    topic: Optional[str] = None

class BlogPost(BaseModel):
    id: Optional[str] = None
    title: str
    content: str
    tags: List[str]
    created_at: Union[datetime, str]
    summary: str
    published: bool = True

# --- HELPER FUNCTIONS ---
async def get_portfolio_context(query: str) -> str:
    """Retrieve relevant context from ALL portfolio ChromaDB collections"""
    all_context = []
    SIMILARITY_THRESHOLD = 0.3
    
    try:
        # Get ChromaDB credentials
        chroma_api_key = os.getenv('CHROMA_API_KEY')
        chroma_tenant = os.getenv('CHROMA_TENANT') or os.getenv('CHROMA_TENANT_ID')
        chroma_database = os.getenv('CHROMA_DATABASE')
        
        if not (chroma_api_key and chroma_tenant and chroma_database):
            logging.error("ChromaDB credentials missing")
            return ""
            
        chroma_client = chromadb.CloudClient(
            api_key=chroma_api_key,
            tenant=chroma_tenant,
            database=chroma_database
        )
        

        # Search ALL 3 collections
        collection_names = ['portfolio', 'Blogs_data', 'Projects_data']
        
        for collection_name in collection_names:
            try:
                # UPDATED: Connect using our custom Gemini Function
                collection = chroma_client.get_collection(
                    name=collection_name,
                    embedding_function=GeminiEmbeddingFunction()
                )
                
                # UPDATED: Perform the query
                # ChromaDB handles the embedding automatically using the function above
                results = collection.query(
                    query_texts=[query], 
                    n_results=10
                )
                
                # Apply similarity threshold
                docs = results.get('documents', [[]])[0]
                distances = results.get('distances', [[]])[0]
                
                # ... (Keep the rest of your filtering logic here) ...
                filtered_docs = []
                for i, (doc, dist) in enumerate(zip(docs, distances)):
                    logging.info(f"{collection_name} result {i+1}: distance={dist:.4f}, doc_preview={doc[:80]}...")
                    if dist < 1.3:
                        filtered_docs.append(doc)
                        logging.info(f"  ACCEPTED (distance={dist:.4f})")
                    else:
                        logging.info(f"  REJECTED (distance={dist:.4f} >= 1.3)")
                if not filtered_docs and docs:
                    fallback_docs = docs[:min(3, len(docs))]
                    filtered_docs.extend(fallback_docs)
                    logging.info(f"No items under threshold for {collection_name}; including top {len(fallback_docs)} result(s)")
                if filtered_docs:
                    all_context.extend(filtered_docs)
                    logging.info(f"Found {len(filtered_docs)} relevant results in {collection_name}")
                else:
                    logging.info(f"No relevant results in {collection_name}")
            except Exception as e:
                logging.error(f"Error accessing {collection_name}: {e}")
                continue
        
        if all_context:
            context_str = '\n\n---\n\n'.join(all_context)
            logging.info(f"Total context retrieved: {len(context_str)} chars from {len(all_context)} documents")
            return context_str
        else:
            logging.warning(f"No relevant context found for query: {query}")
            
    except Exception as e:
        logging.error(f"ChromaDB connection error: {e}")
    
    return ""

# --- ENDPOINTS ---

@app.get("/")
def welcome():
    return {"message": "Server is running. API is at /api"}

@app.post("/trigger-blog-generation")
async def trigger_blog_generation():
    await scheduled_blog_generation()
    return {"status": "Triggered blog generation and notification"}

# --- Helper: Trigger portfolio sync after relevant changes ---
def trigger_portfolio_sync():
    try:
        result = subprocess.run([sys.executable, "backend/sync_complete_portfolio.py"], capture_output=True, text=True)
        logger.info(f"Portfolio sync triggered. Output: {result.stdout}")
    except Exception as e:
        logger.error(f"Failed to trigger portfolio sync: {e}")

@api_router.get("/projects", response_model=List[Project])
async def get_projects():
    """
    Load projects directly from local portfolio_data.json
    Bypasses MongoDB to ensure data structure is perfect.
    """
    try:
        # 1. Locate the file
        json_path = ROOT_DIR / 'portfolio_data_complete.json'
        if not json_path.exists():
            json_path = Path('backend/portfolio_data_complete.json')
        if not json_path.exists():
            logger.error("portfolio_data_complete.json not found")
            return []

        # 2. Read the file
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        raw_projects = data.get('projects', [])
        clean_projects = []

        # 3. Map JSON to Pydantic Model
        for p in raw_projects:
            clean_projects.append({
                "id": str(p.get("id", uuid.uuid4())),
                "name": p.get("title", "Untitled"),
                "title": p.get("title", "Untitled"),
                "summary": p.get("description", ""),
                "description": p.get("description", ""),
                "details": p.get("description", ""),
                "image_url": p.get("image_url", ""),
                "category": p.get("category", ""),
                "technologies": p.get("technologies", []),
                "challenges": p.get("challenges", []),
                "solutions": p.get("solutions", []),
                "achievements": p.get("achievements", []),
                "duration": p.get("duration", ""),
                "role": p.get("role", ""),
                "teamSize": p.get("teamSize", ""),
                "github_url": p.get("github_url", ""),
                "live_url": p.get("live_url", ""),
                "timestamp": p.get("timestamp", datetime.utcnow())
            })

        logger.info(f"Loaded {len(clean_projects)} projects from local file.")
        return clean_projects

    except Exception as e:
        logger.error(f"Error reading local projects: {e}")
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
    # Upload to Cloudinary
    try:
        upload_result = cloudinary.uploader.upload(file.file, folder="portfolio_projects")
        image_url = upload_result.get("secure_url")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image upload failed: {str(e)}")

    project_data = {
        "id": str(uuid.uuid4()),
        "name": bleach.clean(name),
        "summary": bleach.clean(summary),
        "details": sanitize_html(details),
        "image_url": image_url,
        "technologies": [t.strip() for t in bleach.clean(technologies).split(',')],
        "key_outcomes": bleach.clean(key_outcomes),
        "timestamp": datetime.utcnow()
    }
    await db.projects.insert_one(project_data)
    # Trigger project sync (only for new project)
    try:
        result = subprocess.run([sys.executable, "backend/sync_projects.py"], capture_output=True, text=True)
        logger.info(f"Project sync triggered. Output: {result.stdout}")
    except Exception as e:
        logger.error(f"Failed to trigger project sync: {e}")
    return project_data

@api_router.post("/contact")
async def send_contact_email(form: ContactForm):
    try:
        response = await notification_service.send_contact_email(form)
        trigger_portfolio_sync()
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
        # Trigger blog sync (only for new blog)
        try:
            result = subprocess.run([sys.executable, "backend/migrate_local_blogs_new.py"], capture_output=True, text=True)
            logger.info(f"Blog sync triggered. Output: {result.stdout}")
        except Exception as e:
            logger.error(f"Failed to trigger blog sync: {e}")
        return blog
    except Exception as e:
        logger.error(f"Blog generation error: {e}")
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
    """Corporate RAG Chatbot: Strict RAG with Gemma 3"""
    if not ChatbotQuery:
        # Fallback if model not available
        message = query.get('message', '')
    else:
        query_obj = ChatbotQuery(**query)
        message = query_obj.message
    
    try:
        # Step 1: Retrieve ONLY relevant data from ChromaDB
        portfolio_context = await get_portfolio_context(message)
        
        logging.info(f"ChromaDB retrieval for '{message[:50]}...': {len(portfolio_context) if portfolio_context else 0} chars")

        # Step 2: Configure Gemma 3
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        
        generation_config = genai.GenerationConfig(
            temperature=0.3,
            top_p=0.95,
            top_k=20,
            max_output_tokens=1024,
        )
        
        model = genai.GenerativeModel(
            'models/gemma-3-27b-it',
            generation_config=generation_config
        )

        # Step 3: Build STRICT system prompt
        system_instruction = f"""You are Allu Bot, the professional portfolio assistant for Althaf Hussain Syed.

CRITICAL RULES:
1. You are a TRANSLATOR, not a knowledge source
2. Your ONLY job: Convert the raw Context below into polished, professional sentences
3. DO NOT add facts, assumptions, or external knowledge
4. If the Context doesn't answer the question, say: "I don't have that specific information in my knowledge base, but I can tell you about Althaf's skills, projects, and experience."
5. Write in a friendly, professional tone
6. Use bullet points for lists
7. DO NOT say "Based on the context" - speak as if you ARE the portfolio

RAW CONTEXT (Your ONLY source of truth):
{portfolio_context}

Remember: Rewrite this data into nice sentences. Do NOT invent new facts."""

        # Step 4: Generate human-like response
        user_prompt = f"User Question: {message}\n\nRewrite the Context into a polished, professional answer:"
        full_prompt = f"{system_instruction}\n\n{user_prompt}"
        
        response = model.generate_content(full_prompt)

        if response.text:
            logging.info(f"Successfully processed RAG query: {message[:100]}")
            return JSONResponse(
                status_code=200,
                content={
                    "reply": response.text,
                    "source": "Portfolio"
                }
            )
        else:
            raise Exception("Empty response from Gemma")
            
    except Exception as e:
        logging.error(f"Error in chatbot: {e}")
        return JSONResponse(
            status_code=500,
            content={"reply": f"Error processing your request: {str(e)}", "source": None}
        )

# --- REGISTER ROUTER ---
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
