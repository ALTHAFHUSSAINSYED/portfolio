from fastapi import FastAPI, APIRouter, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime
import shutil

# --- SETUP ---
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Create directories for static files if they don't exist
static_dir = ROOT_DIR / 'static'
images_dir = static_dir / 'images'
images_dir.mkdir(parents=True, exist_ok=True)


# --- DATABASE CONNECTION ---
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]


# --- FASTAPI APP INSTANCE ---
app = FastAPI(title="Portfolio API")

# Mount the static directory to serve uploaded images
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# --- PYDANTIC MODELS ---

# Model for the contact form
class ContactForm(BaseModel):
    name: str = Field(..., alias="Your Name")
    email: EmailStr = Field(..., alias="Email Address")
    subject: Optional[str] = Field(None, alias="Subject")
    message: str = Field(..., alias="Message")

# Model for Project data stored in the database
class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    image_url: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# --- API ENDPOINTS ---

# Contact Form Endpoint
@api_router.post("/contact")
async def send_contact_email(form: ContactForm):
    to_email = os.environ.get('TO_EMAIL')
    sendgrid_api_key = os.environ.get('SENDGRID_API_KEY')

    if not to_email or not sendgrid_api_key:
        raise HTTPException(status_code=500, detail="Server is not configured for sending emails.")

    # Use a default subject if one isn't provided
    final_subject = form.subject if form.subject else f"New message from {form.name}"

    html_content = f"""
    <h3>New Contact Form Submission</h3>
    <p><strong>Name:</strong> {form.name}</p>
    <p><strong>Email:</strong> {form.email}</p>
    <p><strong>Subject:</strong> {final_subject}</p>
    <p><strong>Message:</strong></p>
    <p>{form.message}</p>
    """

    message = Mail(
        from_email=to_email, # Must be your verified SendGrid sender
        to_emails=to_email,
        subject=final_subject,
        html_content=html_content
    )

    try:
        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(message)
        if response.status_code >= 200 and response.status_code < 300:
            return {"message": "Email sent successfully!"}
        else:
             raise HTTPException(status_code=500, detail="Failed to send email.")
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while sending the email.")

# Project Upload Endpoint
@api_router.post("/projects", response_model=Project)
async def create_project(
    name: str = Form(...),
    description: str = Form(...),
    file: UploadFile = File(...)
):
    # Generate a unique filename to prevent overwrites
    file_extension = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = images_dir / unique_filename
    
    # Save the uploaded file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Construct the public URL for the image
    # IMPORTANT: Update this with your actual Render frontend URL in production
    base_url = "https://althaf-portfolio.onrender.com" 
    image_url = f"{base_url}/static/images/{unique_filename}"
    
    project_data = {
        "name": name,
        "description": description,
        "image_url": image_url
    }
    
    project = Project(**project_data)
    await db.projects.insert_one(project.dict())
    return project

# Get All Projects Endpoint
@api_router.get("/projects", response_model=List[Project])
async def get_projects():
    projects_cursor = db.projects.find()
    projects = await projects_cursor.to_list(length=100)
    return projects

# Welcome message for the API root
@api_router.get("/")
async def api_root():
    return {"message": "Welcome to the API!"}


# --- APP CONFIGURATION ---

# Include the router in the main app
app.include_router(api_router)

# Welcome message for the main root
@app.get("/")
def welcome():
    return {"message": "Server is running. API is at /api"}

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Database client shutdown event
@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
