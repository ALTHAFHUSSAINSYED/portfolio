import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_serper_api():
    """Test the Serper.dev API integration"""
    serper_api_key = os.getenv("SERPER_API_KEY")
    
    if not serper_api_key:
        print("ERROR: SERPER_API_KEY environment variable not found!")
        print("Please add your Serper.dev API key to the .env file:")
        print("SERPER_API_KEY=your_api_key_here")
        return False
    
    print("Serper.dev API key found. Testing connection...")
    
    # Prepare request to Serper.dev
    url = "https://google.serper.dev/search"
    headers = {
        'X-API-KEY': serper_api_key,
        'Content-Type': 'application/json'
    }
    payload = {
        'q': 'modern web development trends',
        'num': 5
    }
    
    try:
        # Make the request
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        # Check if the request was successful
        if response.status_code == 200:
            results = response.json()
            
            # Check if we got some organic results
            if 'organic' in results and results['organic']:
                print("\nConnection to Serper.dev API successful!")
                print(f"Found {len(results['organic'])} organic results")
                
                # Print the first result
                first_result = results['organic'][0]
                print("\nFirst search result:")
                print(f"Title: {first_result.get('title', 'N/A')}")
                print(f"Link: {first_result.get('link', 'N/A')}")
                print(f"Snippet: {first_result.get('snippet', 'N/A')[:100]}...")
                
                # Extract people also ask if available
                if 'peopleAlsoAsk' in results and results['peopleAlsoAsk']:
                    print(f"\nFound {len(results['peopleAlsoAsk'])} 'People Also Ask' questions")
                    
                # Extract related searches if available
                if 'relatedSearches' in results and results['relatedSearches']:
                    print(f"Found {len(results['relatedSearches'])} related searches")
                
                print("\nSerper.dev API integration test successful!")
                return True
            else:
                print("\nConnection successful but no organic search results found.")
                print("This might indicate an issue with the search query or API limitations.")
                return False
        else:
            print(f"\nError connecting to Serper.dev API: HTTP {response.status_code}")
            print("Response:", response.text)
            return False
    except Exception as e:
        print(f"\nException during Serper.dev API test: {e}")
        return False

if __name__ == "__main__":
    test_serper_api()