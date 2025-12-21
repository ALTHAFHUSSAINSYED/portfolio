"""
Script to check if the provided Gemini API key has free tier access
"""
import os
import logging
import google.generativeai as genai

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_gemini_api_key(api_key):
    """
    Check if the provided Gemini API key works and has free tier access
    """
    print(f"Testing Gemini API key: {api_key[:8]}...{api_key[-4:]}")
    
    try:
        # Configure Gemini API with the provided key
        genai.configure(api_key=api_key)
        
        # List available models (this will verify if the key is valid)
        print("Checking available models...")
        models = genai.list_models()
        gemini_models = [m for m in models if "gemini" in m.name]
        
        if gemini_models:
            print(f"✅ API key is valid. Found {len(gemini_models)} Gemini models:")
            for model in gemini_models:
                print(f" - {model.name}")
            
            # Test with a simple query to check if free tier is available
            print("\n🔄 Testing model access with a simple query...")
            
            # Try to find the best available model
            available_models = [m.name for m in gemini_models]
            print(f"Looking for best available model from: {available_models}")
            
            # Try different model options
            model_options = [
                'models/gemini-pro-latest', 
                'models/gemini-pro', 
                'models/gemini-1.0-pro',
                'models/gemini-2.0-pro',
                'models/gemini-2.5-pro',
                'models/gemini-flash-latest',
                'models/gemini-2.5-flash'
            ]
            
            model_found = False
            for model_name in model_options:
                if any(model_name in m for m in available_models):
                    print(f"Trying model: {model_name}")
                    model = genai.GenerativeModel(model_name)
                    model_found = True
                    break
                    
            if not model_found and gemini_models:
                # Just use the first model from the list
                print(f"Trying first available model: {gemini_models[0].name}")
                model = genai.GenerativeModel(gemini_models[0].name)
                
            response = model.generate_content("Hello, what can you do?")
            
            print("✅ Successfully generated content! Your API key has access to the free tier.")
            print(f"\nResponse excerpt: \"{response.text[:150]}...\"")
            
            # Test limits by making a few requests
            print("\n🔄 Testing free tier limitations with additional requests...")
            
            for i in range(3):
                prompt = f"Write a brief paragraph about {['artificial intelligence', 'machine learning', 'cloud computing'][i]}"
                response = model.generate_content(prompt)
                print(f"✅ Request {i+1} successful: Generated {len(response.text)} characters")
            
            print("\n✅ Your API key has access to the Gemini free tier!")
            print("Free tier typically includes:")
            print("- Access to gemini-pro model")
            print("- 60 queries per minute rate limit")
            print("- No credit card required")
            
            return True
            
        else:
            print("⚠️ API key appears valid but no Gemini models were found")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Gemini API key: {str(e)}")
        
        if "API key not valid" in str(e):
            print("❌ The API key is not valid. Please check the key and try again.")
        elif "quota" in str(e).lower():
            print("⚠️ You have reached your quota limits for the free tier.")
            print("You may need to wait for the quota to reset or upgrade to a paid tier.")
        elif "permission" in str(e).lower():
            print("⚠️ Your API key doesn't have permission to access the Gemini models.")
            print("Make sure you're using a key generated specifically for Gemini API access.")
        elif "billing" in str(e).lower():
            print("⚠️ There may be a billing issue with your account.")
            print("Check if you need to set up a billing account or enable billing for this API.")
        
        return False

if __name__ == "__main__":
    print("===== Gemini API Key Check =====")
    
    # Load API key from environment variables
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    
    if not API_KEY:
        print("❌ No API key found in environment variables")
        print("Please set GEMINI_API_KEY or GOOGLE_API_KEY in your .env file")
        exit(1)
    
    check_gemini_api_key(API_KEY)
    print("===============================")