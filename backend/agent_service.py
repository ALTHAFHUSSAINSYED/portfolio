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
import pymongo
import html  # For HTML entity escaping/unescaping
from dotenv import load_dotenv

# Import Gemini service
from ai_service import gemini_service

# Import search utilities for API optimization
from search_utils import search_cache, rate_limiter, query_optimizer

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

# Create cache directory for search results
cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")
if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)

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
    # Use our unified AI service with Gemini and LangChain
    gemini_api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if gemini_api_key:
        # The gemini_service singleton is already initialized in ai_service.py
        # We can use it directly
        logger.info("Using Gemini AI service")
        gemini_client = gemini_service  # Use our singleton service
    else:
        logger.warning("GEMINI_API_KEY not found in environment variables")
        gemini_client = None
except Exception as e:
    logger.error(f"AI client initialization error: {e}")
    gemini_client = None

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
            # Optimize the query for better results
            original_query = query
            optimized_query = query_optimizer.optimize_query(query)
            
            # Check if we have cached results first
            cached_results = search_cache.get(optimized_query, {'num': max_results})
            if cached_results:
                logger.info(f"Using cached search results for: {optimized_query}")
                return cached_results
                
            # Method 1: Try using Serper.dev API (primary method) if we have available rate limit
            if self.serper_api_key and rate_limiter.check_limit():
                try:
                    logger.info(f"Searching with Serper.dev API: {optimized_query}")
                    url = "https://google.serper.dev/search"
                    headers = {
                        'X-API-KEY': self.serper_api_key,
                        'Content-Type': 'application/json'
                    }
                    payload = {
                        'q': optimized_query,
                        'num': max_results
                    }
                    
                    # Record this request for rate limiting
                    rate_limiter.add_request()
                    
                    response = requests.post(url, headers=headers, json=payload, timeout=10)
                    if response.status_code == 200:
                        results = response.json()
                        extracted_results = self._extract_serper_results(results, max_results)
                        
                        # Cache the results for future use
                        search_cache.set(optimized_query, extracted_results, {'num': max_results})
                        
                        return extracted_results
                except Exception as e:
                    logger.error(f"Error searching with Serper.dev API: {e}")
                    # Fall through to next method
            
            # Method 2: Try using legacy SERP API
            if self.serp_api_key:
                try:
                    logger.info(f"Searching with SERP API: {query}")
                    # Implementation for SERP API
                    # ...
                    pass
                except Exception as e:
                    logger.error(f"Error searching with SERP API: {e}")
                    # Fall through to next method
            
            # Method 3: Fallback to direct web search
            logger.info(f"Falling back to basic web search for: {query}")
            return self._fallback_search(query, max_results)
            
        except Exception as e:
            logger.error(f"Error in search_web: {e}")
            return []
            
    def _extract_serper_results(self, results, max_results=5):
        """Extract useful information from Serper.dev API results"""
        try:
            extracted = []
            
            # Process organic search results
            if 'organic' in results:
                for item in results['organic'][:max_results]:
                    extracted.append({
                        'title': item.get('title', ''),
                        'link': item.get('link', ''),
                        'snippet': item.get('snippet', ''),
                        'position': item.get('position', ''),
                        'source': 'serper.dev'
                    })
            
            # If we don't have enough organic results, add "People Also Ask" entries
            if len(extracted) < max_results and 'peopleAlsoAsk' in results:
                remaining = max_results - len(extracted)
                for item in results['peopleAlsoAsk'][:remaining]:
                    extracted.append({
                        'title': item.get('question', ''),
                        'link': item.get('link', ''),
                        'snippet': item.get('answer', ''),
                        'source': 'serper.dev (People Also Ask)'
                    })
            
            # If we still don't have enough, add knowledge graph info if available
            if len(extracted) < max_results and 'knowledgeGraph' in results:
                kg = results['knowledgeGraph']
                if kg:
                    title = kg.get('title', '')
                    description = kg.get('description', '')
                    if title and description:
                        extracted.append({
                            'title': title,
                            'link': kg.get('url', ''),
                            'snippet': description,
                            'source': 'serper.dev (Knowledge Graph)'
                        })
                        
            return extracted
        except Exception as e:
            logger.error(f"Error extracting Serper results: {e}")
            return []
            
    def _fallback_search(self, query, max_results=5):
        """Basic fallback search when APIs are unavailable"""
        try:
            # Try to do a basic scrape of DuckDuckGo search results
            # DuckDuckGo is more scraping-friendly than Google
            logger.info(f"Attempting DuckDuckGo fallback search for: {query}")
            
            # Format the query for the URL
            import urllib.parse
            encoded_query = urllib.parse.quote_plus(query)
            url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
            
            # Get a random user agent
            headers = self._get_random_headers()
            
            # Make the request
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                # Parse the HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find search results
                results = []
                result_elements = soup.select('.result')
                
                for element in result_elements[:max_results]:
                    title_element = element.select_one('.result__title')
                    snippet_element = element.select_one('.result__snippet')
                    link_element = element.select_one('.result__url')
                    
                    if title_element and link_element:
                        title = title_element.get_text(strip=True)
                        snippet = snippet_element.get_text(strip=True) if snippet_element else ""
                        
                        # Extract href and clean it up
                        link = link_element.get_text(strip=True)
                        if not link.startswith(('http://', 'https://')):
                            link = f"https://{link}"
                        
                        results.append({
                            'title': title,
                            'link': link,
                            'snippet': snippet,
                            'source': 'duckduckgo'
                        })
                
                if results:
                    logger.info(f"DuckDuckGo fallback search found {len(results)} results")
                    return results
        except Exception as e:
            logger.error(f"Error in DuckDuckGo fallback search: {e}")
        
        # Final fallback if everything else fails
        logger.warning("All search methods failed, returning generic fallback result")
        return [{
            'title': f"Search results for {query}",
            'link': f"https://www.google.com/search?q={query}",
            'snippet': f"No direct search results available for '{query}'. Click to search manually.",
            'source': 'fallback'
        }]
        
    def fetch_webpage_content(self, url):
        """Fetch and extract content from a webpage"""
        try:
            logger.info(f"Fetching content from: {url}")
            headers = self._get_random_headers()
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                # Parse the HTML content
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Get the page title
                title = soup.title.string if soup.title else url
                
                # Extract the main content
                # This is a simple implementation and might need to be adjusted
                # for different website structures
                
                # First, try to find the main content
                main_content = ""
                content_tags = soup.find_all(['article', 'main', 'div', 'section'])
                for tag in content_tags:
                    # Skip if it's likely a navigation or header/footer
                    if tag.get('id') and any(x in tag.get('id').lower() for x in ['nav', 'header', 'footer', 'sidebar', 'menu']):
                        continue
                    if tag.get('class') and any(x in ' '.join(tag.get('class')).lower() for x in ['nav', 'header', 'footer', 'sidebar', 'menu']):
                        continue
                        
                    # Get the text content
                    tag_content = tag.get_text(separator=' ', strip=True)
                    if len(tag_content) > 200:  # Only consider substantial content
                        main_content += tag_content + "\n\n"
                        if len(main_content) > 5000:  # Limit the amount of content
                            break
                
                # If we couldn't find good content, take everything from body
                if not main_content:
                    if soup.body:
                        main_content = soup.body.get_text(separator=' ', strip=True)
                
                # Clean up the content
                main_content = ' '.join(main_content.split())  # Remove extra whitespace
                
                return {
                    'title': title,
                    'content': main_content,
                    'url': url
                }
            else:
                logger.warning(f"Failed to fetch content from {url}: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching webpage content from {url}: {e}")
            return None
    
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


