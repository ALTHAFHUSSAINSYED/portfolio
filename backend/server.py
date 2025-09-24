# backend.py

from fastapi import FastAPI, APIRouter, UploadFile, File, Form, HTTPException, status
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, From, To, Subject, Content, ReplyTo
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime
import base64
import shutil
# ✨ --- NEW: IMPORT CLOUDINARY --- ✨
import cloudinary
import cloudinary.uploader
import cloudinary.api

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

# --- FASTAPI APP INSTANCE ---
app = FastAPI(title="Portfolio API")
api_router = APIRouter(prefix="/api")

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

    final_subject = form.subject if form.subject else f"New portfolio message from {form.name}"
    html_content = f"""
    <h3>New Contact Form Submission</h3>
    <p><strong>Name:</strong> {form.name}</p>
    <p><strong>Email:</strong> {form.email}</p>
    <p><strong>Subject:</strong> {form.subject or 'No Subject Provided'}</p>
    <p><strong>Message:</strong></p>
    <p>{form.message}</p>
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
    tech_list = [tech.strip() for tech in technologies.split(',') if tech.strip()]
    
    # NEW: Upload file to Cloudinary instead of using Base64
    try:
        upload_result = cloudinary.uploader.upload(file.file, folder="portfolio_projects")
        image_url = upload_result.get("secure_url") # Get the HTTPS URL
    except Exception as e:
        logging.error(f"Cloudinary upload failed: {e}")
        raise HTTPException(status_code=500, detail="Image could not be uploaded.")

    # REMOVED: The old Base64 logic is gone
    # file_bytes = await file.read()
    # encoded_image = f"data:{file.content_type};base64,{base64.b64encode(file_bytes).decode()}"

    project_data = {
        "name": name, "summary": summary, "details": details, 
        "image_url": image_url, # Use the new Cloudinary URL
        "technologies": tech_list, "key_outcomes": key_outcomes
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

# --- APP CONFIGURATION ---
# (No changes here)
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
