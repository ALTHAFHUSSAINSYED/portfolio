# backend.py

from fastapi import FastAPI, APIRouter, UploadFile, File, Form, HTTPException, status, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
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
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
import base64
import shutil
import json
# ✨ --- NEW: IMPORT CLOUDINARY --- ✨
import cloudinary
import cloudinary.uploader
import cloudinary.api

# Import the agent service conditionally to make deployment more robust
try:
    import agent_service
    HAS_AGENT_SERVICE = True
except (ImportError, ValueError):
    print("Warning: agent_service could not be imported. Chat and AI features will be disabled.")
    HAS_AGENT_SERVICE = False

# Import feedparser and handle the cgi.escape dependency
try:
    # First try to import html module for escaping
    import html
    
    # Create a function to replace cgi.escape
    def escape(s):
        """Replacement for deprecated cgi.escape"""
        return html.escape(s, quote=False)
    
    # Try to import cgi module or create a mock
    try:
        import cgi
    except ImportError:
        # Create a mock cgi module with the escape function
        import types
        cgi = types.ModuleType('cgi')
        cgi.escape = escape
        import sys
        sys.modules['cgi'] = cgi
    
    # Now try to import feedparser
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
db_name = os.environ.get('DB_NAME')
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

# ✨ --- NEW: CONFIGURE CLOUDINARY --- ✨
# This section reads your .env file and sets up Cloudinary
cloudinary.config(
    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key = os.environ.get('CLOUDINARY_API_KEY'),
    api_secret = os.environ.get('CLOUDINARY_API_SECRET'),
    secure=True
)

# Import security utilities
from security_utils import sanitize_html, sanitize_input_dict, HTTPSRedirectMiddleware, SecurityHeadersMiddleware

# --- FASTAPI APP INSTANCE ---
app = FastAPI(title="Portfolio API")
api_router = APIRouter(prefix="/api")

