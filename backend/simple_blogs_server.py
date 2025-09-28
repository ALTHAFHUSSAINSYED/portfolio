"""
Simple API server to serve blog posts from local JSON files
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import logging
from typing import List, Optional
from pydantic import BaseModel

# Import the read_local_blogs module
from read_local_blogs import get_local_blogs

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BlogsServer")

# Initialize FastAPI
app = FastAPI(title="Local Blogs API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Define the Blog model
class BlogPost(BaseModel):
    id: str
    title: str
    content: str
    category: str
    tags: List[str] = []
    author: str = "AI Assistant"
    published: bool = True
    created_at: str
    updated_at: Optional[str] = None

@app.get("/")
async def root():
    return {"message": "Welcome to the Local Blogs API", "endpoints": ["/api/blogs"]}

@app.get("/api/blogs", response_model=List[BlogPost])
async def get_blogs():
    """Get all blog posts from local JSON files"""
    try:
        # Get blogs from local JSON files
        blogs = get_local_blogs()
        
        if blogs:
            logger.info(f"Serving {len(blogs)} locally generated blog posts")
            return blogs
        else:
            logger.warning("No blogs found in local files")
            return []
    except Exception as e:
        logger.error(f"Error fetching blogs: {e}")
        raise HTTPException(status_code=500, detail="Could not fetch blog posts")

if __name__ == "__main__":
    # Get port from environment variable or use default (5001)
    port = int(os.environ.get("PORT", 5001))
    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=port)