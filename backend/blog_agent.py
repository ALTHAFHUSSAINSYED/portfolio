import os
import time
import random
import schedule
import json
import logging
from datetime import datetime, timezone
from dotenv import load_dotenv
import threading
from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("blog_agent.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("BlogAgent")

# MongoDB setup
mongo_url = os.getenv("MONGO_URL")
db_name = os.getenv("DB_NAME")
client = MongoClient(mongo_url)
db = client[db_name]

# Auth token for blog posting
auth_token = os.getenv("BLOG_AUTH_TOKEN")


# Blog topics (sequential round-robin selection)
blog_topics = [
    "Latest AI Innovations",
    "Web Development Trends",
    "DevOps Best Practices",
    "Cloud Computing Advancements",
    "Cybersecurity Updates",
    "Mobile App Development",
    "Data Science and Analytics",
    "IoT Technology Trends",
    "Blockchain Applications",
    "Augmented and Virtual Reality"
]

# Track the current topic index in a file for persistence
TOPIC_INDEX_FILE = "current_topic_index.txt"

def get_next_topic():
    try:
        if os.path.exists(TOPIC_INDEX_FILE):
            with open(TOPIC_INDEX_FILE, "r") as f:
                idx = int(f.read().strip())
        else:
            idx = 0
    except Exception:
        idx = 0
    topic = blog_topics[idx % len(blog_topics)]
    return topic

# Function to fetch tech news from various sources
def fetch_tech_news(limit=3):
    sources = [
        {"url": "https://techcrunch.com/", "selector": "article h2 a"},
        {"url": "https://www.theverge.com/", "selector": "h2 a"},
        {"url": "https://news.ycombinator.com/", "selector": ".titleline > a"}
    ]
    
    all_news = []
    
    for source in sources:
        try:
            response = requests.get(source["url"], headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            
            links = soup.select(source["selector"])
            for i, link in enumerate(links):
                if i >= limit:
                    break
                title = link.text.strip()
                url = link.get("href", "")
                
                # Handle relative URLs
                if url.startswith('/'):
                    url = source["url"] + url.lstrip('/')
                
                all_news.append({
                    "title": title,
                    "url": url,
                    "source": source["url"]
                })
            
            time.sleep(1)  # Be nice to the servers
        except Exception as e:
            logger.error(f"Error fetching from {source['url']}: {e}")
    
    return all_news

# Function to generate blog content using Gemini API
def generate_blog_content(topic=None):
    if not topic:
        topic = get_next_topic()
    
    # For testing, use a simple context
    context = f"Topic: {topic}\n\nWrite a technical blog post about this topic."
    
    try:
        # Import Gemini service only when needed
        from backend.ai_service import gemini_service
        blog = gemini_service.generate_blog_post(context)
        if not blog:
            logger.error("Failed to generate blog with Gemini")
            return None
        return blog
    except Exception as e:
        logger.error(f"Error generating blog content: {e}")
        return None

# Function to post a blog with retry mechanism
async def post_blog(blog=None, max_retries=3):
    from backend.notification_service import notification_service
    
    for attempt in range(max_retries):
        try:
            if not blog:
                blog = generate_blog_content()
            
            if not blog:
                error_msg = "Failed to generate blog content"
                logger.error(error_msg)
                print(f"[ERROR] {error_msg}")
                await notification_service.send_blog_notification(False, error_message=error_msg)
                return False
            

            # Save to ChromaDB first
            try:
                import chromadb
                chroma_client = chromadb.CloudClient(
                    api_key=os.getenv('api_key'),
                    tenant=os.getenv('tenant'),
                    database=os.getenv('database')
                )
                collection = chroma_client.get_or_create_collection(name='Blogs_data')
                # Use blog title as ID, or generate a unique one
                blog_id = blog.get('id') or blog.get('title') or str(datetime.utcnow().timestamp())
                print(f"[INFO] Storing blog in ChromaDB: {blog['title']} (ID: {blog_id})")
                # ChromaDB expects metadata values to be str, int, float, bool, SparseVector, or None
                tags = blog.get('tags', [])
                if isinstance(tags, list):
                    tags = ', '.join(str(tag) for tag in tags)
                collection.add(
                    ids=[str(blog_id)],
                    documents=[blog['content']],
                    metadatas=[{
                        'title': blog['title'],
                        'author': blog.get('author', 'Allu Bot'),
                        'created_at': str(datetime.now(timezone.utc)),
                        'category': blog.get('category', 'General'),
                        'summary': blog.get('summary', ''),
                        'tags': tags,
                        'status': 'published'
                    }]
                )
                logger.info(f"Blog stored in ChromaDB: {blog['title']}")
                print(f"[SUCCESS] Blog stored in ChromaDB: {blog['title']}")
            except Exception as chroma_exc:
                logger.error(f"Failed to store blog in ChromaDB: {chroma_exc}")
                print(f"[ERROR] Failed to store blog in ChromaDB: {chroma_exc}")
                # Fallback to MongoDB
                db.blogs.insert_one({
                    "title": blog["title"],
                    "content": blog["content"],
                    "created_at": datetime.now(timezone.utc),
                    "status": "published"
                })
                logger.info(f"Blog stored in MongoDB: {blog['title']}")
                print(f"[SUCCESS] Blog stored in MongoDB: {blog['title']}")

            await notification_service.send_blog_notification(True)
            print(f"[INFO] Notification sent for blog: {blog['title']}")
            return True
            
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed: {e}")
            print(f"[ERROR] Attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                logger.error("All retries failed")
                print("[ERROR] All retries failed")
                return False
            time.sleep(5 * (attempt + 1))  # Exponential backoff
            
    return False
    # For testing: generate and post a blog immediately
    test_blog_post()