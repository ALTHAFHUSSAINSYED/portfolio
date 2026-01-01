"""
Blog Publisher Module
Handles saving blogs to JSON and embedding into ChromaDB (No MongoDB).
"""

import os
import json
import logging
import time
import uuid
import boto3
from google import genai
from google.genai import types
import chromadb
from typing import Dict, Any, List, Optional
from datetime import datetime
from dotenv import load_dotenv
from botocore.exceptions import ClientError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BlogPublisher")

# ═══════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════

def create_clean_excerpt(content: str, max_length: int = 350) -> str:
    """Create clean excerpt by stripping markdown and extracting readable text
    
    Args:
        content: Blog content with markdown
        max_length: Maximum character length (default 350 for ~3 lines)
    """
    import re
    
    # Remove markdown headers
    clean = re.sub(r'^#+\s+', '', content, flags=re.MULTILINE)
    
    # Remove markdown links [text](url) -> text
    clean = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', clean)
    
    # Remove code blocks
    clean = re.sub(r'```.*?```', '', clean, flags=re.DOTALL)
    
    # Remove inline code
    clean = re.sub(r'`([^`]+)`', r'\1', clean)
    
    # Remove bold/italic markers
    clean = re.sub(r'\*\*([^\*]+)\*\*', r'\1', clean)
    clean = re.sub(r'\*([^\*]+)\*', r'\1', clean)
    
    # Get first 2-3 paragraphs (not just first one)
    paragraphs = [p.strip() for p in clean.split('\n\n') if p.strip()]
    
    # Combine first 2 paragraphs for richer excerpt
    if len(paragraphs) >= 2:
        excerpt = paragraphs[0] + ' ' + paragraphs[1]
    elif paragraphs:
        excerpt = paragraphs[0]
    else:
        excerpt = clean
    
    # Truncate at word boundary
    if len(excerpt) > max_length:
        excerpt = excerpt[:max_length].rsplit(' ', 1)[0] + '...'
    
    return excerpt


# ═══════════════════════════════════════════════════════════
# S3 BLOG STORAGE HELPER
# ═══════════════════════════════════════════════════════════

class S3BlogStorage:
    """Handles persistent blog storage in S3 (Phase A: Fix data loss)"""
    
    def __init__(self, bucket_name: str = "althaf-blogs-storage"):
        self.bucket = bucket_name
        self.s3 = boto3.client("s3")  # Auto-uses IAM role credentials
        self.index_key = "blogs/index.json"
        self.posts_prefix = "blogs/posts/"
        logger.info(f"S3BlogStorage initialized: s3://{bucket_name}")
    
    def read_index(self) -> Dict:
        """Read blogs/index.json from S3"""
        try:
            response = self.s3.get_object(Bucket=self.bucket, Key=self.index_key)
            return json.loads(response['Body'].read().decode('utf-8'))
        except self.s3.exceptions.NoSuchKey:
            logger.warning("index.json not found, returning empty")
            return {"blogs": []}
        except Exception as e:
            logger.error(f"Error reading S3 index: {e}")
            return {"blogs": []}

    def read_blog(self, blog_id: str) -> Optional[Dict]:
        """Read individual blog post from blogs/posts/{id}.json"""
        key = f"{self.posts_prefix}{blog_id}.json"
        try:
            response = self.s3.get_object(Bucket=self.bucket, Key=key)
            return json.loads(response['Body'].read().decode('utf-8'))
        except self.s3.exceptions.NoSuchKey:
            logger.info(f"Blog post {key} not found in S3.")
            return None
        except Exception as e:
            logger.error(f"Error reading S3 blog post {key}: {e}")
            return None
    
    def write_index(self, data: Dict[str, List]):
        """Write blogs/index.json to S3"""
        content = json.dumps(data, indent=2)
        self.s3.put_object(
            Bucket=self.bucket,
            Key=self.index_key,
            Body=content.encode('utf-8'),
            ContentType='application/json'
        )
        logger.info(f"✅ Updated S3: {self.index_key}")
    
    def upload_post(self, blog_id: str, blog_data: Dict):
        """Upload individual blog to blogs/posts/{id}.json"""
        key = f"{self.posts_prefix}{blog_id}.json"
        content = json.dumps(blog_data, indent=2)
        self.s3.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=content.encode('utf-8'),
            ContentType='application/json'
        )
        logger.info(f"✅ Uploaded full post: {key}")
    
    def add_blog_to_index(self, blog: Dict):
        """Insert new blog at top of index.json (newest first)"""
        index_data = self.read_index()
        
        # Prepare metadata entry (lightweight)
        metadata = {
            "id": blog['id'],
            "title": blog['title'],
            "category": blog['category'],
            "slug": blog.get('slug', blog['id']),
            "created_at": blog['created_at'],
            "excerpt": create_clean_excerpt(blog['content']),  # ✅ Clean excerpt without markdown
            "tags": blog.get('tags', []),
            "author": blog.get('author', 'Althaf Hussain Syed'),
            "author_title": blog.get('author_title', 'Solutions Architect')
        }
        
        # Insert at position 0 (top of list)
        index_data['blogs'].insert(0, metadata)
        
        self.write_index(index_data)
        logger.info(f"✅ Added {blog['id']} to index (total: {len(index_data['blogs'])})")

# ═══════════════════════════════════════════════════════════

