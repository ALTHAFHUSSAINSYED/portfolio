import requests
from bs4 import BeautifulSoup
import random
import time
from datetime import datetime
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class WebScraper:
    def __init__(self):
        # List of tech news sources
        self.sources = [
            {
                "name": "TechCrunch",
                "url": "https://techcrunch.com/",
                "article_selector": "article",
                "title_selector": "h2",
                "link_selector": "a",
                "summary_selector": ".post-block__content"
            },
            {
                "name": "The Verge",
                "url": "https://www.theverge.com/",
                "article_selector": "div.c-compact-river__entry",
                "title_selector": "h2",
                "link_selector": "a",
                "summary_selector": "p.c-entry-box--compact__dek"
            },
            {
                "name": "Wired",
                "url": "https://www.wired.com/",
                "article_selector": "div.summary-item",
                "title_selector": "h3",
                "link_selector": "a",
                "summary_selector": "div.summary-item__dek"
            }
        ]
        
        # Initialize with user agent to avoid being blocked
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
        }
    
    def fetch_articles(self, source_index=None, limit=5):
        """Fetch articles from a tech news source"""
        articles = []
        
        # If source_index is not provided, choose a random source
        if source_index is None:
            source_index = random.randint(0, len(self.sources) - 1)
            
        source = self.sources[source_index]
        
        try:
            response = requests.get(source["url"], headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            article_elements = soup.select(source["article_selector"])
            
            count = 0
            for article in article_elements:
                if count >= limit:
                    break
                    
                try:
                    # Extract title
                    title_element = article.select_one(source["title_selector"])
                    title = title_element.text.strip() if title_element else "No title"
                    
                    # Extract link
                    link_element = title_element.select_one(source["link_selector"]) if title_element else None
                    link = link_element.get('href', '#') if link_element else "#"
                    
                    # Handle relative URLs
                    if link.startswith('/'):
                        link = f"{source['url'].rstrip('/')}{link}"
                    
                    # Extract summary
                    summary_element = article.select_one(source["summary_selector"])
                    summary = summary_element.text.strip() if summary_element else "No summary available"
                    
                    articles.append({
                        "source": source["name"],
                        "title": title,
                        "link": link,
                        "summary": summary,
                        "fetched_at": datetime.now().isoformat()
                    })
                    
                    count += 1
                except Exception as e:
                    print(f"Error extracting article data: {e}")
                    continue
            
        except Exception as e:
            print(f"Error fetching from {source['name']}: {e}")
            
        return articles
    
    def fetch_all_sources(self, limit_per_source=2):
        """Fetch articles from all sources"""
        all_articles = []
        
        for i in range(len(self.sources)):
            articles = self.fetch_articles(source_index=i, limit=limit_per_source)
            all_articles.extend(articles)
            # Add a delay to avoid overloading servers
            time.sleep(2)
            
        return all_articles
    
    def search_tech_topic(self, topic, limit=5):
        """Search for a specific tech topic across sources"""
        search_results = []
        
        for source_index, source in enumerate(self.sources):
            # Modify URL for search if the source has a search endpoint
            search_url = f"{source['url']}search?q={topic.replace(' ', '+')}"
            
            try:
                response = requests.get(search_url, headers=self.headers, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                article_elements = soup.select(source["article_selector"])
                
                count = 0
                for article in article_elements:
                    if count >= limit:
                        break
                        
                    # Extract data similar to fetch_articles method
                    # ... (similar extraction logic)
                    # For brevity, simplified here
                    
                    search_results.append({
                        "source": source["name"],
                        "title": article.select_one(source["title_selector"]).text.strip() if article.select_one(source["title_selector"]) else "No title",
                        "link": article.select_one("a").get("href", "#") if article.select_one("a") else "#",
                        "fetched_at": datetime.now().isoformat()
                    })
                    
                    count += 1
                    
            except Exception as e:
                print(f"Error searching {source['name']} for '{topic}': {e}")
                continue
                
            # Add a delay to avoid overloading servers
            time.sleep(2)
            
        return search_results
        
    def generate_blog_post(self, topic=None):
        """Generate a blog post based on scraped content"""
        if topic:
            articles = self.search_tech_topic(topic)
        else:
            # Pick random source for main topic
            articles = self.fetch_articles(limit=3)
            
        if not articles:
            return None
            
        # Prepare data for blog generation
        blog_data = {
            "articles": articles,
            "timestamp": datetime.now().isoformat(),
            "topic": topic if topic else "Latest Tech News"
        }
        
        return blog_data

if __name__ == "__main__":
    scraper = WebScraper()
    articles = scraper.fetch_all_sources()
    print(json.dumps(articles, indent=2))