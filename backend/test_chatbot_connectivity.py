import requests
import json

# Local server URL (adjust port if needed)
API_URL = "http://127.0.0.1:8000/api/ask-all-u-bot"

# Test queries for each data source
queries = [
    {
        "desc": "ChromaDB test (portfolio topic)",
        "message": "Tell me about Althaf's React projects."
    },
    {
        "desc": "MongoDB test (blog topic)",
        "message": "Show me the latest blog post about AI."
    },
    {
        "desc": "Internet test (tech trend)",
        "message": "What are the latest web development trends in 2025?"
    }
]

def test_chatbot():
    for q in queries:
        print(f"\n--- {q['desc']} ---")
        payload = {"message": q["message"]}
        try:
            response = requests.post(API_URL, json=payload)
            if response.status_code == 200:
                data = response.json()
                print(f"Reply: {data.get('reply')}")
                print(f"Source: {data.get('source')}")
            else:
                print(f"Error: HTTP {response.status_code}")
        except Exception as e:
            print(f"Request failed: {e}")

if __name__ == "__main__":
    test_chatbot()
