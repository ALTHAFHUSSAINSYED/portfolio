"""
Google Gemini API Quota Checker (Simplified)

This script checks the current quota and usage for Google Gemini API using a simplified approach.
"""

import os
import requests
import json
from datetime import datetime
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_gemini_status():
    """
    Check if the Gemini API key is valid and working using direct API calls
    """
    print("\n" + "=" * 60)
    print(" GOOGLE GEMINI API QUOTA CHECKER ".center(60, "="))
    print("=" * 60)
    
    # Get the API key
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        print("\n❌ Error: No GEMINI_API_KEY or GOOGLE_API_KEY found in environment variables")
        print("Please add your API key to the .env file")
        return
    
    print(f"\n🔑 API Key: {api_key[:5]}...{api_key[-4:]}")
    
    # First check - get available models
    try:
        print("\n🔄 Checking available models...")
        models_url = f"https://generativelanguage.googleapis.com/v1/models?key={api_key}"
        
        models_response = requests.get(models_url)
        
        if models_response.status_code == 200:
            models_data = models_response.json()
            available_models = []
            
            if "models" in models_data:
                for model in models_data["models"]:
                    if "gemini" in model.get("name", "").lower():
                        available_models.append(model["name"])
                
                if available_models:
                    print(f"✅ Found {len(available_models)} Gemini models:")
                    for model in available_models:
                        print(f"  - {model}")
                    
                    # Use the first model for testing
                    test_model = available_models[0]
                else:
                    print("❌ No Gemini models found in your account")
                    return
            else:
                print(f"❌ No models found in API response: {models_data}")
                return
        else:
            print(f"❌ Error getting models: HTTP {models_response.status_code}")
            print(f"Response: {models_response.text}")
            return
    except Exception as e:
        print(f"❌ Error requesting models: {str(e)}")
        return
    
    # Second check - test the API with a simple request
    try:
        print(f"\n🔄 Testing API with model: {test_model}")
        test_url = f"https://generativelanguage.googleapis.com/v1/{test_model}:generateContent?key={api_key}"
        
        test_payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": "Hello, please respond with a simple 'Quota check successful' if this request worked."
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.1,
                "topK": 16,
                "topP": 0.8,
                "maxOutputTokens": 20
            }
        }
        
        test_headers = {
            "Content-Type": "application/json"
        }
        
        start_time = time.time()
        test_response = requests.post(test_url, headers=test_headers, json=test_payload)
        response_time = time.time() - start_time
        
        if test_response.status_code == 200:
            test_data = test_response.json()
            
            response_text = ""
            if "candidates" in test_data and test_data["candidates"]:
                if "content" in test_data["candidates"][0]:
                    if "parts" in test_data["candidates"][0]["content"]:
                        for part in test_data["candidates"][0]["content"]["parts"]:
                            if "text" in part:
                                response_text += part["text"]
            
            print(f"✅ API test successful! Response time: {response_time:.2f} seconds")
            print(f"Response: {response_text[:100]}")
            
            # Third check - test rate limits with a quick sequence of requests
            print("\n🔄 Testing rate limits with 3 rapid requests...")
            
            success_count = 0
            total_requests = 3
            
            for i in range(total_requests):
                rate_test_payload = {
                    "contents": [
                        {
                            "parts": [
                                {
                                    "text": f"Test request #{i+1}. Return only one word."
                                }
                            ]
                        }
                    ],
                    "generationConfig": {
                        "temperature": 0.1,
                        "maxOutputTokens": 5
                    }
                }
                
                rate_test_response = requests.post(test_url, headers=test_headers, json=rate_test_payload)
                
                if rate_test_response.status_code == 200:
                    success_count += 1
                    print(f"✅ Rate test #{i+1}: Success")
                else:
                    print(f"❌ Rate test #{i+1}: Failed - {rate_test_response.status_code}")
                    print(f"Response: {rate_test_response.text[:100]}")
                    
                # Small delay between requests to avoid overwhelming the API
                time.sleep(0.2)
            
            print(f"\n✅ Rate test results: {success_count}/{total_requests} requests successful")
            
            if success_count == total_requests:
                print("\n✅ Your Gemini API quota appears to be healthy!")
            elif success_count > 0:
                print("\n⚠️ Your Gemini API quota may be limited, but still functioning.")
            else:
                print("\n❌ Your Gemini API appears to be rate-limited or quota-exhausted.")
        else:
            print(f"❌ API test failed: HTTP {test_response.status_code}")
            print(f"Response: {test_response.text[:200]}")
            
            if "quota" in test_response.text.lower():
                print("\n❌ You appear to have reached your Gemini API quota limits.")
    except Exception as e:
        print(f"❌ Error testing API: {str(e)}")
    
    # Display quota information (standard limits)
    print("\n" + "=" * 60)
    print(" QUOTA INFORMATION ".center(60, "="))
    print("=" * 60)
    print("\nGoogle Gemini API Free Tier Limits:")
    print("• 60 queries per minute")
    print("• Approximately 60,000 tokens per minute")
    print("• Maximum context length varies by model")
    
    print("\nEstimated Maximum Usage (Free Tier):")
    print(f"• Requests per day: {60 * 60 * 24:,} (theoretical maximum)")
    print(f"• Tokens per month: {60000 * 60 * 24 * 30:,} (theoretical maximum)")
    
    print("\nNote: Google doesn't provide a direct API to check remaining quota.")
    print("To monitor usage, visit the Google AI Studio dashboard:")
    print("https://aistudio.google.com/app/apikey")
    
    print("\n" + "=" * 60)
    print(f" Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ".center(60, "="))
    print("=" * 60)

if __name__ == "__main__":
    check_gemini_status()