# backend.py - Portfolio Backend Server with Chatbot API

from fastapi import FastAPI, APIRouter, UploadFile, File, Form, HTTPException, status, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

# Import scheduling libraries
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timezone
import logging
import sys
import json

# Configure logging
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S UTC',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('BlogScheduler')

# Create FastAPI app instance
app = FastAPI(title="Portfolio Backend API", version="1.0.0")

# Manual trigger endpoint for blog generation and notification
@app.post("/trigger-blog-generation")
async def trigger_blog_generation():
    await scheduled_blog_generation()
    return {"status": "Triggered blog generation and notification"}
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
import aiohttp
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, From, To, Subject, Content, ReplyTo
import bleach
import os
import logging
import threading
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any, Union
import uuid
from datetime import datetime
import base64
import shutil
import json
import re
import requests
from sentence_transformers import SentenceTransformer

# Initialize embedding model globally to avoid reloading on every request
try:
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
except Exception as e:
    print(f"Warning: Could not load SentenceTransformer: {e}")
    embedding_model = None
from bs4 import BeautifulSoup
import chromadb
import google.generativeai as genai
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import cloudinary
import cloudinary.uploader

# Import required services
from backend import agent_service
from backend.ai_service import gemini_service
from backend import test_blog_generation
from backend.notification_service import notification_service
HAS_AGENT_SERVICE = True

from datetime import timedelta
scheduler = AsyncIOScheduler()

production_cron = CronTrigger(hour=1, minute=0, timezone=timezone.utc)





@app.on_event("startup")
async def start_scheduler():
    # Register scheduled blog generation job
    production_cron = CronTrigger(hour=9, minute=40, timezone=timezone.utc)
    scheduler.add_job(scheduled_blog_generation, production_cron)
    scheduler.start()

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

@app.on_event("startup")
async def setup_scheduled_tasks():
    """Setup scheduled tasks on application startup."""
    # Schedule blog generation in 2 minutes for testing
    # Removed undefined generate_daily_blog job to prevent runtime error
    pass
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

async def get_portfolio_context(query: str) -> str:
    """Retrieve relevant context from ALL portfolio ChromaDB collections with similarity threshold."""
    all_context = []
    SIMILARITY_THRESHOLD = 0.3  # Lower threshold - ChromaDB uses different distance metrics
    
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
                collection = chroma_client.get_collection(name=collection_name)
                
                # Use embedding model if available, otherwise text search
                # Fetch more results to ensure complete data coverage (all certs, skills, projects)
                if embedding_model:
                    embedding = embedding_model.encode([query]).tolist()
                    results = collection.query(query_embeddings=embedding, n_results=15)
                else:
                    results = collection.query(query_texts=[query], n_results=15)
                
                # Apply similarity threshold
                docs = results.get('documents', [[]])[0]
                distances = results.get('distances', [[]])[0]
                
                # Filter by similarity (lower distance = higher similarity)
                # ChromaDB returns squared euclidean distance, not cosine
                filtered_docs = []
                for i, (doc, dist) in enumerate(zip(docs, distances)):
                    # Log actual distance for debugging
                    logging.info(f"{collection_name} result {i+1}: distance={dist:.4f}, doc_preview={doc[:80]}...")
                    
                    # Keep results with reasonably low distance
                    # Based on logs: 1.08-1.25 are very relevant results
                    if dist < 1.3:  # Accept results with distance < 1.3
                        filtered_docs.append(doc)
                        logging.info(f"  ✅ ACCEPTED (distance={dist:.4f})")
                    else:
                        logging.info(f"  ❌ REJECTED (distance={dist:.4f} >= 1.3)")
                
                if filtered_docs:
                    all_context.extend(filtered_docs)
                    logging.info(f"Found {len(filtered_docs)} relevant results in {collection_name}")
                else:
                    logging.info(f"No relevant results in {collection_name} (all below threshold)")
                    
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

