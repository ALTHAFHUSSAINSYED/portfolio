import os
import sys
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_api():
    """Test the backend API integration with the new AI service"""
    # Get the server URL from environment or use default
    server_url = os.getenv("API_URL", "http://localhost:8000")
    
    print(f"Testing API at {server_url}")
    
    # Test endpoints
    test_chat()
    test_blog_generation()

def test_chat():
    """Test the chat endpoint"""
    server_url = os.getenv("API_URL", "http://localhost:8000")
    
    print("\n=== Testing Chat Endpoint ===")
    
    # Prepare request
    url = f"{server_url}/api/chat"
    payload = {
        "message": "Tell me about your portfolio projects",
        "session_id": "test_session"
    }
    
    try:
        # Make the request
        response = requests.post(url, json=payload, timeout=30)
        
        # Check if the request was successful
        if response.status_code == 200:
            result = response.json()
            print("Chat response successful!")
            print(f"Reply: {result.get('reply')[:150]}...")
            if result.get('source'):
                print(f"Source: {result.get('source')}")
        else:
            print(f"Error: HTTP {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Error making chat request: {e}")

def test_blog_generation():
    """Test the blog generation endpoint"""
    server_url = os.getenv("API_URL", "http://localhost:8000")
    
    print("\n=== Testing Blog Generation Endpoint ===")
    
    # Prepare request
    url = f"{server_url}/api/blogs/generate"
    payload = {
        "topic": "Modern JavaScript Frameworks"
    }
    
    try:
        # Make the request
        response = requests.post(url, json=payload, timeout=60)
        
        # Check if the request was successful
        if response.status_code == 200:
            result = response.json()
            print("Blog generation successful!")
            print(f"Title: {result.get('title')}")
            print(f"Summary: {result.get('summary')}")
            print(f"Tags: {', '.join(result.get('tags', []))}")
            print(f"Content length: {len(result.get('content', ''))}")
        else:
            print(f"Error: HTTP {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Error making blog generation request: {e}")

if __name__ == "__main__":
    test_api()