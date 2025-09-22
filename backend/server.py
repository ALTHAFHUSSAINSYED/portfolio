from fastapi import FastAPI, APIRouter, UploadFile, File, Form, HTTPException, status
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
static_dir = ROOT_DIR / 'static'
images_dir = static_dir / 'images'
images_dir.mkdir(parents=True, exist_ok=True)

# --- DATABASE CONNECTION ---
mongo_url = os.environ.get('MONGO_URL')
db_name = os.environ.get('DB_NAME')
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

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
    key_outcomes: Optional[List[str]] = None

# --- API ENDPOINTS ---

# Contact Form Endpoint
@api_router.post("/contact")
async def send_contact_email(form: ContactForm):
    to_email = os.environ.get('TO_EMAIL')
    sendgrid_api_key = os.environ.get('SENDGRID_API_KEY')

    if not to_email or not sendgrid_api_key:
        raise HTTPException(status_code=500, detail="Server is not configured for sending emails.")
    
    final_subject = form.subject if form.subject else f"New portfolio message from {form.name}"
    html_content = f"<h3>New Contact: {form.name} ({form.email})</h3><h4>Subject: {final_subject}</h4><p>{form.message}</p>"
    
    message = Mail(from_email=to_email, to_emails=to_email, subject=final_subject, html_content=html_content)
    message.reply_to = form.email
    
    try:
        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(message)
        if 200 <= response.status_code < 300:
            return {"message": "Email sent successfully!"}
        else:
            raise HTTPException(status_code=response.status_code, detail=f"Failed to send email: {response.body}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

# All Project Endpoints (fully implemented)
@api_router.post("/projects", response_model=Project, status_code=status.HTTP_201_CREATED)
async def create_project(name: str = Form(...), summary: str = Form(...), details: str = Form(...), technologies: str = Form(...), key_outcomes: str = Form(...), file: UploadFile = File(...)):
    tech_list = [tech.strip() for tech in technologies.split(',') if tech.strip()]
    outcomes_list = [outcome.strip() for outcome in key_outcomes.split(',') if outcome.strip()]
    
    base_url = os.environ.get('BACKEND_URL', 'http://127.0.0.1:8000')
    image_url = ""
    if file:
        file_bytes = await file.read()
        encoded_image = f"data:{file.content_type};base64,{base64.b64encode(file_bytes).decode()}"
        image_url = encoded_image

    project_data = {"name": name, "summary": summary, "details": details, "image_url": image_url, "technologies": tech_list, "key_outcomes": outcomes_list}
    project = Project(**project_data)
    await db.projects.insert_one(project.model_dump())
    return project

@api_router.get("/projects", response_model=List[Project])
async def get_projects():
    projects_cursor = db.projects.find()
    projects = await projects_cursor.to_list(length=100)
    return projects

@api_router.get("/projects/{project_id}", response_model=Project)
async def get_project_by_id(project_id: str):
    project = await db.projects.find_one({"id": project_id})
    if project:
        return project
    raise HTTPException(status_code=404, detail="Project not found")

@api_router.put("/projects/{project_id}", response_model=Project)
async def update_project(project_id: str, name: str = Form(...), summary: str = Form(...), details: str = Form(...), technologies: str = Form(...), key_outcomes: str = Form(...), file: Optional[UploadFile] = File(None)):
    update_data = {
        "name": name, "summary": summary, "details": details,
        "technologies": [tech.strip() for tech in technologies.split(',') if tech.strip()],
        "key_outcomes": [outcome.strip() for outcome in key_outcomes.split(',') if outcome.strip()]
    }
    if file:
        file_bytes = await file.read()
        encoded_image = f"data:{file.content_type};base64,{base64.b64encode(file_bytes).decode()}"
        update_data["image_url"] = encoded_image

    result = await db.projects.update_one({"id": project_id}, {"$set": update_data})
    if result.modified_count == 1:
        updated_project = await db.projects.find_one({"id": project_id})
        return updated_project
    raise HTTPException(status_code=404, detail="Project not found")

@api_router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: str):
    result = await db.projects.delete_one({"id": project_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    return

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
