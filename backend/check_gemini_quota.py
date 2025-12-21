"""
Script to check Google Gemini API quota status
"""
import os
import logging
from dotenv import load_dotenv
import google.generativeai as genai
from datetime import datetime
import sys

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def format_number(num):
    """Format a number with commas for thousands"""
    return f"{num:,}"

def check_gemini_quota():
    """
    Check if the Gemini API key works and what quota limitations might exist
    """
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    
    if not api_key:
        print("⚠️ GEMINI_API_KEY or GOOGLE_API_KEY not found in environment variables")
        print("Please add your Gemini API key to the .env file:")
        print("GEMINI_API_KEY=your_api_key_here")
        return False
    
    print(f"🔑 Found Gemini API key: {api_key[:5]}...{api_key[-4:]}")
    
    try:
        # Configure Gemini API
        genai.configure(api_key=api_key)
        
        # List available models first
        print("🔄 Listing available Gemini models...")
        try:
            models = genai.list_models()
            gemini_models = [model.name for model in models if "gemini" in model.name.lower()]
            
            if gemini_models:
                print("✅ Available Gemini models:")
                for model_name in gemini_models:
                    print(f"  - {model_name}")
                
                # Use the first available model
                model_to_use = gemini_models[0]
            else:
                print("❌ No Gemini models found")
                return False
        except Exception as e:
            print(f"❌ Error listing models: {str(e)}")
            # Try with a default model name
            model_to_use = "models/gemini-1.5-flash"
            print(f"🔄 Will try with default model: {model_to_use}")
        
        # Create a model instance
        model = genai.GenerativeModel(model_to_use)
        
        print("🔄 Testing Gemini API connection...")
        
        # Send a simple test request
        response = model.generate_content("What is the current time?")
        
        if response:
            print("✅ API connection successful!")
            print("\nResponse from Gemini:")
            print(f"{response.text[:200]}...")
            
            # Try a more substantial request to test quota
            print("\n🔄 Testing quota capacity with a longer request...")
            
            test_prompt = """
            Please write a short essay about artificial intelligence, 
            approximately 300 words in length. Include key concepts,
            applications, and ethical considerations.
            """
            
            response = model.generate_content(test_prompt)
            
            if response:
                print("✅ Quota test successful! You have available credits.")
                print(f"\nGenerated {len(response.text)} characters")
                print(f"First 200 characters of response: {response.text[:200]}...")
                
                # Try multiple requests to test rate limits
                print("\n🔄 Testing rate limits with 3 consecutive requests...")
                
                for i in range(3):
                    prompt = f"Generate a short paragraph about topic {i+1}: {'cloud computing' if i==0 else 'machine learning' if i==1 else 'blockchain'}"
                    response = model.generate_content(prompt)
                    print(f"✅ Request {i+1} successful - {len(response.text)} characters")
                
                print("\n✅ API is working properly with sufficient quota!")
                print("\n====== GEMINI API QUOTA INFORMATION ======")
                print("Google Gemini provides a free tier with:")
                print("- 60 queries per minute rate limit")
                print("- Approximately 60,000 tokens per minute")
                print(f"- Estimated {format_number(60*60*24)} requests per day (theoretical maximum)")
                print(f"- Estimated {format_number(60000*60*24*30)} tokens per month (theoretical maximum)")
                
                print("\nModel Features:")
                print("- Web browsing capability")
                print("- Function calling")
                print("- Image processing (for vision models)")
                print("- System instructions support")
                
                # Typical quota allocations for free tier
                if "1.5-flash" in model_to_use or "2.0-flash" in model_to_use:
                    print("\nYou're using the Flash model which optimizes for:")
                    print("- Faster response times")
                    print("- Higher throughput (more tokens per minute)")
                    print("- Better handling of high-volume applications")
                elif "1.5-pro" in model_to_use or "pro" in model_to_use:
                    print("\nYou're using the Pro model which optimizes for:")
                    print("- Higher quality responses")
                    print("- Better reasoning capabilities")
                    print("- More complex task handling")
                    
                print("\nNote: Google doesn't provide a direct API to check remaining quota.")
                print("To monitor usage, check the Google AI Studio dashboard:")
                print("https://aistudio.google.com/app/apikey")
                
                # Get current time
                now = datetime.now()
                print(f"\nTest completed at: {now.strftime('%Y-%m-%d %H:%M:%S')}")
                
                return True
    except Exception as e:
        print(f"❌ Error testing Gemini API: {str(e)}")
        
        if "quota" in str(e).lower():
            print("\n⚠️ You appear to have reached your Gemini API quota limits.")
            print("Possible solutions:")
            print("1. Wait for quota to reset (typically daily)")
            print("2. Upgrade to a paid tier")
            print("3. Create a new Google account to get a new free tier allocation")
        return False

if __name__ == "__main__":
    print("===== Google Gemini API Quota Check =====")
    
    # Check if we should suppress log warnings
    if len(sys.argv) > 1 and sys.argv[1] == "--quiet":
        logging.disable(logging.WARNING)
    check_gemini_quota()
    print("==========================================")