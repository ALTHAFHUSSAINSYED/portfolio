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
    name: str = Field(..., alias="Your Name")
    email: EmailStr = Field(..., alias="Email Address")
    subject: Optional[str] = Field(None, alias="Subject")
    message: str = Field(..., alias="Message")

class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    summary: str
    details: str
    image_url: str
    technologies: List[str] = []
    key_outcomes: List[str] = []
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# --- API ENDPOINTS ---
# (Contact form endpoint remains the same)
@api_router.post("/contact")
async def send_contact_email(form: ContactForm):
    # This endpoint is ready when you configure SendGrid
    pass

@api_router.post("/projects", response_model=Project)
async def create_project(
    name: str = Form(...),
    summary: str = Form(...),
    details: str = Form(...),
    technologies: str = Form(...),
    key_outcomes: str = Form(...),
    file: UploadFile = File(...)
):
    tech_list = [tech.strip() for tech in technologies.split(',') if tech.strip()]
    outcomes_list = [outcome.strip() for outcome in key_outcomes.split(',') if outcome.strip()]
    
    file_extension = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = images_dir / unique_filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    base_url = os.environ.get('BACKEND_URL', 'http://127.0.0.1:8000')
    image_url = f"{base_url}/static/images/{unique_filename}"
    
    project_data = {
        "name": name,
        "summary": summary,
        "details": details,
        "image_url": image_url,
        "technologies": tech_list,
        "key_outcomes": outcomes_list
    }
    
    project = Project(**project_data)
    # This code assumes your data will be in a collection named "projects"
    await db.projects.insert_one(project.model_dump())
    return project

@api_router.get("/projects", response_model=List[Project])
async def get_projects():
    # This code reads from a collection named "projects"
    projects_cursor = db.projects.find()
    projects = await projects_cursor.to_list(length=100)
    return projects

@api_router.get("/projects/{project_id}", response_model=Project)
async def get_project_by_id(project_id: str):
    # This code reads from a collection named "projects"
    project = await db.projects.find_one({"id": project_id})
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@api_router.get("/")
async def api_root():
    return {"message": "Welcome to the API!"}


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

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
