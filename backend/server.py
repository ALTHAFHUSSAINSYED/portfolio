from fastapi import FastAPI, APIRouter, UploadFile, File, Form, HTTPException, status
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime
import base64

# --- SETUP ---
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# --- DATABASE CONNECTION ---
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# --- FASTAPI APP INSTANCE ---
app = FastAPI(title="Portfolio API")
api_router = APIRouter(prefix="/api")

# --- PYDANTIC MODELS ---
class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    summary: str
    details: str
    image_url: str  # now contains Base64 string
    technologies: List[str] = []
    key_outcomes: List[str] = []
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Update model (all optional fields for partial update)
class UpdateProjectModel(BaseModel):
    name: Optional[str] = None
    summary: Optional[str] = None
    details: Optional[str] = None
    image_url: Optional[str] = None
    technologies: Optional[List[str]] = None
    key_outcomes: Optional[List[str]] = None

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

    # Read file and encode as Base64
    file_bytes = await file.read()
    encoded_image = f"data:{file.content_type};base64,{base64.b64encode(file_bytes).decode()}"

    project_data = {
        "name": name,
        "summary": summary,
        "details": details,
        "technologies": tech_list,
        "key_outcomes": outcomes_list,
        "image_url": encoded_image
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

# UPDATE an existing project (PUT with image + text support)
@api_router.put("/projects/{project_id}", response_model=Project)
async def update_project(
    project_id: str,
    name: Optional[str] = Form(None),
    summary: Optional[str] = Form(None),
    details: Optional[str] = Form(None),
    technologies: Optional[str] = Form(None),
    key_outcomes: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    update_data = {}

    if name:
        update_data["name"] = name
    if summary:
        update_data["summary"] = summary
    if details:
        update_data["details"] = details
    if technologies:
        update_data["technologies"] = [t.strip() for t in technologies.split(",") if t.strip()]
    if key_outcomes:
        update_data["key_outcomes"] = [o.strip() for o in key_outcomes.split(",") if o.strip()]
    if file:
        file_bytes = await file.read()
        encoded_image = f"data:{file.content_type};base64,{base64.b64encode(file_bytes).decode()}"
        update_data["image_url"] = encoded_image

    result = await db.projects.update_one({"id": project_id}, {"$set": update_data})

    if result.modified_count == 1:
        return await db.projects.find_one({"id": project_id})

    existing = await db.projects.find_one({"id": project_id})
    if existing:
        return existing

    raise HTTPException(status_code=404, detail="Project not found")

# DELETE a project by ID
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