class BlogPublisher:
    def __init__(self):
        load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '.env'))
        
        # Setup Gemini for Embeddings
        self.gemini_key = os.getenv("GEMINI_BLOG_API_KEY") or os.getenv("GEMINI_API_KEY")
        self.gemini_client = None
        if self.gemini_key:
             try:
                self.gemini_client = genai.Client(api_key=self.gemini_key)
             except Exception as e:
                logger.warning(f"Gemini Client init failed: {e}")
        
        # Setup ChromaDB
        self.chroma_client = self._setup_chroma()
        
        # Setup S3 Storage (Phase A: Persistent storage)
        s3_bucket = os.getenv("S3_BLOG_BUCKET", "althaf-blogs-storage")
        self.s3_storage = S3BlogStorage(bucket_name=s3_bucket)
        
        # Local Storage Path (kept for backwards compatibility)
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
            chroma_api_key = os.getenv("CHROMA_API_KEY")
            chroma_tenant = os.getenv("CHROMA_TENANT") or os.getenv("CHROMA_TENANT_ID")
            chroma_db = os.getenv("CHROMA_DATABASE") or os.getenv("CHROMA_DB_NAME")
            
            if chroma_api_key and chroma_tenant and chroma_db:
                logger.info("Connecting to ChromaDB Cloud...")
                return chromadb.CloudClient(
                    api_key=chroma_api_key,
                    tenant=chroma_tenant,
                    database=chroma_db
                )
            else:
                 # Local fallback if cloud not configured
                logger.info("Using local ChromaDB (fallback/dev)...")
                return chromadb.PersistentClient(path="./chroma_db")
        except Exception as e:
            logger.error(f"ChromaDB setup failed: {e}")
            return None

    def _get_embedding(self, text: str) -> list:
        """Generate embedding using Gemini"""
        try:
            if not self.gemini_client:
                return []
                
            result = self.gemini_client.models.embed_content(
                model="text-embedding-004",
                contents=text,
                config=types.EmbedContentConfig(
                    task_type="RETRIEVAL_DOCUMENT"
                )
            )
            return result.embeddings[0].values
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return []

    def publish(self, blog: Dict[str, Any]) -> str:
        """Save blog and embed"""
        logger.info(f"Publishing blog: {blog.get('title')}")
        
        # VALIDATION: Check for failed sections
        content = blog.get('content', '')
        
        # Strict validation checks
        failed_indicators = [
            '<<SECTION_GENERATION_FAILED>>', # New strict token
            '[Content Generation Failed',    # Legacy token
            '[Section Generation Failed]'    # Potential legacy token
        ]
        
        has_failure = any(indicator in content for indicator in failed_indicators)
        
        if has_failure or not content or len(content) < 1000:
            error_msg = "Blog validation FAILED: Contains failed sections or insufficient content"
            logger.error(f"❌ {error_msg}")
            
            # Find which indicator triggered it
            for indicator in failed_indicators:
                if indicator in content:
                     logger.error(f"   Reason: Found failure token '{indicator}'")
                     
            logger.error(f"Content preview: {content[:200]}...")
            raise ValueError(error_msg)
        
        # Additional validation: Check for raw markdown artifacts
        if content.count('##') > 20:  # Suspiciously high header count
            logger.warning("⚠️ High markdown header count detected - possible rendering issue")
        
        logger.info("✅ Blog content validation passed")
        
        # 1. Finalize Metadata
        blog_id = f"{blog['category'].replace(' ', '_')}_{int(time.time())}"
        blog['id'] = blog_id
        blog['published'] = True
        blog['created_at'] = datetime.now().isoformat()
        
        # 2. Save to S3 (Phase A: Persistent Storage)
        try:
            # Upload full post to S3 posts/
            self.s3_storage.upload_post(blog_id, blog)
            
            # Add metadata to index.json
            self.s3_storage.add_blog_to_index(blog)
            
            logger.info(f"✅ Saved to S3: {blog_id}")
        except Exception as e:
            logger.error(f"S3 save failed: {e}")
            raise Exception(f"Failed to save to S3: {e}")
        
        # 2b. Also save locally (optional backup, ephemeral)
        filename = f"{blog_id}.json"
        filepath = os.path.join(self.storage_dir, filename)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(blog, f, indent=2)
            logger.info(f"Saved local backup: {filepath}")
        except Exception as e:
            logger.warning(f"Local save failed (non-critical): {e}")

        # 3. Save to ChromaDB (with retry logic)
        if self.chroma_client:
            max_retries = 3
            retry_delay = 5
            
            for attempt in range(max_retries):
                try:
                    collection = self.chroma_client.get_or_create_collection("Blogs_data")
                    
                    # Check if embedding exists (rare collision)
                    existing = collection.get(ids=[blog_id])
                    if existing and existing['ids']:
                         logger.warning(f"Blog {blog_id} already in ChromaDB. Updating...")
                    
                    embedding = self._get_embedding(blog['content'])
                    if not embedding:
                        raise ValueError("Embedding generation failed - null embedding returned")
                    
                    collection.upsert(
                        ids=[blog_id],
                        documents=[blog['content']],
                        metadatas=[{
                            "title": blog['title'],
                            "category": blog['category'],
                            "url": f"https://althafportfolio.site/blogs/{blog_id}",
                            "timestamp": str(int(time.time()))
                        }],
                        embeddings=[embedding]
                    )
                    logger.info("✅ Successfully embedded into ChromaDB")
                    break  # Success - exit retry loop
                    
                except Exception as e:
                    logger.warning(f"ChromaDB sync attempt {attempt + 1}/{max_retries} failed: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                    else:
                        logger.error(f"❌ ChromaDB sync FAILED after {max_retries} attempts for blog {blog_id}")
                        # Continue anyway - S3 is the source of truth
        
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
