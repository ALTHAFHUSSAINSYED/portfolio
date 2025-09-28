import os
import time
import schedule
import requests
import json
from datetime import datetime
import random
import threading
import logging
from bs4 import BeautifulSoup
from openai import OpenAI
import pymongo
import html  # For HTML entity escaping/unescaping
from dotenv import load_dotenv

# Import Gemini client
from gemini_service import GeminiClient

# Monkey patch for old cgi.escape functionality
def escape(s):
    """
    Replace special characters '&', '<' and '>' in string s with HTML-safe
    sequences. This is a replacement for the deprecated cgi.escape.
    """
    return html.escape(s, quote=False)

# Add to module builtins for feedparser
try:
    import cgi
except ImportError:
    # Create a mock cgi module with the escape function
    import types
    cgi = types.ModuleType('cgi')
    cgi.escape = escape
    import sys
    sys.modules['cgi'] = cgi

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("agent.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('AlluAgent')

# Load environment variables
load_dotenv()

# MongoDB configuration
try:
    MONGO_URI = os.getenv("MONGODB_URI")
    client = pymongo.MongoClient(MONGO_URI)
    db = client.get_database("portfolio")
    blogs_collection = db.blogs
    agent_logs = db.agent_logs
    logger.info("Connected to MongoDB successfully")
except Exception as e:
    logger.error(f"MongoDB connection error: {e}")
    MONGO_URI = None

# AI service configuration
try:
    # Initialize Gemini API client (primary)
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if gemini_api_key:
        gemini_client = GeminiClient(api_key=gemini_api_key)
        if gemini_client.is_available:
            logger.info("Gemini client initialized successfully")
        else:
            logger.warning("Gemini client initialization failed")
            gemini_client = None
    else:
        logger.warning("GEMINI_API_KEY not found in environment variables")
        gemini_client = None
        
    # Initialize OpenAI API client (fallback)
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if openai_api_key:
        openai_client = OpenAI(api_key=openai_api_key)
        logger.info("OpenAI client initialized (fallback)")
    else:
        logger.warning("OPENAI_API_KEY not found in environment variables")
        openai_client = None
except Exception as e:
    logger.error(f"AI client initialization error: {e}")
    gemini_client = None
    openai_client = None

class WebSearchEngine:
    def __init__(self):
        # API Keys for services
        self.serper_api_key = os.getenv("SERPER_API_KEY")  # For Serper.dev (replaces SERP API)
        self.serp_api_key = os.getenv("SERP_API_KEY")      # Legacy support
        self.news_api_key = os.getenv("NEWS_API_KEY")
        
        # Log status of API keys
        if not self.serper_api_key and not self.serp_api_key:
            logger.warning("No search API keys found. Using DuckDuckGo fallback for web search.")
        if not self.news_api_key:
            logger.warning("NEWS_API_KEY not found. Using RSS feeds for news content.")
            
        # RSS feed URLs for technology news
        self.tech_rss_feeds = [
            "https://feeds.feedburner.com/TechCrunch",
            "https://www.wired.com/feed/rss",
            "https://www.theverge.com/rss/index.xml",
            "https://feeds.feedburner.com/venturebeat/SZYF",
            "https://www.cnet.com/rss/all/"
        ]
            
        # User agents for web requests to avoid being blocked
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.9999.99 Safari/537.36",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0"
        ]
    
    def _get_random_headers(self):
        return {
            "User-Agent": random.choice(self.user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://www.google.com/",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
    
    def search_web(self, query, max_results=5):
        """Search the web using multiple available methods with fallbacks"""
        try:
            # Method 1: Try using Serper.dev API (primary method)
            if self.serper_api_key:
                try:
                    logger.info(f"Searching with Serper.dev API: {query}")
                    url = "https://api.serper.dev/search"
                    headers = {
                        'X-API-KEY': self.serper_api_key,
                        'Content-Type': 'application/json'
                    }
                    payload = {
                        'q': query,
                        'num': max_results
                    }
                    response = requests.post(url, headers=headers, json=payload, timeout=10)
                    if response.status_code == 200:
                        results = response.json()
                        return self._extract_serper_results(results, max_results)
                except Exception as e:
            logger.error(f"Error generating blog with AI: {e}")
            return {
                "title": f"Latest Insights on {topic}",
                "content": "Our blog generation system is currently experiencing technical difficulties. Please check back later for new content.",
                "tags": [topic.lower(), "technology", "development"],
                "summary": "Upcoming blog post on technology trends."
            }
    
    def save_blog_to_database(self, blog):
        """Save the generated blog to MongoDB"""
        try:
            if MONGO_URI and blogs_collection:
                result = blogs_collection.insert_one(blog)
                logger.info(f"Blog saved to database with ID: {result.inserted_id}")
                return str(result.inserted_id)
            else:
                logger.error("MongoDB not available")
                return None
        except Exception as e:
            logger.error(f"Error saving blog to database: {e}")
            return None


class AgentScheduler:
    def __init__(self):
        self.blog_generator = BlogGenerator()
        self.running = False
        self.thread = None
        
    def schedule_blog_generation(self, time_str="01:00"):
        """Schedule daily blog generation at specified time"""
        schedule.every().day.at(time_str).do(self.generate_and_publish_blog)
        logger.info(f"Scheduled daily blog generation at {time_str}")
        
    def generate_and_publish_blog(self):
        """Generate and publish a new blog"""
        try:
            logger.info("Starting automated blog generation")
            blog = self.blog_generator.generate_blog()
            
            if blog:
                # Save to database
                blog_id = self.blog_generator.save_blog_to_database(blog)
                
                if blog_id:
                    logger.info(f"Successfully published blog: {blog.get('title')}")
                    
                    # Log the activity
                    if agent_logs:
                        agent_logs.insert_one({
                            "action": "blog_published",
                            "blog_id": blog_id,
                            "blog_title": blog.get("title"),
                            "timestamp": datetime.now()
                        })
                    
                    return True
                else:
                    logger.error("Failed to save blog to database")
            else:
                logger.error("Failed to generate blog")
                
            return False
                
        except Exception as e:
            logger.error(f"Error in generate_and_publish_blog: {e}")
            return False
    
    def start(self):
        """Start the scheduler in a separate thread"""
        if self.running:
            logger.warning("Scheduler is already running")
            return False
            
        self.running = True
        
        def run_scheduler():
            logger.info("Starting agent scheduler")
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        self.thread = threading.Thread(target=run_scheduler)
        self.thread.daemon = True
        self.thread.start()
        logger.info("Agent scheduler started")
        return True
        
    def stop(self):
        """Stop the scheduler"""
        if not self.running:
            logger.warning("Scheduler is not running")
            return False
            
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        logger.info("Agent scheduler stopped")
        return True


# API endpoints for the agent
def handle_agent_query(query):
    """Handle a direct query to the agent from the chatbot"""
    try:
        # Check if we have OpenAI API access
        if not openai_client:
            return {
                "reply": "I'm currently operating with limited capabilities. My AI services are unavailable at the moment. I can still help with basic portfolio information that doesn't require external searches.",
                "source": None
            }
            
        # Initialize web search engine
        search_engine = WebSearchEngine()
        
        # Search for information
        search_results = search_engine.search_web(query)
        
        if not search_results:
            return {
                "reply": "I couldn't find specific information about that. My search capabilities might be limited right now. Could you try asking about Althaf's portfolio directly?",
                "source": None
            }
        
        # Get the first relevant result
        top_result = search_results[0]
        
        # Fetch more detailed content if there's a link
        detailed_content = None
        if top_result.get("link"):
            detailed_content = search_engine.fetch_webpage_content(top_result.get("link"))
        
        # Use OpenAI to generate a response based on the search results
        if openai_client and detailed_content:
            system_prompt = """You are an AI assistant providing helpful information based on web search results.
            Create a concise, informative response that answers the user's query using the information provided.
            Include relevant facts and details, but be brief and to the point.
            If the information is insufficient to answer the query, acknowledge that and suggest alternatives."""
            
            user_prompt = f"""User Query: {query}
            
            Search Result Title: {top_result.get('title', '')}
            Search Result Snippet: {top_result.get('snippet', '')}
            
            Additional Content from {top_result.get('link', '')}:
            {detailed_content.get('content', '')[:1000]}
            
            Provide a helpful response to the user's query based on this information.
            """
            
            try:
                response = openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.5,
                    max_tokens=500
                )
                
                return {
                    "reply": response.choices[0].message.content,
                    "source": top_result.get("link")
                }
            except Exception as e:
                logger.error(f"OpenAI API error: {e}")
                # If OpenAI call fails, fall back to search snippet
                return {
                    "reply": f"Based on what I found: {top_result.get('snippet', 'I found some information but cannot provide complete details at the moment.')}",
                    "source": top_result.get("link")
                }
        else:
            # Fallback to a simple response with the search snippet
            return {
                "reply": f"{top_result.get('snippet', 'I found some information but cannot provide details at the moment.')}",
                "source": top_result.get("link")
            }
            
    except Exception as e:
        logger.error(f"Error handling agent query: {e}")
        return {
            "reply": "Sorry, I encountered an error while processing your request.",
            "source": None
        }


# Initialize and start the agent scheduler
agent_scheduler = AgentScheduler()

# For API use
def initialize_agent():
    agent_scheduler.schedule_blog_generation("01:00")  # Schedule for 1 AM
    return agent_scheduler.start()

def generate_blog_now(topic=None):
    # Check if we have OpenAI API access
    if not openai_client:
        # Create a sample blog post if OpenAI API is not available
        current_date = datetime.now()
        sample_blog = {
            "title": f"Sample Blog Post: {topic or 'Portfolio Technology Overview'}",
            "content": """# Welcome to My Portfolio Blog

## Introduction
This is a sample blog post generated without using OpenAI API. The actual blog generation functionality requires an OpenAI API key to work properly.

## What This Blog Would Cover
If the OpenAI API was configured, this blog would provide detailed information about the requested topic with insights from internet research.

## Features of This Portfolio
- Modern React frontend with Tailwind CSS
- FastAPI backend with MongoDB integration
- AI-powered chatbot for interactive portfolio navigation
- Automatic blog generation using AI and web scraping
- Cloud deployment with CI/CD pipelines

## Next Steps
To enable full AI blog generation:
1. Obtain an OpenAI API key
2. Add it to your environment variables or .env file
3. Restart the backend server

Thank you for visiting my portfolio!
""",
            "topic": topic or "Portfolio Technology",
            "created_at": current_date,
            "tags": ["sample", "portfolio", "technology", "web development"],
            "summary": "A sample blog post created when OpenAI API is not available. This demonstrates the blog display functionality.",
            "published": True,
            "sources": ["https://example.com/sample-source"]
        }
        
        # Save to database if available
        if MONGO_URI and blogs_collection:
            try:
                result = blogs_collection.insert_one(sample_blog)
                logger.info(f"Sample blog saved to database with ID: {result.inserted_id}")
                sample_blog["id"] = str(result.inserted_id)
                return sample_blog
            except Exception as e:
                logger.error(f"Error saving sample blog to database: {e}")
                return sample_blog  # Return the blog even if saving fails
        return sample_blog
    
    # Normal flow if OpenAI is available
    blog_generator = BlogGenerator()
    blog = blog_generator.generate_blog(topic)
    if blog:
        blog_id = blog_generator.save_blog_to_database(blog)
        return blog if blog_id else None
    return None

# Auto-start when imported
if __name__ == "__main__":
    initialize_agent()