try:
    # Use html.escape for escaping
    import html
    def escape(s):
        """Replacement for deprecated cgi.escape"""
        return html.escape(s, quote=False)
    import feedparser
except ImportError:
    import subprocess
    import sys
    print("Installing feedparser package...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "feedparser"])
    import feedparser

# --- SETUP ---
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# --- DATABASE CONNECTION ---
mongo_url = os.environ.get('MONGO_URL')
db_name = os.environ.get('DB_NAME', 'portfolioDB')  # Use portfolioDB as the default database name

# Configure MongoDB client and database with proper error handling
if not mongo_url:
    print("Warning: MONGO_URL environment variable is not set. Database functionality will be limited.")
    client = None
    db = None
else:
    try:
        client = AsyncIOMotorClient(mongo_url)
        if not db_name:
            print("Warning: DB_NAME environment variable is not set. Using default 'portfolio' database.")
        db = client[db_name]
        print(f"Successfully connected to MongoDB database: {db_name}")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        client = None
        db = None

# ✨ --- NEW: CONFIGURE CLOUDINARY --- ✨
# This section reads your .env file and sets up Cloudinary
cloudinary.config(
    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key = os.environ.get('CLOUDINARY_API_KEY'),
    api_secret = os.environ.get('CLOUDINARY_API_SECRET'),
    secure=True
)

# Import security utilities
from backend.security_utils import sanitize_html, sanitize_input_dict, HTTPSRedirectMiddleware, SecurityHeadersMiddleware

# --- FASTAPI APP INSTANCE ---
app = FastAPI(title="Portfolio API")
api_router = APIRouter(prefix="/api")

# --- Add Security Middleware ---
# Enable HTTPS redirect in production, disable in development
# Note: Disabled because nginx handles HTTPS termination
is_production = os.environ.get("ENVIRONMENT", "development").lower() == "production"
app.add_middleware(HTTPSRedirectMiddleware, enabled=False)  # Disabled - nginx handles HTTPS
app.add_middleware(SecurityHeadersMiddleware)

# Note: CORS middleware is added later with environment-based configuration

# --- PYDANTIC MODELS ---
# (No changes here)
class ContactForm(BaseModel):
    name: str = Field(...)
    email: EmailStr = Field(...)
    subject: Optional[str] = None
    message: str = Field(...)

class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    summary: str
    details: str
    image_url: str
    technologies: List[str] = []
    key_outcomes: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class UpdateProjectModel(BaseModel):
    name: Optional[str] = None
    summary: Optional[str] = None
    details: Optional[str] = None
    image_url: Optional[str] = None
    technologies: Optional[List[str]] = None
    key_outcomes: Optional[str] = None

# --- API ENDPOINTS ---

# (No changes to your contact form)
@api_router.post("/contact")
async def send_contact_email(form: ContactForm):
    to_email = os.environ.get('TO_EMAIL')
    sendgrid_api_key = os.environ.get('SENDGRID_API_KEY')

    if not to_email or not sendgrid_api_key:
        raise HTTPException(status_code=500, detail="Server is not configured for sending emails.")
    
    # Sanitize inputs to prevent XSS
    sanitized_name = bleach.clean(form.name)
    sanitized_subject = bleach.clean(form.subject) if form.subject else None
    sanitized_message = bleach.clean(form.message)
    
    # Use sanitized inputs
    final_subject = sanitized_subject if sanitized_subject else f"New portfolio message from {sanitized_name}"
    html_content = f"""
    <h3>New Contact Form Submission</h3>
    <p><strong>Name:</strong> {sanitized_name}</p>
    <p><strong>Email:</strong> {form.email}</p>
    <p><strong>Subject:</strong> {sanitized_subject or 'No Subject Provided'}</p>
    <p><strong>Message:</strong></p>
    <p>{sanitized_message}</p>
    """
    
    message = Mail(
        from_email=From(to_email, form.name),
        to_emails=To(to_email),
        subject=Subject(final_subject),
        html_content=Content("text/html", html_content)
    )
    message.reply_to = ReplyTo(form.email, form.name)

    try:
        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(message)
        if 200 <= response.status_code < 300:
            return {"message": "Email sent successfully!"}
        else:
            logging.error(f"SendGrid error: {response.status_code} {response.body}")
            raise HTTPException(status_code=500, detail="Failed to send email.")
    except Exception as e:
        logging.error(f"Error sending email: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while sending the email.")


# ✨ --- MODIFIED: The create_project endpoint --- ✨
@api_router.post("/projects", response_model=Project, status_code=status.HTTP_201_CREATED)
async def create_project(name: str = Form(...), summary: str = Form(...), details: str = Form(...), technologies: str = Form(...), key_outcomes: str = Form(...), file: UploadFile = File(...)):
    # Check if database is available
    if db is None:
        raise HTTPException(status_code=503, detail="Database is not available. Check your MongoDB connection.")
        
    # Sanitize all user inputs to prevent XSS attacks
    sanitized_name = bleach.clean(name)
    sanitized_summary = bleach.clean(summary)
    # Allow specific HTML tags in details for formatting
    sanitized_details = sanitize_html(details)  
    sanitized_tech = bleach.clean(technologies)
    sanitized_key_outcomes = bleach.clean(key_outcomes)
    
    tech_list = [tech.strip() for tech in sanitized_tech.split(',') if tech.strip()]
    
    # Upload file to Cloudinary
    try:
        upload_result = cloudinary.uploader.upload(file.file, folder="portfolio_projects")
        image_url = upload_result.get("secure_url") # Get the HTTPS URL
    except Exception as e:
        logging.error(f"Cloudinary upload failed: {e}")
        raise HTTPException(status_code=500, detail="Image could not be uploaded.")

    project_data = {
        "name": sanitized_name, 
        "summary": sanitized_summary, 
        "details": sanitized_details, 
        "image_url": image_url, 
        "technologies": tech_list, 
        "key_outcomes": sanitized_key_outcomes
    }
    project = Project(**project_data)
    
    try:
        await db.projects.insert_one(project.model_dump())
        return project
    except Exception as e:
        logging.error(f"Database error when creating project: {e}")
        raise HTTPException(status_code=500, detail="Failed to save project to database")

@api_router.get("/projects", response_model=List[Project])
async def get_projects():
    # Always fallback to empty list if db is unavailable
    try:
        if db is not None:
            projects_cursor = db.projects.find()
            projects = await projects_cursor.to_list(length=100)
            return projects
        else:
            logging.warning("Database not available when fetching projects, returning empty list")
            return []
    except Exception as e:
        logging.error(f"Error fetching projects: {e}")
        return []

@api_router.get("/projects/{project_id}", response_model=Project)
async def get_project_by_id(project_id: str):
    # Check if database is available
    if db is None:
        raise HTTPException(
            status_code=503, 
            detail="Database is not available. Check your MongoDB connection."
        )
    
    try:
        project = await db.projects.find_one({"id": project_id})
        if project: 
            return project
        raise HTTPException(status_code=404, detail="Project not found")
    except Exception as e:
        logging.error(f"Error fetching project {project_id}: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving project from database")

@api_router.put("/projects/{project_id}", response_model=Project)
async def update_project(project_id: str, name: Optional[str] = Form(None), summary: Optional[str] = Form(None), details: Optional[str] = Form(None), technologies: Optional[str] = Form(None), key_outcomes: Optional[str] = Form(None), file: Optional[UploadFile] = File(None)):
    # Check if database is available
    if db is None:
        raise HTTPException(
            status_code=503, 
            detail="Database is not available. Check your MongoDB connection."
        )
    
    update_data = {}
    if name is not None: update_data["name"] = bleach.clean(name)
    if summary is not None: update_data["summary"] = bleach.clean(summary)
    if details is not None: update_data["details"] = sanitize_html(details)
    if technologies is not None: update_data["technologies"] = [bleach.clean(t.strip()) for t in technologies.split(',') if t.strip()]
    if key_outcomes is not None: update_data["key_outcomes"] = bleach.clean(key_outcomes)
    
    # If a new file is provided, upload it to Cloudinary
    if file:
        try:
            upload_result = cloudinary.uploader.upload(file.file, folder="portfolio_projects")
            update_data["image_url"] = upload_result.get("secure_url")
        except Exception as e:
            logging.error(f"Cloudinary upload failed on update: {e}")
            raise HTTPException(status_code=500, detail="Image could not be updated.")
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No update data provided")

    try:
        result = await db.projects.update_one({"id": project_id}, {"$set": update_data})
        
        if result.modified_count >= 0:
            updated_project = await db.projects.find_one({"id": project_id})
            if updated_project:
                return updated_project
        
        raise HTTPException(status_code=404, detail="Project not found")
    except Exception as e:
        logging.error(f"Database error when updating project {project_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update project in database")

@api_router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: str):
    # Check if database is available
    if db is None:
        raise HTTPException(
            status_code=503, 
            detail="Database is not available. Check your MongoDB connection."
        )
    
    try:
        result = await db.projects.delete_one({"id": project_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Project not found")
        return
    except Exception as e:
        logging.error(f"Database error when deleting project {project_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete project from database")

# --- AGENT API MODELS ---
class AgentQuery(BaseModel):
    message: str = Field(..., description="The message to send to the agent")
    context: Optional[str] = Field(None, description="Optional context to provide to the agent")

class BlogPostRequest(BaseModel):
    topic: Optional[str] = Field(None, description="Optional topic for the blog post")

class BlogPost(BaseModel):
    id: Optional[str] = None
    title: str
    content: str
    topic: str
    created_at: datetime
    tags: List[str]
    summary: str
    published: bool = True
    sources: Optional[List[str]] = None
    category: Optional[str] = None  # Added category field for blog classification

# --- AGENT API ENDPOINTS ---
from backend.models import ChatbotQuery

@api_router.post("/ask-all-u-bot")
async def ask_agent(query: ChatbotQuery):
    """Endpoint for the chatbot to ask questions with RAG system"""
    try:
        # Check for required environment variables
        required_vars = {
            "Gemini API": os.environ.get("GEMINI_API_KEY"),
            "Serper API": os.environ.get("SERPER_API_KEY"),
        }
        missing_vars = [key for key, value in required_vars.items() if not value]
        if missing_vars:
            missing_list = ", ".join(missing_vars)
            logging.warning(f"Missing required API keys: {missing_list}")
            return JSONResponse(
                status_code=200,
                content={
                    "reply": f"I have limited functionality right now because some API configurations are missing ({missing_list}). I can still try to help with basic questions.",
                    "source": None
                }
            )

        # Configure Gemini with STRICT settings (Corporate RAG)
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        
        # temperature=0 eliminates creativity/hallucinations
        generation_config = genai.GenerationConfig(
            temperature=0.0,
            top_p=0.95,
            top_k=20,
            max_output_tokens=1024,
        )
        model = genai.GenerativeModel(
            'models/gemini-1.5-flash',  # 1,500 requests/day (testing), can upgrade to 2.5-flash for production
            generation_config=generation_config
        )

        # Step 1: ALWAYS query ChromaDB (no exceptions)
        portfolio_context = await get_portfolio_context(query.message)
        
        # Log what we retrieved for debugging
        logging.info(f"ChromaDB retrieval for '{query.message[:50]}...': {len(portfolio_context) if portfolio_context else 0} chars")

        # Step 2: Check if we have RELEVANT context (strict threshold)
        if not portfolio_context or len(portfolio_context.strip()) < 20:
            # No relevant data found - refuse to answer
            return JSONResponse(
                status_code=200,
                content={
                    "reply": "I don't have information about that in Althaf's portfolio. I can only answer questions about Althaf Hussain Syed's professional experience, skills, projects, and certifications based on his portfolio data.",
                    "source": None
                }
            )

        # Step 3: Build STRICT system instruction (Corporate RAG)
        system_instruction = f"""You are 'Allu Bot', the official AI assistant for Althaf Hussain Syed's professional portfolio.

STRICT RULES (NO EXCEPTIONS):
1. You are FORBIDDEN from using your internal knowledge, training data, or the internet
2. You MUST answer SOLELY based on the 'Context' provided below
3. If the Context does not contain the answer, you MUST reply: "I don't have that information in my knowledge base"
4. Do NOT make assumptions, inferences, or add any information not explicitly in the Context
5. Do NOT say "Based on the context" - just answer directly as if you know this information
6. Keep answers professional, concise, and well-formatted

CONTEXT (Your ONLY source of truth):
{portfolio_context}

Remember: If it's not in the Context above, you don't know it. Period."""

        # Step 4: Build user prompt
        user_prompt = f"User Question: {query.message}\n\nAnswer using ONLY the Context provided in your system instruction:"

        # Step 5: Generate response (temperature=0 prevents creativity)
        response = model.generate_content(user_prompt, generation_config=generation_config)
        
        # Override system instruction by prepending it to prompt
        full_prompt = f"{system_instruction}\n\n{user_prompt}"
        response = model.generate_content(full_prompt)

        if response.text:
            # Log successful interaction
            logging.info(f"Successfully processed query: {query.message[:100]}...")
            return JSONResponse(
                status_code=200,
                content={
                    "reply": response.text,
                    "source": "Portfolio"
                }
            )
        else:
            raise Exception("Empty response from Gemini")
    except Exception as e:
        logging.error(f"Error in agent query: {e}")
        return JSONResponse(
            status_code=500,
            content={"reply": f"Error processing your request: {str(e)}", "source": None}
        )

@api_router.post("/generate-blog", response_model=BlogPost)
async def generate_blog(request: BlogPostRequest, background_tasks: BackgroundTasks):
    """Generate a new blog post on demand"""
    try:
        # Check for required environment variables
        required_vars = {
            "Gemini API": os.environ.get("GEMINI_API_KEY"),
            "MongoDB URL": os.environ.get("MONGO_URL") or os.environ.get("MONGODB_URI")
        }
        
        missing_vars = [key for key, value in required_vars.items() if not value]
        
        if missing_vars:
            missing_list = ", ".join(missing_vars)
            logging.warning(f"Missing required API keys for blog generation: {missing_list}")
        
        # Generate the blog post (will use fallback if APIs are missing)
        if HAS_AGENT_SERVICE:
            blog = agent_service.generate_blog_now(request.topic)
            if blog:
                # Convert MongoDB datetime to string for JSON serialization
                if isinstance(blog.get("created_at"), datetime):
                    blog["created_at"] = blog["created_at"].isoformat()
                return blog
        else:
            return JSONResponse(
                status_code=200,  # Return 200 to avoid frontend error handling
                content={
                    "title": f"Sample Blog: {request.topic or 'Technology Overview'}",
                    "content": "# Blog Generation Service\n\nThe blog generation service is currently unavailable. This may be due to missing API configurations.\n\n## Required Setup\n\nTo enable full blog generation capabilities, please configure the Gemini API and MongoDB connection.",
                    "summary": "Information about the blog generation service requirements.",
                    "tags": ["sample", "service", "configuration"],
                    "created_at": datetime.now().isoformat(),
                    "published": True
                }
            )
    except Exception as e:
        logging.error(f"Error generating blog: {e}")
        return JSONResponse(
            status_code=200,  # Return 200 to avoid frontend error handling
            content={
                "title": f"Sample Blog: {request.topic or 'Technology Overview'}",
                "content": "# Blog Generation Error\n\nThere was an error generating this blog post. This might be due to API configuration issues or service unavailability.\n\n## Error Details\n\nAn unexpected error occurred during blog generation. Please check the server logs for more information.",
                "summary": "Error information for blog generation service.",
                "tags": ["error", "service", "configuration"],
                "created_at": datetime.now().isoformat(),
                "published": True
            }
        )

@api_router.get("/blogs", response_model=List[BlogPost])
async def get_blogs():
    """Get all published blog posts"""
    # Always fallback to local blogs for reliability
    try:
        from backend.read_local_blogs import get_local_blogs
        local_blogs = get_local_blogs()
        if local_blogs:
            logging.info(f"Serving {len(local_blogs)} locally generated blog posts")
            return local_blogs
        else:
            logging.warning("No local blogs found, returning empty array")
            return []
    except Exception as e:
        logging.error(f"Error fetching local blogs: {e}")
        return []

@api_router.get("/blogs/{blog_id}", response_model=BlogPost)
async def get_blog(blog_id: str):
    """Get a specific blog post by ID"""
    # Check if database is available
    if db is None:
        raise HTTPException(
            status_code=503, 
            detail="Database is not available. Check your MongoDB connection."
        )
    
    try:
        from bson.objectid import ObjectId
        blog = await db.blogs.find_one({"_id": ObjectId(blog_id)})
        if blog:
            blog["id"] = str(blog.pop("_id"))
            return blog
        else:
            raise HTTPException(status_code=404, detail="Blog not found")
    except ValueError as e:
        # Handle invalid ObjectId format
        logging.error(f"Invalid blog ID format: {e}")
        raise HTTPException(status_code=400, detail="Invalid blog ID format")
    except Exception as e:
        logging.error(f"Error fetching blog: {e}")
        raise HTTPException(status_code=500, detail="Could not fetch blog post")

@api_router.post("/agent/start")
async def start_agent():
    """Start the agent scheduler"""
    if not HAS_AGENT_SERVICE:
        return JSONResponse(
            status_code=200,  # Using 200 to avoid frontend errors
            content={"message": "Agent service is not available in this deployment"}
        )
        
    try:
        success = agent_service.initialize_agent()
        if success:
            return {"status": "Agent scheduler started successfully"}
        else:
            return JSONResponse(
                status_code=400,
                content={"error": "Agent scheduler is already running"}
            )
    except Exception as e:
        logging.error(f"Error starting agent: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"An error occurred: {str(e)}"}
        )

# --- APP CONFIGURATION ---
app.include_router(api_router)

@app.get("/")
def welcome():
    return {"message": "Server is running. API is at /api"}

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Start the agent scheduler in a background thread ---
def start_agent_thread():
    if not HAS_AGENT_SERVICE:
        logging.info("Agent service is not available in this deployment. Skipping agent initialization.")
        return
        
    try:
        agent_service.initialize_agent()
        logging.info("Agent scheduler started successfully in background thread")
    except Exception as e:
        logging.error(f"Failed to start agent scheduler: {e}")

# Start the agent when the server starts
agent_thread = threading.Thread(target=start_agent_thread)
agent_thread.daemon = True
agent_thread.start()
if hasattr(app, 'scheduler_started'):
    delattr(app, 'scheduler_started')

# Lifespan context manager for the FastAPI app
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start scheduler
    scheduler.start()
    logging.info("Started main scheduler for blog generation")
    yield
    scheduler.shutdown()

app.router.lifespan_context = lifespan

# Start the server if this file is run directly
if __name__ == "__main__":
    import asyncio
    import nest_asyncio
    nest_asyncio.apply()
    async def main():
        print("Starting AsyncIOScheduler in standalone mode...")
        scheduler.start()
        while True:
            await asyncio.sleep(1)

    try:
        import nest_asyncio
        nest_asyncio.apply()
        loop = asyncio.get_event_loop()
        loop.create_task(main())
        loop.run_forever()
    except (KeyboardInterrupt, SystemExit):
        print("Shutting down scheduler...")
        scheduler.shutdown()