# --- Add Security Middleware ---
# Enable HTTPS redirect in production, disable in development
is_production = os.environ.get("ENVIRONMENT", "development").lower() == "production"
app.add_middleware(HTTPSRedirectMiddleware, enabled=is_production)
app.add_middleware(SecurityHeadersMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Development frontend
        "https://yourdomain.com",  # Production frontend - replace with your actual domain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    await db.projects.insert_one(project.model_dump())
    return project

# (No changes to your get_projects endpoint)
@api_router.get("/projects", response_model=List[Project])
async def get_projects():
    projects_cursor = db.projects.find()
    projects = await projects_cursor.to_list(length=100)
    return projects

# (No changes to your get_project_by_id endpoint)
@api_router.get("/projects/{project_id}", response_model=Project)
async def get_project_by_id(project_id: str):
    project = await db.projects.find_one({"id": project_id})
    if project: return project
    raise HTTPException(status_code=404, detail="Project not found")

# ✨ --- MODIFIED: The update_project endpoint --- ✨
@api_router.put("/projects/{project_id}", response_model=Project)
async def update_project(project_id: str, name: Optional[str] = Form(None), summary: Optional[str] = Form(None), details: Optional[str] = Form(None), technologies: Optional[str] = Form(None), key_outcomes: Optional[str] = Form(None), file: Optional[UploadFile] = File(None)):
    update_data = {}
    if name is not None: update_data["name"] = name
    if summary is not None: update_data["summary"] = summary
    if details is not None: update_data["details"] = details
    if technologies is not None: update_data["technologies"] = [t.strip() for t in technologies.split(',') if t.strip()]
    if key_outcomes is not None: update_data["key_outcomes"] = key_outcomes
    
    # NEW: If a new file is provided, upload it to Cloudinary
    if file:
        try:
            upload_result = cloudinary.uploader.upload(file.file, folder="portfolio_projects")
            update_data["image_url"] = upload_result.get("secure_url")
        except Exception as e:
            logging.error(f"Cloudinary upload failed on update: {e}")
            raise HTTPException(status_code=500, detail="Image could not be updated.")

    # REMOVED: The old Base64 logic for file updates
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No update data provided")

    result = await db.projects.update_one({"id": project_id}, {"$set": update_data})
    
    # This logic remains the same
    if result.modified_count >= 0:
        updated_project = await db.projects.find_one({"id": project_id})
        if updated_project:
            return updated_project
    
    raise HTTPException(status_code=404, detail="Project not found")

# (No changes to your delete_project endpoint)
@api_router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: str):
    result = await db.projects.delete_one({"id": project_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    return

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
@api_router.post("/ask-all-u-bot")
async def ask_agent(query: AgentQuery):
    """Endpoint for the chatbot to ask questions to the agent with internet access"""
    try:
        # Check for required environment variables
        required_vars = {
            "Gemini API": os.environ.get("GEMINI_API_KEY"),
            "MongoDB URL": os.environ.get("MONGO_URL") or os.environ.get("MONGODB_URI")
        }
        
        missing_vars = [key for key, value in required_vars.items() if not value]
        
        if missing_vars:
            missing_list = ", ".join(missing_vars)
            logging.warning(f"Missing required API keys: {missing_list}")
            return JSONResponse(
                status_code=200,  # Return 200 to avoid frontend error handling
                content={
                    "reply": f"I have limited functionality right now because some API configurations are missing ({missing_list}). I can still answer questions about Althaf's portfolio that don't require external information.",
                    "source": None
                }
            )
            
        # Call the agent service to handle the query if available
        if HAS_AGENT_SERVICE:
            result = agent_service.handle_agent_query(query.message)
            return result
        else:
            return JSONResponse(
                status_code=200,
                content={"reply": "AI features are currently disabled. Please contact the administrator.", "source": None}
            )
    except Exception as e:
        logging.error(f"Error in agent query: {e}")
        return JSONResponse(
            status_code=200,  # Return 200 to avoid frontend error handling
            content={"reply": "I'm having trouble accessing external information right now. I can still answer questions about Althaf's portfolio directly.", "source": None}
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
    try:
        # First try to get blogs from MongoDB
        try:
            blogs_cursor = db.blogs.find({"published": True}).sort("created_at", -1)
            blogs = await blogs_cursor.to_list(length=50)
            for blog in blogs:
                blog["id"] = str(blog.pop("_id"))
            
            # If we have blogs from MongoDB, return them
            if blogs:
                return blogs
        except Exception as e:
            logging.warning(f"Could not fetch blogs from MongoDB: {e}")
            blogs = []
            
        # If MongoDB fails or returns no blogs, try to get locally generated blogs
        try:
            from read_local_blogs import get_local_blogs
            local_blogs = get_local_blogs()
            if local_blogs:
                logging.info(f"Serving {len(local_blogs)} locally generated blog posts")
                return local_blogs
        except Exception as e:
            logging.warning(f"Could not fetch locally generated blogs: {e}")
            
        # If we reach here and blogs is empty, we have no blogs to return
        if not blogs:
            logging.warning("No blogs found in MongoDB or local files")
            
        return blogs
    except Exception as e:
        logging.error(f"Error fetching blogs: {e}")
        raise HTTPException(status_code=500, detail="Could not fetch blog posts")

@api_router.get("/blogs/{blog_id}", response_model=BlogPost)
async def get_blog(blog_id: str):
    """Get a specific blog post by ID"""
    try:
        from bson.objectid import ObjectId
        blog = await db.blogs.find_one({"_id": ObjectId(blog_id)})
        if blog:
            blog["id"] = str(blog.pop("_id"))
            return blog
        else:
            raise HTTPException(status_code=404, detail="Blog not found")
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

# Start the server if this file is run directly
if __name__ == "__main__":
    # Configure logging
    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logging.info(f"Starting server with log level: {log_level}")
    
    # Log configuration status
    if HAS_AGENT_SERVICE:
        logging.info("Agent service is available and enabled")
    else:
        logging.warning("Agent service is not available. AI features will be disabled.")
        
    # Start the server
    import uvicorn
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "0.0.0.0")
    logging.info(f"Starting server on {host}:{port}")
    uvicorn.run("server:app", host=host, port=port, reload=True)