class BlogGenerator:
    def __init__(self):
        self.search_engine = WebSearchEngine()
    
    def generate_blog(self, topic=None):
        """Generate a blog using AI and web search data"""
        try:
            # Pick a topic if none provided
            if not topic:
                # Organized IT software topics by categories
                it_software_topics = {
                    "Cloud Computing": [
                        "AWS Lambda vs Azure Functions: Serverless Comparison",
                        "Multi-Cloud Deployment Strategies for Enterprise Applications",
                        "Cloud Cost Optimization Best Practices",
                        "Kubernetes vs Docker Swarm for Container Orchestration",
                        "Serverless Architecture Patterns and Use Cases",
                        "Google Cloud Run vs AWS App Runner",
                        "Cloud-Native Application Development Patterns",
                        "Terraform vs Pulumi for Infrastructure as Code",
                        "Implementing Effective Cloud Disaster Recovery Strategies",
                        "Hybrid Cloud Integration Best Practices"
                    ],
                    "AI and ML": [
                        "MLOps Best Practices for Production AI Systems",
                        "NLP Techniques for Software Documentation",
                        "Computer Vision Applications in Software Testing",
                        "Machine Learning Model Monitoring in Production",
                        "Ethical Considerations in Enterprise AI Development",
                        "LLMs for Code Generation and Refactoring",
                        "AI-Powered Test Automation Frameworks",
                        "Graph Neural Networks for Software Dependency Analysis",
                        "Explainable AI Techniques for Enterprise Applications",
                        "Time Series Forecasting for Infrastructure Planning"
                    ],
                    "DevOps": [
                        "CI/CD Pipeline Optimization for Microservices",
                        "Infrastructure as Code with Terraform and Ansible",
                        "GitOps Workflow for Kubernetes Applications",
                        "Observability Platforms: Prometheus vs Grafana vs Datadog",
                        "DevSecOps: Integrating Security into DevOps Workflows",
                        "ArgoCD vs Flux for Kubernetes Deployments",
                        "Jenkins vs GitHub Actions vs CircleCI: CI/CD Comparison",
                        "Implementing Chaos Engineering in Production",
                        "SRE Practices for High-Availability Systems",
                        "Advanced Docker Optimization Techniques"
                    ],
                    "Software Development": [
                        "Microservices vs Monoliths: Architecture Tradeoffs",
                        "API Gateway Patterns and Implementation",
                        "Domain-Driven Design in Modern Software Development",
                        "Event-Driven Architecture with Kafka and RabbitMQ",
                        "Clean Code Principles for Enterprise Applications",
                        "Hexagonal Architecture Implementation Patterns",
                        "Trunk-Based Development vs Feature Branching",
                        "CQRS and Event Sourcing in Distributed Systems",
                        "Advanced Unit Testing Strategies for Complex Systems",
                        "Functional Programming Patterns in Object-Oriented Languages"
                    ],
                    "Databases": [
                        "NoSQL Database Selection: MongoDB vs Cassandra vs DynamoDB",
                        "Database Sharding Strategies for High-Scale Applications",
                        "Graph Databases: Neo4j vs Amazon Neptune",
                        "Data Warehousing with Snowflake and BigQuery",
                        "Time-Series Database Solutions for Monitoring Applications",
                        "PostgreSQL vs MySQL Performance Optimization",
                        "Multi-Model Databases: When and How to Use Them",
                        "Database Migration Strategies with Zero Downtime",
                        "Distributed SQL Databases: CockroachDB vs YugabyteDB",
                        "In-Memory Databases: Redis vs Memcached"
                    ],
                    "Cybersecurity": [
                        "Zero Trust Architecture Implementation",
                        "Container Security Best Practices",
                        "API Security Testing Strategies",
                        "SAST vs DAST in DevSecOps Pipelines",
                        "Cloud Security Posture Management",
                        "Kubernetes Security Hardening Techniques",
                        "OAuth2 and OpenID Connect Implementation Patterns",
                        "Secrets Management in Modern Applications",
                        "Security Implications of Infrastructure as Code",
                        "Implementing Effective Security Incident Response"
                    ],
                    "Blockchain": [
                        "Smart Contract Development Best Practices",
                        "Blockchain for Supply Chain Management Software",
                        "Private Blockchain Implementation for Enterprise",
                        "Web3 Architecture and Development Patterns",
                        "Solidity Programming: Security Best Practices",
                        "Blockchain Consensus Mechanisms Compared",
                        "Integrating Blockchain with Traditional Enterprise Systems",
                        "Layer 2 Solutions for Blockchain Scalability",
                        "Zero-Knowledge Proofs in Blockchain Applications",
                        "NFT Platform Development Architecture"
                    ],
                    "Quantum Computing": [
                        "Quantum Computing Algorithms for Software Developers",
                        "Quantum Machine Learning: Current Capabilities and Future",
                        "Quantum-Safe Cryptography Implementation",
                        "Hybrid Quantum-Classical Computing Applications",
                        "Quantum Programming Languages: Qiskit vs Cirq",
                        "Preparing Software Architecture for Quantum Advantage",
                        "Quantum Simulation for Optimization Problems",
                        "Quantum Computing's Impact on Encryption Standards",
                        "Error Correction in Quantum Computing Systems",
                        "Quantum SDKs and Development Tools Comparison"
                    ],
                    "Edge Computing": [
                        "Edge Computing Architecture Patterns",
                        "Edge-Cloud Hybrid Application Development",
                        "Real-Time Processing at the Edge: Frameworks and Tools",
                        "Edge Computing for AI Inference",
                        "Kubernetes at the Edge: K3s vs MicroK8s",
                        "Edge Computing Security Challenges and Solutions",
                        "Implementing 5G Edge Computing Applications",
                        "MQTT vs Kafka for Edge-to-Cloud Communication",
                        "Content Delivery Networks for Edge Applications",
                        "Edge Analytics: Architectures and Implementation Patterns"
                    ],
                    "IoT Development": [
                        "IoT Architecture Patterns for Scalable Systems",
                        "MQTT vs CoAP for IoT Communications",
                        "IoT Security: Authentication and Encryption Strategies",
                        "Low-Power IoT Protocol Implementation",
                        "Digital Twin Implementation for IoT Systems",
                        "IoT Data Processing Pipelines",
                        "Firmware Update Strategies for IoT Devices",
                        "IoT Gateway Design and Implementation",
                        "Time Series Data Storage for IoT Applications",
                        "Testing Frameworks for IoT Applications"
                    ],
                    "Low-Code/No-Code": [
                        "Enterprise Integration with Low-Code Platforms",
                        "Extending Low-Code Platforms with Custom Code",
                        "Low-Code vs Traditional Development: Performance Comparison",
                        "API Integration Strategies in Low-Code Environments",
                        "Testing Methodologies for Low-Code Applications",
                        "Low-Code DevOps Implementation",
                        "Power Platform vs Mendix vs OutSystems Comparison",
                        "Building Secure Applications with Low-Code Platforms",
                        "Low-Code Database Design Best Practices",
                        "Implementing CI/CD for Low-Code Applications"
                    ],
                    "Frontend Development": [
                        "Micro-Frontend Architecture Implementation Strategies",
                        "React vs Vue vs Angular: 2025 Performance Comparison",
                        "State Management in Modern Frontend Applications",
                        "WebAssembly for Frontend Performance Optimization",
                        "Advanced CSS Architecture for Large Applications",
                        "Server Components and Streaming SSR",
                        "Frontend Monitoring and Error Tracking Tools",
                        "Implementing Accessibility in Single Page Applications",
                        "GraphQL vs REST for Frontend Data Fetching",
                        "Progressive Web Apps: Implementation Best Practices"
                    ]
                }
                
                # Select a random category and then a topic from that category
                category = random.choice(list(it_software_topics.keys()))
                topic_from_category = random.choice(it_software_topics[category])
                
                # Store both the category and the topic
                self.current_category = category
                topic = topic_from_category
                
            logger.info(f"Generating blog on topic: {topic}")
            
            # Search for information on the topic
            search_results = self.search_engine.search_web(topic, max_results=5)
            
            # Retrieve recent news about the topic
            news_results = self.search_engine.search_web(f"{topic} latest news", max_results=3)
            
            # Use Gemini service if available (preferred)
            if gemini_client:
                try:
                    logger.info("Generating blog with Gemini AI")
                    blog_data = gemini_client.generate_blog_post(
                        topic=topic,
                        research_info=search_results,
                        news_info=news_results
                    )
                    
                    # Format the blog with category
                    blog = {
                        "title": blog_data.get("title") or f"Latest Insights on {topic}",
                        "content": blog_data.get("content") or f"Blog content about {topic} will be available soon.",
                        "topic": topic,
                        "created_at": datetime.now(),
                        "tags": blog_data.get("tags", [topic.lower(), "technology", "development"]),
                        "summary": blog_data.get("summary", "Insights on technology trends."),
                        "published": True,
                        "sources": [result.get("link") for result in search_results if result.get("link")],
                        # Use category from AI response if available, otherwise use the one from topic selection
                        "category": blog_data.get("category") or getattr(self, "current_category", "Technology")
                    }
                    return blog
                except Exception as e:
                    logger.error(f"Error with Gemini blog generation: {e}")
                    # No need to fall back to OpenAI since we removed it
            
            # Create fallback blog if Gemini is not available or failed
            logger.warning("Gemini AI failed or not available, using fallback blog generator")
            
            # Create simple fallback blog with available information
            fallback_blog = {
                "title": f"Latest Insights on {topic}",
                "content": f"# {topic}\n\nThis blog post will explore the latest developments in {topic}. Stay tuned for a detailed analysis.",
                "topic": topic,
                "created_at": datetime.now(),
                "tags": [topic.lower().replace(" ", "-"), "technology", "software", "development"],
                "summary": f"An exploration of {topic} and its implications for software development.",
                "published": True,
                "sources": [result.get("link") for result in search_results if result.get("link")],
                "category": getattr(self, "current_category", "Technology")
            }
            return fallback_blog
            
        except Exception as e:
            logger.error(f"Error generating blog: {e}")
            
            # Default fallback if all AI services are unavailable
            logger.warning("All AI services unavailable, generating simple blog")
            return {
                "title": f"Latest Insights on {topic}",
                "content": f"""# {topic}: The Future of Technology
                
                ## Introduction
                
                {topic} is rapidly evolving and transforming how we interact with technology. This blog post provides an overview of the current state and future trends.
                
                ## Current Developments
                
                Technology continues to advance at an unprecedented pace. Stay tuned for more detailed analysis on this topic in our upcoming blog posts.
                
                ## Conclusion
                
                As we continue to monitor developments in {topic}, we'll share more insights and analysis in future updates.
                """,
                "topic": topic,
                "created_at": datetime.now(),
                "tags": [topic.lower().replace(" ", "-"), "technology", "development", "trends", "innovation"],
                "summary": f"A brief overview of current trends in {topic}.",
                "published": True,
                "sources": []
            }
            
        except Exception as e:
            logger.error(f"Blog generation error: {e}")
            return None
    
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
        # Portfolio-specific knowledge base for Althaf Hussain Syed
        portfolio_knowledge = {
            "personal_info": {
                "name": "Althaf Hussain Syed",
                "title": "DevOps Engineer | Cloud & Infrastructure Specialist",
                "email": "allualthaf42@gmail.com",
                "phone": "8184812249",
                "location": "Hyderabad, India",
                "linkedin": "https://linkedin.com/in/althafhussainsyed",
                "summary": "Certified DevOps Engineer with 3+ years of experience in cloud infrastructure, automation, and CI/CD pipeline engineering. Multi-cloud certified professional with expertise in AWS, GCP, Azure, and Oracle Cloud. Proven track record of reducing operational overhead by 40% and improving incident response time by 30%."
            },
            "skills": {
                "cloud_platforms": ["AWS (Expert)", "Google Cloud Platform (Advanced)", "Microsoft Azure (Advanced)", "Oracle Cloud (Intermediate)"],
                "devops_tools": ["Jenkins (Expert)", "Docker (Advanced)", "Kubernetes (Advanced)", "Terraform (Advanced)", "Ansible (Advanced)", "GitHub Actions (Intermediate)"],
                "programming": ["Python (Advanced)", "Bash Scripting (Advanced)", "Java (Intermediate)"],
                "storage": ["Brocade SAN (Expert)", "HPE 3PAR (Expert)", "HPE Primera (Advanced)", "Dell EMC (Advanced)"]
            },
            "experience": {
                "current_role": "Analyst III Infrastructure Services / DevOps Engineer at DXC Technology (Aug 2022 – Present)",
                "key_achievements": [
                    "Automated infrastructure provisioning using Terraform and Ansible, reducing manual effort by 40%",
                    "Designed and deployed CI/CD pipelines using Jenkins and AWS CodePipeline",
                    "Containerized applications with Docker and orchestrated them using Kubernetes (EKS, GKE, AKS)",
                    "Implemented comprehensive monitoring solutions with AWS CloudWatch and GCP Cloud Monitoring, improving incident response time by 30%",
                    "Managed enterprise storage solutions ensuring 99.9% uptime"
                ]
            },
            "certifications": [
                "AWS Certified Solutions Architect – Associate",
                "Google Cloud Professional Cloud Architect",
                "Microsoft Azure Administrator Associate (AZ-104)",
                "Oracle Cloud Infrastructure Architect Associate",
                "AWS Certified AI Practitioner",
                "AWS Cloud Practitioner",
                "Azure Fundamentals (AZ-900)",
                "GitHub Foundations",
                "Generative AI Certified Professional (Oracle)"
            ],
            "education": [
                "Master of Science in Computer Science - Acharya Nagarjuna University (Dec 2022 – June 2024)",
                "Bachelor of Science in Computer Science - Acharya Nagarjuna University (June 2019 – June 2022)"
            ],
            "projects": [
                {
                    "name": "Multi-Cloud CI/CD Pipeline",
                    "description": "Designed and implemented end-to-end CI/CD pipelines across AWS, GCP, and Azure environments",
                    "technologies": ["Jenkins", "AWS CodePipeline", "GCP Cloud Build", "Docker", "Kubernetes"],
                    "achievements": ["Reduced deployment time by 60%", "Improved code quality through automated testing"]
                },
                {
                    "name": "Infrastructure as Code Implementation", 
                    "description": "Automated infrastructure provisioning using Terraform and Ansible across multiple cloud platforms",
                    "technologies": ["Terraform", "Ansible", "AWS", "GCP", "Azure"],
                    "achievements": ["40% reduction in manual provisioning", "Standardized infrastructure deployment"]
                },
                {
                    "name": "Enterprise Storage Optimization",
                    "description": "Managed and optimized enterprise storage solutions for high-performance computing environments", 
                    "technologies": ["Brocade SAN", "HPE 3PAR", "HPE Primera", "Dell EMC"],
                    "achievements": ["99.9% uptime achievement", "30% improvement in storage efficiency"]
                }
            ],
            "recent_blogs": [
                {
                    "title": "Unlocking Enterprise Agility: Low-Code Integration Platforms in 2025",
                    "summary": "Low-code integration platforms empower enterprises to connect systems, automate workflows, and drive digital transformation with unprecedented speed and efficiency.",
                    "category": "Low-Code/No-Code",
                    "tags": ["low-code", "integration", "enterprise integration", "automation", "digital transformation"]
                },
                {
                    "title": "Architecting for the IoT Tsunami: Building Scalable IoT Systems",
                    "summary": "Explores key architectural patterns for building scalable IoT solutions, including Lambda, Kappa, Microservices, Edge Computing architectures.",
                    "category": "IoT Development", 
                    "tags": ["IoT", "Scalability", "Architecture", "Cloud Computing", "Data Streaming", "Edge Computing", "Microservices"]
                },
                {
                    "title": "Unlocking the Potential of Edge-Cloud Hybrid Applications: A Developer's Guide",
                    "summary": "Edge-cloud hybrid applications combine the strengths of edge and cloud computing to deliver faster, more responsive, and reliable applications.",
                    "category": "Edge Computing",
                    "tags": ["Edge Computing", "Cloud Computing", "Hybrid Cloud", "Application Development", "IoT", "Cloud-Native"]
                }
            ]
        }
        
        # Convert query to lowercase for better matching
        query_lower = query.lower()
        
        # Define allowed topics and keywords
        allowed_tech_keywords = [
            # Portfolio-specific
            'althaf', 'portfolio', 'skills', 'experience', 'projects', 'certifications', 'education', 'contact', 'blogs',
            # DevOps & Cloud
            'devops', 'cloud', 'aws', 'azure', 'gcp', 'google cloud', 'oracle cloud', 'kubernetes', 'docker', 'jenkins',
            'terraform', 'ansible', 'ci/cd', 'pipeline', 'automation', 'infrastructure', 'monitoring', 'deployment',
            # Programming & Tech
            'programming', 'python', 'java', 'bash', 'scripting', 'development', 'software', 'architecture',
            'microservices', 'api', 'database', 'storage', 'networking', 'security', 'linux', 'containers',
            # Emerging Tech
            'ai', 'artificial intelligence', 'machine learning', 'iot', 'edge computing', 'blockchain', 'serverless',
            'low-code', 'no-code', 'integration', 'data', 'analytics', 'big data', 'streaming'
        ]
        
        # Define blocked topics
        blocked_keywords = [
            # Inappropriate content
            'sex', 'sexy', 'porn', 'adult', 'nude', 'explicit', 'dating', 'relationship', 'romance',
            # Violence & illegal
            'kill', 'murder', 'violence', 'weapon', 'bomb', 'terrorist', 'illegal', 'drug', 'hack', 'exploit',
            # Personal attacks
            'stupid', 'idiot', 'dumb', 'hate', 'racist', 'discrimination',
            # Off-topic entertainment
            'movie', 'film', 'celebrity', 'gossip', 'sport', 'football', 'cricket', 'music', 'song',
            # Random topics
            'weather', 'food', 'recipe', 'travel', 'vacation', 'shopping', 'fashion', 'beauty'
        ]
        
        # Check for blocked content first
        if any(blocked_word in query_lower for blocked_word in blocked_keywords):
            return {
                "reply": "I'm focused on technical discussions and Althaf's portfolio. Please ask about DevOps, cloud technologies, programming, or Althaf's professional experience.",
                "source": "Portfolio"
            }
        
        # Check if query contains allowed tech topics or portfolio keywords
        is_tech_related = any(keyword in query_lower for keyword in allowed_tech_keywords)
        
        # If not tech-related and longer than 3 words, redirect
        if not is_tech_related and len(query.split()) > 2:
            return {
                "reply": "I specialize in technical topics and Althaf's portfolio information. Please ask about:\n• DevOps tools and practices\n• Cloud technologies (AWS, Azure, GCP)\n• Programming and software development\n• Althaf's projects and experience\n• Technical certifications and skills",
                "source": "Portfolio"
            }
        
        # Handle greeting and basic interactions first
        if any(keyword in query_lower for keyword in ['hi', 'hello', 'hey', 'thanks', 'thank you']):
            if any(keyword in query_lower for keyword in ['hi', 'hello', 'hey']):
                return {
                    "reply": "Hi! I'm Allu Bot, Althaf's technical portfolio assistant. Ask me about his DevOps skills, cloud experience, programming projects, or any tech-related topics!",
                    "source": "Portfolio"
                }
            elif any(keyword in query_lower for keyword in ['thanks', 'thank you']):
                return {
                    "reply": "You're welcome! Feel free to ask more about Althaf's technical skills or any tech topics.",
                    "source": "Portfolio"
                }
        
        # Handle inappropriate or irrelevant queries with strict guardrails
        inappropriate_keywords = ['fuck', 'shit', 'damn', 'wtf', 'sexy', 'porn', 'sex', 'dating', 'violence', 'drugs', 'gambling']
        if any(keyword in query_lower for keyword in inappropriate_keywords):
            return {
                "reply": "Let's keep our discussion professional and technical. Please ask about Althaf's portfolio, DevOps skills, or technology topics.",
                "source": "Portfolio"
            }
        
        # Strict topic filtering - only allow tech and portfolio topics
        allowed_topics = [
            # Portfolio specific
            'althaf', 'portfolio', 'skills', 'experience', 'projects', 'certifications', 'education', 'contact', 'resume', 'cv',
            # Tech topics - Core areas
            'devops', 'cloud', 'aws', 'azure', 'gcp', 'google cloud', 'oracle cloud', 'kubernetes', 'docker', 
            'jenkins', 'terraform', 'ansible', 'ci/cd', 'infrastructure', 'automation', 'monitoring',
            'programming', 'python', 'java', 'bash', 'scripting', 'coding', 'development', 'software',
            'storage', 'database', 'brocade', 'hpe', 'dell emc', 'san', '3par', 'primera',
            # Advanced tech topics
            'microservices', 'containers', 'orchestration', 'pipeline', 'deployment', 'serverless',
            'iot', 'edge computing', 'hybrid cloud', 'integration', 'api', 'architecture', 'blockchain',
            'security', 'networking', 'virtualization', 'linux', 'windows', 'server', 'ai', 'ml', 'machine learning',
            'artificial intelligence', 'data science', 'analytics', 'big data', 'streaming', 'kafka', 'redis',
            'nosql', 'sql', 'mongodb', 'postgresql', 'mysql', 'elasticsearch', 'nginx', 'apache'
        ]
        
        # Check if query contains any allowed topics
        has_allowed_topic = any(topic in query_lower for topic in allowed_topics)
        
        # Check for greeting keywords
        greeting_keywords = ['hi', 'hello', 'hey', 'thanks', 'thank you', 'good morning', 'good evening', 'good afternoon']
        is_greeting = any(greeting in query_lower for greeting in greeting_keywords)
        
        # Check for chatbot meta questions
        meta_keywords = ['what can you', 'how does this bot', 'what do you know', 'internet access', 'what topics']
        is_meta_question = any(meta in query_lower for meta in meta_keywords)
        
        # Reject queries that don't contain allowed topics (unless it's a greeting or meta question)
        if not has_allowed_topic and not is_greeting and not is_meta_question and len(query_lower.strip()) > 5:
            return {
                "reply": "I'm specialized in discussing Althaf's portfolio and technology topics. Please ask about:\n• Althaf's DevOps skills and experience\n• Cloud technologies (AWS, Azure, GCP)\n• Programming and software development\n• DevOps tools and practices\n• General tech topics in my expertise areas\n\nWhat specific tech topic interests you?",
                "source": "Portfolio"
            }
        
        # Check if the query is about portfolio-specific information
        if any(keyword in query_lower for keyword in ['skills', 'devops', 'tools', 'aws', 'azure', 'gcp', 'cloud', 'kubernetes', 'docker', 'jenkins', 'terraform', 'ansible']):
            if 'skills' in query_lower or 'devops' in query_lower or 'tools' in query_lower:
                return {
                    "reply": f"**Althaf's DevOps Tools:**\n\n• **Cloud:** {', '.join(portfolio_knowledge['skills']['cloud_platforms'])}\n• **DevOps:** {', '.join(portfolio_knowledge['skills']['devops_tools'])}\n• **Programming:** {', '.join(portfolio_knowledge['skills']['programming'])}",
                    "source": "Portfolio"
                }
        
        # Handle chatbot-specific questions
        if any(keyword in query_lower for keyword in ['how does this chatbot work', 'chatbot work', 'bot work']):
            return {
                "reply": "I'm Allu Bot, built specifically for Althaf's technical portfolio. I can discuss:\n• Althaf's DevOps and cloud expertise\n• Technical projects and achievements\n• Programming skills and certifications\n• General tech topics (AI, cloud, DevOps, programming)\n• Industry trends and best practices\n\nI'm designed to keep discussions technical and professional.",
                "source": "Portfolio"
            }
        
        # Handle general tech topic requests
        if any(keyword in query_lower for keyword in ['what can you discuss', 'what topics', 'what do you know']):
            return {
                "reply": "I can help with:\n\n**Althaf's Portfolio:**\n• DevOps skills & experience\n• Cloud certifications (AWS, Azure, GCP)\n• Technical projects & achievements\n• Programming expertise\n\n**Tech Topics:**\n• Cloud computing & DevOps practices\n• Programming languages & frameworks\n• AI/ML, IoT, Edge computing\n• Software architecture & development\n\nWhat would you like to explore?",
                "source": "Portfolio"
            }
        
        # Handle internet access questions
        if any(keyword in query_lower for keyword in ['internet access', 'internet', 'online']):
            return {
                "reply": "I have limited internet access and primarily focus on Althaf's portfolio information. For the most accurate details about his skills and experience, I use his portfolio data directly.",
                "source": "Portfolio"
            }
        
        if any(keyword in query_lower for keyword in ['experience', 'work', 'job', 'role', 'achievements']):
            return {
                "reply": f"**Current Role:** {portfolio_knowledge['experience']['current_role']}\n\n**Key Achievements:**\n• Reduced manual effort by 40% with automation\n• Improved incident response time by 30%\n• Managed enterprise storage with 99.9% uptime",
                "source": "Portfolio"
            }
        
        if any(keyword in query_lower for keyword in ['certifications', 'certified', 'cert']):
            return {
                "reply": f"Althaf holds the following certifications:\n" + "\n".join([f"• {cert}" for cert in portfolio_knowledge['certifications']]),
                "source": "Portfolio"
            }
        
        if any(keyword in query_lower for keyword in ['education', 'degree', 'university', 'college']):
            return {
                "reply": f"Althaf's education:\n" + "\n".join([f"• {edu}" for edu in portfolio_knowledge['education']]),
                "source": "Portfolio"
            }
        
        if any(keyword in query_lower for keyword in ['contact', 'email', 'phone', 'linkedin', 'reach']):
            return {
                "reply": f"You can contact Althaf:\n• Email: {portfolio_knowledge['personal_info']['email']}\n• Phone: {portfolio_knowledge['personal_info']['phone']}\n• LinkedIn: {portfolio_knowledge['personal_info']['linkedin']}\n• Location: {portfolio_knowledge['personal_info']['location']}",
                "source": "Portfolio"
            }
        
        if any(keyword in query_lower for keyword in ['projects', 'project', 'work samples', 'portfolio projects']):
            projects_text = ""
            for i, project in enumerate(portfolio_knowledge['projects'], 1):
                projects_text += f"**{i}. {project['name']}**\n{project['description']}\n• Technologies: {', '.join(project['technologies'])}\n• Key Results: {', '.join(project['achievements'])}\n\n"
            return {
                "reply": f"**Althaf's Key Projects:**\n\n{projects_text.strip()}",
                "source": "Portfolio"
            }
        
        if any(keyword in query_lower for keyword in ['blogs', 'blog', 'articles', 'writing', 'content']):
            blogs_text = ""
            for i, blog in enumerate(portfolio_knowledge['recent_blogs'], 1):
                blogs_text += f"**{i}. {blog['title']}**\n{blog['summary']}\n• Category: {blog['category']}\n• Tags: {', '.join(blog['tags'][:3])}\n\n"
            return {
                "reply": f"**Althaf's Recent Blog Posts:**\n\n{blogs_text.strip()}",
                "source": "Portfolio"
            }
        
        if any(keyword in query_lower for keyword in ['about', 'who', 'introduction', 'summary']):
            return {
                "reply": f"**{portfolio_knowledge['personal_info']['name']}** is a {portfolio_knowledge['personal_info']['title']} based in {portfolio_knowledge['personal_info']['location']}.\n\n{portfolio_knowledge['personal_info']['summary'][:150]}...",
                "source": "Portfolio"
            }
        
        # STRICT GUARDRAIL: Only use internet search for very specific technical queries 
        # that are NOT already covered by portfolio data
        portfolio_covered_keywords = ['althaf', 'portfolio', 'skills', 'experience', 'projects', 'certifications', 'education', 'contact', 'devops tools', 'aws', 'azure', 'gcp', 'jenkins', 'docker', 'kubernetes', 'terraform', 'ansible']
        
        # If query is about portfolio-covered topics, don't search internet
        if any(keyword in query_lower for keyword in portfolio_covered_keywords):
            return {
                "reply": "I have comprehensive information about Althaf's portfolio and skills. Please ask more specifically about his DevOps experience, cloud certifications, technical projects, or contact details.",
                "source": "Portfolio"
            }
        
        # CREDIT PROTECTION: Only search internet for very general tech concepts not specific to Althaf
        general_tech_keywords = ['what is', 'how does', 'explain', 'difference between', 'comparison of', 'best practices for', 'trends in']
        is_general_tech_query = any(phrase in query_lower for phrase in general_tech_keywords)
        
        if not is_general_tech_query:
            return {
                "reply": "I'm designed to discuss Althaf's portfolio and provide general tech insights. For Althaf-specific information, I have comprehensive data. For general tech topics, try phrasing your question like 'What is...?' or 'How does...?' or 'Explain...'",
                "source": "Portfolio"
            }
        
        # Final check: Only proceed with internet search for truly technical queries
        advanced_tech_keywords = ['machine learning', 'artificial intelligence', 'blockchain', 'quantum computing', 'edge computing', 'serverless', 'microservices', 'containerization', 'orchestration']
        if not any(tech in query_lower for tech in advanced_tech_keywords) and not any(tech in query_lower for tech in ['programming', 'software', 'development', 'architecture', 'framework', 'database', 'api']):
            return {
                "reply": "I focus on technical discussions. Please ask about advanced technologies, programming concepts, software architecture, or Althaf's technical expertise.",
                "source": "Portfolio"
            }
        
        # FINAL CREDIT PROTECTION: Add a warning before using internet search
        # This ensures users are aware when we're using external API
        internet_search_warning = "\n\n⚠️ *Using limited internet search for this tech query*"
        
        # Only use internet search as a last resort for tech-related queries
        if not gemini_client:
            return {
                "reply": "I can provide information about Althaf's technical portfolio and skills. Please ask about his DevOps experience, cloud certifications, or programming projects.",
                "source": None
            }
        
        # Initialize web search engine for non-portfolio queries
        search_engine = WebSearchEngine()
        
        # Search for information
        search_results = search_engine.search_web(query)
        
        if not search_results:
            return {
                "reply": "I couldn't find specific information about that. Please try asking about Althaf's portfolio - his skills, experience, certifications, or contact information.",
                "source": None
            }
        
        # Get the first relevant result
        top_result = search_results[0]
        
        # For internet queries, provide brief responses
        context = [{
            'title': top_result.get('title', 'Search Result'),
            'content': top_result.get('snippet', '')[:500]  # Limit content
        }]
        
        # Try using Gemini service for concise, tech-focused responses
        if gemini_client:
            try:
                # Modified prompt for tech-focused, concise responses
                tech_query = f"Provide a brief, technical answer (2-3 sentences max) about this technology topic: {query}. Focus on technical aspects, use cases, or industry relevance."
                reply = gemini_client.answer_query(tech_query, context)
                return {
                    "reply": reply + internet_search_warning,
                    "source": top_result.get("link")
                }
            except Exception as e:
                logger.error(f"Gemini API error: {e}")
                # Fallback to portfolio information instead of generic error
                return {
                    "reply": f"I had trouble accessing external tech information. However, I can tell you about Althaf's expertise:\n\n• **Cloud Platforms:** {', '.join(portfolio_knowledge['skills']['cloud_platforms'])}\n• **DevOps Tools:** {', '.join(portfolio_knowledge['skills']['devops_tools'])}\n• **Programming:** {', '.join(portfolio_knowledge['skills']['programming'])}\n\nPlease ask about his specific experience or projects!",
                    "source": "Portfolio"
                }
        
        # Fallback to brief snippet with tech focus check
        snippet = top_result.get('snippet', 'I found some information but cannot provide complete details.')
        
        # Final tech-relevance check before providing external content
        if not any(tech_word in snippet.lower() for tech_word in ['technology', 'software', 'development', 'programming', 'cloud', 'system', 'data', 'computing', 'technical']):
            return {
                "reply": "I couldn't find relevant technical information about that topic. Please ask about Althaf's portfolio or technology-related subjects.",
                "source": None
            }
        
        return {
            "reply": f"{snippet[:200]}...",
            "source": top_result.get("link")
        }
            
    except Exception as e:
        logger.error(f"Error handling agent query: {e}")
        return {
            "reply": "Sorry, I encountered an error. Please ask about Althaf's portfolio information.",
            "source": None
        }


