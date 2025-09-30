import os
import time
import random
import schedule
import json
import logging
from datetime import datetime
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
    # Update index for next run
    with open(TOPIC_INDEX_FILE, "w") as f:
        f.write(str((idx + 1) % len(blog_topics)))
    return topic

# Function to fetch trending topics
def fetch_trending_topics():
    try:
        response = requests.get("https://dev.to/t/trending")
        soup = BeautifulSoup(response.text, "html.parser")
        topics = [a.text.strip() for a in soup.find_all("h2")[:5] if a.text.strip()]
        return topics
    except Exception as e:
        logger.error(f"Error fetching trending topics: {e}")
        return []

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
        from ai_service import gemini_service
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
    from notification_service import notification_service
    
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
                    api_key=os.getenv('CHROMA_API_KEY'),
                    tenant=os.getenv('CHROMA_TENANT_ID'),
                    database=os.getenv('CHROMA_DATABASE')
                )
                collection = chroma_client.get_or_create_collection(name='Blogs_data')
                # Use blog title as ID, or generate a unique one
                blog_id = blog.get('id') or blog.get('title') or str(datetime.utcnow().timestamp())
                print(f"[INFO] Storing blog in ChromaDB: {blog['title']} (ID: {blog_id})")
                collection.add(
                    ids=[str(blog_id)],
                    documents=[blog['content']],
                    metadatas=[{
                        'title': blog['title'],
                        'author': blog.get('author', 'Allu Bot'),
                        'created_at': str(datetime.utcnow()),
                        'category': blog.get('category', 'General'),
                        'summary': blog.get('summary', ''),
                        'tags': blog.get('tags', []),
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
                    "created_at": datetime.utcnow(),
                    "status": "published"
                })
                logger.info(f"Blog stored in MongoDB: {blog['title']}")
                print(f"[SUCCESS] Blog stored in MongoDB: {blog['title']}")

            await notification_service.send_blog_notification(True, blog_title=blog['title'])
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
    
    try:
        response = requests.post(
            api_url,
            headers=headers,
            json={
                "title": blog["title"],
                "content": blog["content"],
                "author": "Allu Bot"
            }
        )
        
        response.raise_for_status()
        
        # Save to MongoDB for tracking
        db.blogs.insert_one({
            "title": blog["title"],
            "content": blog["content"],
            "created_at": datetime.utcnow(),
            "status": "published"
        })
        
        logger.info(f"Blog posted successfully: {blog['title']}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to post blog: {e}")
        return False

# Function to run the blog agent as a scheduled task
def run_blog_agent():
    # Schedule a daily post at 11:00 AM UTC
    from datetime import timezone
    hour = 11
    minute = 0
    logger.info("Scheduling daily blog post at 11:00 UTC")
    while True:
        now = datetime.now(timezone.utc)
        if now.hour == hour and now.minute == minute:
            logger.info("Executing scheduled blog post at 11:00 UTC")
            post_blog()
            time.sleep(60)  # Sleep for a minute to avoid duplicate posts
        time.sleep(30)  # Check every 30 seconds

# Function to start the blog agent in a background thread
def start_blog_agent():
    thread = threading.Thread(target=run_blog_agent)
    thread.daemon = True
    thread.start()
    logger.info("Blog agent started in background")

# Test function to generate a blog immediately
def test_blog_post():
    blog = generate_blog_content()
    if blog:
        logger.info(f"Generated blog: {blog['title']}")
        return post_blog(blog)
    return False

if __name__ == "__main__":
    # For testing: generate and post a blog immediately
    test_blog_post()