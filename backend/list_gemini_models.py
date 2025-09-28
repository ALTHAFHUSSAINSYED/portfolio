"""
List available Gemini models
"""

import os
import logging
from dotenv import load_dotenv
import google.generativeai as genai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def list_models():
    """List all available Gemini models"""
    try:
        # Get API key
        api_key = os.environ.get('GOOGLE_API_KEY') or os.environ.get('GEMINI_API_KEY')
        if not api_key:
            logger.error("No API key found for Gemini")
            return
            
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # List models
        models = genai.list_models()
        print("Available Models:")
        for model in models:
            print(f"- {model.name}")
            print(f"  Supported generation methods: {model.supported_generation_methods}")
        
    except Exception as e:
        logger.error(f"Error listing models: {e}")

if __name__ == "__main__":
    list_models()