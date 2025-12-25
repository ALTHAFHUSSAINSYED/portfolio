"""
Blog Researcher Module
Uses SERPER API to gather fresh insights, trends, and authoritative sources for blog topics.
"""

import os
import json
import logging
import time
import requests
from typing import Dict, List, Any
from datetime import datetime
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BlogResearcher")

class BlogResearcher:
    def __init__(self):
        load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '.env'))
        self.serper_api_key = os.getenv("SERPER_API_KEY")
        
        if not self.serper_api_key:
            logger.warning("SERPER_API_KEY not found. Research will fail.")

    def search_google(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """Perform a Google search via SERPER API"""
        url = "https://google.serper.dev/search"
        payload = json.dumps({
            "q": query,
            "num": num_results,
            "tbs": "qdr:w"  # Past week for freshness
        })
        headers = {
            'X-API-KEY': self.serper_api_key,
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(url, headers=headers, data=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"SERPER API failed: {str(e)}")
            return {}

    def analyze_trends(self, category: str) -> Dict[str, Any]:
        """Gather research data for a specific category"""
        logger.info(f"Starting research for category: {category}")
        
        # 1. Broad trend search
        trend_query = f"latest {category} trends {datetime.now().year} technology breakthroughs"
        trends_data = self.search_google(trend_query, num_results=5)
        
        # 2. Specific impactful news
        news_query = f"major {category} failures or success stories {datetime.now().year}"
        news_data = self.search_google(news_query, num_results=3)
        
        # 3. Extract key data points
        headlines = []
        sources = []
        
        # Process organic results
        if 'organic' in trends_data:
            for item in trends_data['organic']:
                headlines.append(item.get('title'))
                sources.append({
                    "title": item.get('title'),
                    "link": item.get('link'),
                    "snippet": item.get('snippet')
                })
                
        if 'organic' in news_data:
             for item in news_data['organic']:
                sources.append({
                    "title": item.get('title'),
                    "link": item.get('link'),
                    "snippet": item.get('snippet')
                })

        # 4. Construct Research Artifact
        research_artifact = {
            "category": category,
            "research_date": datetime.now().isoformat(),
            "query_used": trend_query,
            "headlines": headlines[:5], # Top 5 headlines
            "key_insights": [s['snippet'] for s in sources[:5]],
            "authoritative_sources": sources,
            "raw_data_summary": f"Found {len(sources)} sources from SERPER."
        }
        
        logger.info(f"Research complete for {category}. Found {len(sources)} sources.")
        return research_artifact

    def get_fallback_research(self, category: str) -> Dict[str, Any]:
        """Provide fallback generic research data if API fails"""
        logger.warning(f"Using fallback research for {category}")
        return {
            "category": category,
            "research_date": datetime.now().isoformat(),
            "headlines": [f"The Future of {category}", f"{category} Best Practices"],
            "key_insights": ["Focus on efficiency", "Security is paramount"],
            "authoritative_sources": [],
            "status": "fallback"
        }

if __name__ == "__main__":
    # Simple test
    researcher = BlogResearcher()
    result = researcher.analyze_trends("DevOps")
    print(json.dumps(result, indent=2))
