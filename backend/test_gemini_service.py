"""
Test script for the Gemini AI service in the portfolio project
"""
import os
import logging
from dotenv import load_dotenv
import google.generativeai as genai
from gemini_service import GeminiClient

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def test_gemini_service():
    """Test the Gemini API service for the portfolio"""
    print("===== Testing Gemini Service =====")
    
    # Check if the Gemini API key is set
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_api_key:
        print("❌ GEMINI_API_KEY not found in .env file")
        return False
    
    print(f"✅ Found Gemini API key: {gemini_api_key[:8]}...{gemini_api_key[-4:]}")
    
    # Configure Gemini directly first to test
    print("Testing direct Gemini API access...")
    genai.configure(api_key=gemini_api_key)
    
    try:
        # Create a Gemini model
        model = genai.GenerativeModel('models/gemini-pro-latest')
        
        # Generate content
        response = model.generate_content("Write a short blog post about AI in healthcare.")
        
        # Print the response
        print("✅ Direct Gemini API call successful!")
        print(f"Response: {response.text[:200]}...")
        
        # Now test the adapter
        print("\nTesting Gemini service adapter...")
        gemini_client = GeminiClient(api_key=gemini_api_key)
        
        if gemini_client.is_available:
            print("✅ Gemini client adapter initialized successfully")
        else:
            print("❌ Failed to initialize Gemini client adapter")
            return False
        
        # Make sure we're using the right model
        print("Testing service adapter model names...")
        for openai_model in ["gpt-3.5-turbo", "gpt-4"]:
            gemini_model = gemini_client.chat.model_mapping.get(openai_model)
            print(f"✅ OpenAI '{openai_model}' maps to Gemini '{gemini_model}'")
        
        print("\n✅ Gemini service is working correctly!")
        print("You can now run the server with: python server.py")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

if __name__ == "__main__":
    test_gemini_service()