# Initialize and start the agent scheduler
agent_scheduler = AgentScheduler()

# For API use
def initialize_agent():
    agent_scheduler.schedule_blog_generation("01:00")  # Schedule for 1 AM
    return agent_scheduler.start()

def generate_blog_now(topic=None):
    # Generate a blog using the BlogGenerator class
    blog_generator = BlogGenerator()
    blog = blog_generator.generate_blog(topic)
    
    if blog:
        blog_id = blog_generator.save_blog_to_database(blog)
        if blog_id and isinstance(blog, dict):
            blog["id"] = blog_id
        return blog
    
    # Fallback if blog generation fails completely
    current_date = datetime.now()
    sample_blog = {
        "title": f"Sample Blog Post: {topic or 'Portfolio Technology Overview'}",
        "content": """# Welcome to My Portfolio Blog

## Introduction
This is a sample blog post generated as a fallback. The blog generation functionality encountered an error.

## What This Blog Would Cover
Normally, this blog would provide detailed information about the requested topic with insights from internet research.

## Features of This Portfolio
- Modern React frontend with Tailwind CSS
- FastAPI backend with MongoDB integration
- AI-powered chatbot for interactive portfolio navigation
- Automatic blog generation using AI and web scraping
- Cloud deployment with CI/CD pipelines

Thank you for visiting my portfolio!
""",
        "topic": topic or "Portfolio Technology",
        "created_at": current_date,
        "tags": ["sample", "portfolio", "technology", "web development"],
        "summary": "A sample blog post created as a fallback. This demonstrates the blog display functionality.",
        "published": True,
        "sources": ["https://example.com/sample-source"]
    }
    
    # Save to database if available
    if MONGO_URI and blogs_collection:
        try:
            result = blogs_collection.insert_one(sample_blog)
            logger.info(f"Sample blog saved to database with ID: {result.inserted_id}")
            sample_blog["id"] = str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error saving sample blog to database: {e}")
    
    return sample_blog

# Auto-start when imported
if __name__ == "__main__":
    initialize_agent()