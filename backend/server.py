from fastapi import FastAPI, APIRouter, UploadFile, File, Form, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
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
    name: str
    summary: str
    details: str
    image_url: str
    technologies: List[str] = []
    key_outcomes: List[str] = []

# --- API ENDPOINTS (CRUD) ---

# CREATE a new project (POST)
@api_router.post("/projects", response_model=Project, status_code=status.HTTP_201_CREATED)
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
        "name": name, "summary": summary, "details": details, "image_url": image_url,
        "technologies": tech_list, "key_outcomes": outcomes_list
    }
    project = Project(**project_data)
    await db.projects.insert_one(project.model_dump())
    return project

# READ all projects (GET)
@api_router.get("/projects", response_model=List[Project])
async def get_projects():
    projects_cursor = db.projects.find()
    projects = await projects_cursor.to_list(length=100)
    return projects

# READ a single project by ID (GET)
@api_router.get("/projects/{project_id}", response_model=Project)
async def get_project_by_id(project_id: str):
    project = await db.projects.find_one({"id": project_id})
    if project:
        return project
    raise HTTPException(status_code=404, detail="Project not found")

# UPDATE an existing project (PUT)
@api_router.put("/projects/{project_id}", response_model=Project)
async def update_project(project_id: str, updated_project_data: UpdateProjectModel):
    update_data = updated_project_data.model_dump(exclude_unset=True)
    
    result = await db.projects.update_one(
        {"id": project_id},
        {"$set": update_data}
    )
    
    if result.modified_count == 1:
        updated_project = await db.projects.find_one({"id": project_id})
        return updated_project
        
    existing_project = await db.projects.find_one({"id": project_id})
    if existing_project:
        return existing_project # Return existing if no changes were made

    raise HTTPException(status_code=404, detail="Project not found")

# ? NEW: DELETE a project by ID
@api_router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: str):
    result = await db.projects.delete_one({"id": project_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    # A 204 response should not have a body, so we return nothing.
    return

# --- APP CONFIGURATION ---
app.include_router(api_router)

@app.get("/")
def welcome():
    return {"message": "Server is running. API is at /api"}

# (CORS Middleware and other app settings remain the same)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)
