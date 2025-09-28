"""
Test script for Gemini API Proxy

This script demonstrates how to use the Gemini API proxy with optional LangChain integration.
"""

import os
import logging
from dotenv import load_dotenv

# Import our proxy
from langchain_proxy import GeminiProxy, get_langchain_gemini

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def test_gemini_proxy():
    """Test the direct Gemini proxy"""
    try:
        # Create the proxy
        proxy = GeminiProxy()
        
        # Generate text
        prompt = "Write a Python function to calculate factorial with recursion"
        logger.info(f"Sending prompt: {prompt}")
        
        response = proxy.generate_text(prompt)
        print("\n=== Generated Text ===")
        print(response)
        
        # Test chat functionality
        proxy.start_chat()
        chat_response = proxy.chat("Can you help me understand how to use generators in Python?")
        
        print("\n=== Chat Response ===")
        print(chat_response)
        
        return True
    except Exception as e:
        logger.error(f"Error testing Gemini proxy: {e}")
        return False

def test_langchain_integration():
    """Test LangChain integration if available"""
    try:
        # Get LangChain components
        lc = get_langchain_gemini()
        if not lc:
            logger.warning("LangChain components not available")
            return False
        
        # Create a simple prompt template
        template = "Write a {length} paragraph about {topic}"
        prompt = lc["PromptTemplate"].from_template(template)
        
        # Create a chain
        chain = lc["LLMChain"](llm=lc["llm"], prompt=prompt)
        
        # Generate content
        result = chain.run(length="short", topic="artificial intelligence")
        
        print("\n=== LangChain Result ===")
        print(result)
        
        return True
    except Exception as e:
        logger.error(f"Error testing LangChain integration: {e}")
        return False

if __name__ == "__main__":
    print("\n===== Testing Gemini API Proxy =====")
    
    # Test the direct Gemini proxy
    print("\n🔄 Testing Gemini Proxy...")
    gemini_result = test_gemini_proxy()
    
    # Test LangChain integration if available
    print("\n🔄 Testing LangChain integration (if available)...")
    langchain_result = test_langchain_integration()
    
    # Print summary
    print("\n===== Test Summary =====")
    print(f"Gemini Direct API: {'✅ Successful' if gemini_result else '❌ Failed'}")
    print(f"LangChain Integration: {'✅ Successful' if langchain_result else '❌ Failed or Not Available'}")