"""
LangChain proxy for Google Gemini AI integration

This module provides a convenient way to use Google Gemini models with LangChain's interfaces.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import google.generativeai as genai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class GeminiProxy:
    """
    A simple proxy class for Google Gemini AI models.
    """
    
    def __init__(self, model_name="models/gemini-2.0-flash", temperature=0.7):
        """
        Initialize the Gemini proxy.
        
        Args:
            model_name (str): The Gemini model to use (default: gemini-1.5-pro)
            temperature (float): Controls randomness in outputs (0.0-1.0)
        """
        self.api_key = os.environ.get('GOOGLE_API_KEY') or os.environ.get('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("No Gemini API key found. Set GOOGLE_API_KEY or GEMINI_API_KEY environment variable.")
        
        logger.info(f"Initializing Gemini model: {model_name}")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Initialize model
        self.model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=genai.GenerationConfig(temperature=temperature)
        )
        
        # Create conversation history
        self._conversation = None
        
    def generate_text(self, prompt: str) -> str:
        """
        Generate text using the Gemini model with a simple prompt.
        
        Args:
            prompt (str): The text prompt to send to the model
            
        Returns:
            str: The generated text response
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error generating text with Gemini: {e}")
            return f"Error: {str(e)}"
    
    def start_chat(self) -> None:
        """
        Start a new chat session with memory.
        """
        self._conversation = self.model.start_chat(history=[])
    
    def chat(self, user_input: str) -> str:
        """
        Process a message in a conversation with memory.
        
        Args:
            user_input (str): The user's message
            
        Returns:
            str: The AI's response
        """
        try:
            # Create a conversation if not already created
            if self._conversation is None:
                self.start_chat()
                
            # Process the message and get a response
            response = self._conversation.send_message(user_input)
            return response.text
        except Exception as e:
            logger.error(f"Error in chat with Gemini: {e}")
            return f"I encountered an error: {str(e)}"


def get_langchain_gemini():
    """
    Import and configure LangChain with Google Gemini - do the imports here to avoid 
    import errors if LangChain is not installed.
    
    Returns:
        dict: Dictionary containing LangChain components configured for Gemini
    """
    try:
        # Try to import LangChain components
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain.chains import LLMChain
        from langchain_core.prompts import PromptTemplate
        
        # Get API key
        api_key = os.environ.get('GOOGLE_API_KEY') or os.environ.get('GEMINI_API_KEY')
        if not api_key:
            logger.error("No API key found for Gemini")
            return None
        
        # Initialize LangChain with Gemini
        llm = ChatGoogleGenerativeAI(
            model="models/gemini-2.0-flash",
            temperature=0.7,
            google_api_key=api_key
        )
        
        return {
            "llm": llm,
            "LLMChain": LLMChain,
            "PromptTemplate": PromptTemplate
        }
        
    except ImportError as e:
        logger.error(f"Error importing LangChain components: {e}")
        return None