from fastapi import FastAPI, APIRouter, UploadFile, File, Form, HTTPException, status
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime
import base64
import shutil

# --- SETUP ---
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# --- DATABASE CONNECTION ---
mongo_url = os.environ.get('MONGO_URL')
db_name = os.environ.get('DB_NAME')
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

# --- FASTAPI APP INSTANCE ---
app = FastAPI(title="Portfolio API")
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
    # ✨ CORRECTED: Changed from List[str] to str to match your data
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

@api_router.post("/contact")
async def send_contact_email(form: ContactForm):
    # This endpoint is ready for when we fix the frontend form
    pass

@api_router.post("/projects", response_model=Project, status_code=status.HTTP_201_CREATED)
async def create_project(name: str = Form(...), summary: str = Form(...), details: str = Form(...), technologies: str = Form(...), key_outcomes: str = Form(...), file: UploadFile = File(...)):
    tech_list = [tech.strip() for tech in technologies.split(',') if tech.strip()]
    
    file_bytes = await file.read()
    encoded_image = f"data:{file.content_type};base64,{base64.b64encode(file_bytes).decode()}"

    project_data = {
        "name": name, "summary": summary, "details": details, "image_url": encoded_image,
        "technologies": tech_list, "key_outcomes": key_outcomes # Stored as a plain string
    }
    project = Project(**project_data)
    await db.projects.insert_one(project.model_dump())
    return project

@api_router.get("/projects", response_model=List[Project])
async def get_projects():
    projects_cursor = db.projects.find()
    projects = await projects_cursor.to_list(length=100)
    return projects

# ... (GET by ID, PUT, and DELETE endpoints remain the same and are correct) ...
@api_router.get("/projects/{project_id}", response_model=Project)
async def get_project_by_id(project_id: str):
    project = await db.projects.find_one({"id": project_id})
    if project: return project
    raise HTTPException(status_code=404, detail="Project not found")

@api_router.put("/projects/{project_id}", response_model=Project)
async def update_project(project_id: str, name: Optional[str] = Form(None), summary: Optional[str] = Form(None), details: Optional[str] = Form(None), technologies: Optional[str] = Form(None), key_outcomes: Optional[str] = Form(None), file: Optional[UploadFile] = File(None)):
    update_data = {}
    if name is not None: update_data["name"] = name
    if summary is not None: update_data["summary"] = summary
    if details is not None: update_data["details"] = details
    if technologies is not None: update_data["technologies"] = [t.strip() for t in technologies.split(',') if t.strip()]
    if key_outcomes is not None: update_data["key_outcomes"] = key_outcomes
    if file:
        file_bytes = await file.read()
        encoded_image = f"data:{file.content_type};base64,{base64.b64encode(file_bytes).decode()}"
        update_data["image_url"] = encoded_image
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No update data provided")

    result = await db.projects.update_one({"id": project_id}, {"$set": update_data})
    if result.modified_count == 1:
        updated_project = await db.projects.find_one({"id": project_id})
        return updated_project
    
    existing_project = await db.projects.find_one({"id": project_id})
    if existing_project: return existing_project
    
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
