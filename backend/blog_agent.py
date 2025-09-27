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
import openai
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

# OpenAI API setup
openai.api_key = os.getenv("OPENAI_API_KEY")

# Auth token for blog posting
auth_token = os.getenv("BLOG_AUTH_TOKEN")

# Blog topics
# List of blog topics
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

# Function to generate blog content using OpenAI API
def generate_blog_content(topic=None):
    if not topic:
        topic = random.choice(blog_topics)
    
    # Get trending topics and tech news for context
    trending_topics = fetch_trending_topics()
    tech_news = fetch_tech_news()
    
    # Build context for the AI
    context = f"Topic: {topic}\n\nTrending tech topics: {', '.join(trending_topics)}\n\nRecent tech news:\n"
    for i, news in enumerate(tech_news):
        context += f"{i+1}. {news['title']} ({news['source']})\n"
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system", 
                    "content": "You are an expert tech blogger who writes engaging, informative articles. " +
                               "Generate a complete blog post with HTML formatting using the provided information. " +
                               "Include a catchy title, introduction, main sections with headers, and a conclusion. " +
                               "The blog post should be informative, engaging, and 600-800 words in length."
                },
                {"role": "user", "content": context}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        
        blog_content = response["choices"][0]["message"]["content"]
        
        # Extract title from the generated content
        lines = blog_content.split('\n')
        title = ""
        for line in lines[:5]:  # Check first few lines for title
            if line.strip().startswith('#') or line.strip().startswith('<h1>'):
                title = line.strip().replace('#', '').strip()
                title = title.replace('<h1>', '').replace('</h1>', '').strip()
                break
        
        if not title:
            title = topic  # Fallback to topic if no title found
        
        return {"title": title, "content": blog_content}
        
    except Exception as e:
        logger.error(f"Error generating blog content: {e}")
        return None

# Function to post a blog
def post_blog(blog=None):
    if not blog:
        blog = generate_blog_content()
    
    if not blog:
        logger.error("Failed to generate blog content")
        return False
    
    # API endpoint for posting blog
    api_url = os.getenv("BLOG_API_URL", "http://localhost:5000/api/post-blog")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth_token}"
    }
    
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
    # Schedule a daily post at a random time between 9 AM and 5 PM
    hour = random.randint(9, 17)
    minute = random.randint(0, 59)
    
    logger.info(f"Scheduling daily blog post at {hour:02d}:{minute:02d}")
    
    while True:
        now = datetime.now()
        if now.hour == hour and now.minute == minute:
            logger.info("Executing scheduled blog post")
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