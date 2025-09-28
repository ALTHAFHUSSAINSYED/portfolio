"""
Test script for the integrated Gemini API in the portfolio project
"""
import os
import logging
from dotenv import load_dotenv
from gemini_service import GeminiClient

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def test_integration():
    """Test the Gemini integration with the portfolio project"""
    print("===== Testing Gemini Integration =====")
    
    # Check if the Gemini API key is set
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_api_key:
        print("❌ GEMINI_API_KEY not found in .env file")
        return False
    
    print(f"✅ Found Gemini API key: {gemini_api_key[:8]}...{gemini_api_key[-4:]}")
    
    # Initialize the Gemini client
    print("Creating Gemini client...")
    gemini_client = GeminiClient(api_key=gemini_api_key)
    
    if not gemini_client.is_available:
        print("❌ Failed to initialize Gemini client")
        return False
    
    print("✅ Gemini client initialized successfully")
    
    # Test blog generation capability
    print("\n🔄 Testing blog generation capability...")
    try:
        # Create a prompt for blog generation
        system_prompt = """You are an expert blog writer specializing in technology topics. 
        Create a short blog post about artificial intelligence."""
        
        user_prompt = "Write a short blog post about the impact of AI on healthcare."
        
        response = gemini_client.chat.create(
            model="gpt-4",  # This will be mapped to the correct Gemini model
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=1000
        )
        
        blog_content = response.choices[0].message.content
        
        if blog_content and len(blog_content) > 100:
            print(f"✅ Successfully generated blog content ({len(blog_content)} characters)")
            print("\nBlog excerpt:")
            print(f"{blog_content[:200]}...")
            
            # Test if the format matches what the portfolio expects
            try:
                import json
                # Try to parse as JSON (some responses might be formatted as JSON)
                parsed = json.loads(blog_content)
                if isinstance(parsed, dict) and "title" in parsed and "content" in parsed:
                    print("\n✅ Response is properly formatted as JSON with title and content")
            except:
                # If not JSON, check if it's a well-formatted blog post with markdown
                if "#" in blog_content and len(blog_content) > 300:
                    print("\n✅ Response is a well-formatted blog post with markdown")
                else:
                    print("\n⚠️ Response is not in JSON format or well-structured markdown")
        else:
            print("❌ Generated content is too short or empty")
            return False
        
        print("\n✅ All tests passed! Your portfolio is ready to use Gemini API.")
        print("You can now run the server with: python server.py")
        return True
    
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

if __name__ == "__main__":
    test_integration()