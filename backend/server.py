# backend/backend.py (Updated)
from fastapi import FastAPI, APIRouter, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os, logging, uuid, shutil
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime

# (Setup and other parts of the file remain the same)
# ...

# ✨ MODIFIED: Updated Project model with new lists
class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    summary: str
    details: str
    image_url: str
    technologies: List[str] = [] # New list for technologies
    key_outcomes: List[str] = [] # New list for outcomes
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# ...

# ✨ MODIFIED: Updated Project Upload Endpoint to handle new fields
@api_router.post("/projects", response_model=Project)
async def create_project(
    name: str = Form(...),
    summary: str = Form(...),
    details: str = Form(...),
    file: UploadFile = File(...),
    technologies: str = Form(...), # Receive as a comma-separated string
    key_outcomes: str = Form(...)  # Receive as a comma-separated string
):
    # Process the comma-separated strings into lists
    tech_list = [tech.strip() for tech in technologies.split(',') if tech.strip()]
    outcomes_list = [outcome.strip() for outcome in key_outcomes.split(',') if outcome.strip()]
    
    # (File saving logic remains the same)
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
    # The collection name should be 'projects', not 'myFirstCollection'
    await db.projects.insert_one(project.model_dump()) 
    return project

# (Rest of the file remains the same)
# ...
