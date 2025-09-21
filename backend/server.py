# backend/backend.py (Updated)
from fastapi import FastAPI, APIRouter, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
# (Other imports remain the same)
import os, logging, uuid, shutil
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime

# (Setup code remains the same)
# --- SETUP ---
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')
static_dir = ROOT_DIR / 'static'
images_dir = static_dir / 'images'
images_dir.mkdir(parents=True, exist_ok=True)

# (Database connection remains the same)
# --- DATABASE CONNECTION ---
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# (FastAPI App instance remains the same)
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

# ✨ MODIFIED: Updated Project model
class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    summary: str  # Short summary for the main page card
    details: str  # Long, detailed description for the details page
    image_url: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# --- API ENDPOINTS ---
# (Contact Form Endpoint remains the same)

# ✨ MODIFIED: Updated Project Upload Endpoint
@api_router.post("/projects", response_model=Project)
async def create_project(
    name: str = Form(...),
    summary: str = Form(...), # Changed from description
    details: str = Form(...), # Added details field
    file: UploadFile = File(...)
):
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
        "image_url": image_url
    }
    
    project = Project(**project_data)
    await db.projects.insert_one(project.model_dump())
    return project

# (Get All Projects endpoint remains the same)
@api_router.get("/projects", response_model=List[Project])
async def get_projects():
    projects_cursor = db.projects.find()
    projects = await projects_cursor.to_list(length=100)
    return projects

# (Get Single Project endpoint is now correct)
@api_router.get("/projects/{project_id}", response_model=Project)
async def get_project_by_id(project_id: str):
    project = await db.projects.find_one({"id": project_id})
    if project is None:
        # This is where your backend sends the "Not Found" if the ID is wrong
        # The plain "Not Found" page is a Render issue we will fix next
        raise HTTPException(status_code=404, detail="Project not found")
    return project

# (Rest of the file remains the same)
# ... app configuration ...
app.include_router(api_router)
# ... etc. ...
