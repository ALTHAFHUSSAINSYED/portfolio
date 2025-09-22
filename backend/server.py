from fastapi import FastAPI, APIRouter, UploadFile, File, Form, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
# Import SendGrid libraries
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
static_dir = ROOT_DIR / 'static'
images_dir = static_dir / 'images'
images_dir.mkdir(parents=True, exist_ok=True)

# --- DATABASE CONNECTION ---
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# --- FASTAPI APP INSTANCE ---
app = FastAPI(title="Portfolio API")
app.mount("/static", StaticFiles(directory=static_dir), name="static")
api_router = APIRouter(prefix="/api")

# --- PYDANTIC MODELS ---
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
    key_outcomes: List[str] = []
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class UpdateProjectModel(BaseModel):
    name: Optional[str] = None
    summary: Optional[str] = None
    details: Optional[str] = None
    image_url: Optional[str] = None
    technologies: Optional[List[str]] = None
    key_outcomes: Optional[str] = None

# --- API ENDPOINTS ---

# Contact Form Endpoint (Now with full logic)
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
    <p><strong>Subject:</strong> {form.subject}</p>
    <p><strong>Message:</strong></p>
    <p>{form.message}</p>
    """
    message = Mail(
        from_email=to_email,
        to_emails=to_email,
        subject=final_subject,
        html_content=html_content)
    message.reply_to = form.email

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

# All Project Endpoints remain unchanged and will work as before
@api_router.post("/projects", response_model=Project, status_code=status.HTTP_201_CREATED)
async def create_project(name: str = Form(...), summary: str = Form(...), details: str = Form(...), technologies: str = Form(...), key_outcomes: str = Form(...), file: UploadFile = File(...)):
    # ... your working code ...
    pass

@api_router.get("/projects", response_model=List[Project])
async def get_projects():
    # ... your working code ...
    pass

@api_router.get("/projects/{project_id}", response_model=Project)
async def get_project_by_id(project_id: str):
    # ... your working code ...
    pass

@api_router.put("/projects/{project_id}", response_model=Project)
async def update_project(project_id: str, updated_project_data: UpdateProjectModel):
    # ... your working code ...
    pass

@api_router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: str):
    # ... your working code ...
    pass

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
