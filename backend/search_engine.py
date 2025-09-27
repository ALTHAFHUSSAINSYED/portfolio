import os
import requests
import json
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

class SearchEngine:
    def __init__(self):
        # Google Custom Search API credentials
        self.api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
        self.custom_search_engine_id = os.getenv("GOOGLE_CSE_ID")
        self.search_url = "https://www.googleapis.com/customsearch/v1"
        
        # Use DuckDuckGo as a fallback (doesn't require API key)
        self.ddg_search_url = "https://api.duckduckgo.com/"
    
    def google_search(self, query, num_results=5):
        """
        Perform a search using Google Custom Search API
        """
        if not self.api_key or not self.custom_search_engine_id:
            print("Google Search API credentials not found.")
            return self.duckduckgo_search(query, num_results)
        
        params = {
            'q': query,
            'key': self.api_key,
            'cx': self.custom_search_engine_id,
            'num': min(num_results, 10)  # Max 10 results per request for CSE API
        }
        
        try:
            response = requests.get(self.search_url, params=params)
            response.raise_for_status()
            results = response.json()
            
            formatted_results = []
            if 'items' in results:
                for item in results['items']:
                    formatted_results.append({
                        'title': item.get('title', ''),
                        'link': item.get('link', ''),
                        'snippet': item.get('snippet', ''),
                        'source': 'Google Search',
                        'fetched_at': datetime.now().isoformat()
                    })
            
            return formatted_results
        except Exception as e:
            print(f"Google search error: {e}")
            # Fall back to DuckDuckGo if Google API fails
            return self.duckduckgo_search(query, num_results)
    
    def duckduckgo_search(self, query, num_results=5):
        """
        Perform a search using DuckDuckGo API
        """
        params = {
            'q': query,
            'format': 'json',
            'no_html': 1,
            'skip_disambig': 1
        }
        
        try:
            response = requests.get(self.ddg_search_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            formatted_results = []
            
            # Extract abstract if available
            if data.get('Abstract'):
                formatted_results.append({
                    'title': data.get('Heading', query),
                    'link': data.get('AbstractURL', ''),
                    'snippet': data.get('Abstract', ''),
                    'source': 'DuckDuckGo',
                    'fetched_at': datetime.now().isoformat()
                })
            
            # Add related topics
            if data.get('RelatedTopics'):
                count = 0
                for topic in data.get('RelatedTopics', []):
                    if count >= num_results - len(formatted_results):
                        break
                    
                    if 'Text' in topic and 'FirstURL' in topic:
                        formatted_results.append({
                            'title': topic.get('Text', '').split(' - ')[0] if ' - ' in topic.get('Text', '') else topic.get('Text', ''),
                            'link': topic.get('FirstURL', ''),
                            'snippet': topic.get('Text', ''),
                            'source': 'DuckDuckGo',
                            'fetched_at': datetime.now().isoformat()
                        })
                        count += 1
            
            return formatted_results
        except Exception as e:
            print(f"DuckDuckGo search error: {e}")
            return []
    
    def search(self, query, num_results=5):
        """
        General search function that tries Google first, then falls back to DuckDuckGo
        """
        return self.google_search(query, num_results)

if __name__ == "__main__":
    engine = SearchEngine()
    results = engine.search("latest AI technology trends")
    print(json.dumps(results, indent=2))