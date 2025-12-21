"""
Test script for verifying Gemini API integration
"""
import os
from dotenv import load_dotenv
import logging
from gemini_service import GeminiClient

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def test_gemini_api():
    """Test if the Gemini API is working correctly"""
    try:
        # Get API key from environment variable
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            print("GEMINI_API_KEY not found in environment variables")
            print("Please set this variable in your .env file")
            return False
            
        # Initialize Gemini client
        gemini_client = GeminiClient(api_key=api_key)
        
        if not gemini_client.is_available:
            print("Failed to initialize Gemini client")
            return False
            
        # Test a simple completion
        response = gemini_client.chat.create(
            model="gemini-pro",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Explain how neural networks work in 2 sentences."}
            ],
            max_tokens=100
        )
        
        # Print response
        print("Gemini API test successful!")
        print("\nResponse:")
        print(response.choices[0].message.content)
        
        return True
    except Exception as e:
        print(f"Gemini API test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing Gemini API integration...")
    success = test_gemini_api()
    print(f"\nTest {'succeeded' if success else 'failed'}")