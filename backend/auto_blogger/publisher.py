"""
Blog Publisher Module
Handles saving blogs to JSON and embedding into ChromaDB (No MongoDB).
"""

import os
import json
import logging
import time
import uuid
import google.generativeai as genai
import chromadb
from typing import Dict, Any
from datetime import datetime
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BlogPublisher")

class BlogPublisher:
    def __init__(self):
        load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '.env'))
        
        # Setup Gemini for Embeddings
        self.gemini_key = os.getenv("GEMINI_BLOG_API_KEY") or os.getenv("GEMINI_API_KEY")
        if self.gemini_key:
            genai.configure(api_key=self.gemini_key)
        
        # Setup ChromaDB
        self.chroma_client = self._setup_chroma()
        
        # Storage Path
        self.storage_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            "generated_blogs"
        )
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)

    def _setup_chroma(self):
        """Initialize ChromaDB client"""
        try:
            # Using ChromaDB Cloud or Persistent Client based on env
            # Assuming Cloud for EC2 based on user context, or local persistent
            # Reusing environment variables used in server.py likely
            chroma_api_key = os.getenv("CHROMA_API_KEY")
            chroma_host = "api.trychroma.com" # Or from env
            chroma_tenant = os.getenv("CHROMA_TENANT_ID")
            chroma_db = os.getenv("CHROMA_DATABASE")
            
            if chroma_api_key:
                logger.info("Connecting to ChromaDB Cloud...")
                return chromadb.HttpClient(
                    host=chroma_host,
                    ssl=True,
                    headers={
                        "x-chroma-token": chroma_api_key,
                        "x-tenant": chroma_tenant,
                        "x-database": chroma_db
                    }
                )
            else:
                 # Local fallback if cloud not configured
                logger.info("Using local ChromaDB (fallback)...")
                return chromadb.PersistentClient(path="./chroma_db")
        except Exception as e:
            logger.error(f"ChromaDB setup failed: {e}")
            return None

    def _get_embedding(self, text: str) -> list:
        """Generate embedding using Gemini"""
        try:
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return []

    def publish(self, blog: Dict[str, Any]) -> str:
        """Save blog and embed"""
        logger.info(f"Publishing blog: {blog.get('title')}")
        
        # 1. Finalize Metadata
        blog_id = f"{blog['category'].replace(' ', '_')}_{int(time.time())}"
        blog['id'] = blog_id
        blog['published'] = True
        blog['created_at'] = datetime.now().isoformat()
        
        # 2. Save JSON File
        filename = f"{blog_id}.json"
        filepath = os.path.join(self.storage_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(blog, f, indent=2)
            logger.info(f"Saved JSON to {filepath}")
        except Exception as e:
            raise Exception(f"Failed to save JSON: {e}")

        # 3. Save to ChromaDB
        if self.chroma_client:
            try:
                collection = self.chroma_client.get_or_create_collection("Blogs_data")
                
                # Check if embedding exists (rare collision)
                existing = collection.get(ids=[blog_id])
                if existing and existing['ids']:
                     logger.warning(f"Blog {blog_id} already in ChromaDB. Updating...")
                
                embedding = self._get_embedding(blog['content'])
                if embedding:
                    collection.upsert(
                        ids=[blog_id],
                        documents=[blog['content']],
                        metadatas=[{
                            "title": blog['title'],
                            "category": blog['category'],
                            "url": f"https://althafportfolio.site/blogs/{blog_id}", # Live URL construction
                            "timestamp": str(int(time.time()))
                        }],
                        embeddings=[embedding]
                    )
                    logger.info("Successfully embedded into ChromaDB")
                else:
                    logger.error("Skipped ChromaDB: Embedding failed")
            except Exception as e:
                 logger.error(f"ChromaDB insert failed: {e}")
                 # We don't raise here to avoid failing the whole publish if local save worked
        
        return f"https://althafportfolio.site/blogs/{blog_id}"

if __name__ == "__main__":
    # Test
    pub = BlogPublisher()
    mock_blog = {
        "title": "Test Publish",
        "category": "DevOps",
        "content": "This is a test content for embedding.",
        "tags": ["test"]
    }
    url = pub.publish(mock_blog)
    print(f"Published URL: {url}")
