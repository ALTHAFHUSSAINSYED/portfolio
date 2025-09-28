"""
Google Gemini AI Service for the portfolio project.

This module provides integration with Google's Gemini API as an alternative to OpenAI.
It maintains the same interface as the OpenAI client for easy swapping.
"""

import os
import logging
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from dotenv import load_dotenv

logger = logging.getLogger('AlluAgent')

# Load environment variables
load_dotenv()

class GeminiClient:
    """
    A client for the Google Gemini API that follows the same interface as OpenAI for easy swapping.
    """
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Gemini client with the provided API key or from environment variables.
        
        Args:
            api_key: The Gemini API key. If None, will try to load from GEMINI_API_KEY environment variable.
        """
        try:
            self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
            if not self.api_key:
                logger.warning("GEMINI_API_KEY not found in environment variables")
                self.is_available = False
                return
                
            # Configure the Gemini API
            genai.configure(api_key=self.api_key)
            
            # Set default safety settings to be similar to OpenAI defaults
            self.safety_settings = [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                }
            ]
            
            # Test the API connection
            self._test_model = genai.GenerativeModel(model_name="models/gemini-pro-latest")
            self._test_model.generate_content("Test")
            
            self.is_available = True
            logger.info("Gemini API client initialized successfully")
            
            # Initialize model for chat completions
            self.chat = self.ChatCompletions(self)
            
        except Exception as e:
            logger.error(f"Gemini client initialization error: {e}")
            self.is_available = False
    
    class ChatCompletions:
        """
        An adapter class to mimic OpenAI's ChatCompletions API.
        """
        def __init__(self, parent):
            self.parent = parent
            self.model_mapping = {
                "gpt-3.5-turbo": "models/gemini-pro-latest",
                "gpt-4": "models/gemini-pro-latest",  # Use Pro as default fallback
                "gpt-4-turbo": "models/gemini-pro-latest",
            }
        
        def create(self, model: str, messages: List[Dict[str, str]], max_tokens: int = None, temperature: float = 0.7):
            """
            Create a chat completion using Gemini API with the same interface as OpenAI.
            
            Args:
                model: The model name (will be mapped to appropriate Gemini model)
                messages: A list of message dictionaries with 'role' and 'content' keys
                max_tokens: Maximum number of tokens to generate
                temperature: Sampling temperature (0.0 to 1.0)
                
            Returns:
                A response object with a similar structure to OpenAI's response
            """
            try:
                # Map the model name
                gemini_model = self.model_mapping.get(model, "gemini-pro")
                
                # Create the Gemini model
                generation_model = genai.GenerativeModel(
                    model_name=gemini_model,
                    generation_config={
                        "temperature": temperature,
                        "max_output_tokens": max_tokens if max_tokens else 2048,
                        "top_p": 0.95,
                    },
                    safety_settings=self.parent.safety_settings
                )
                
                # Convert OpenAI message format to Gemini format
                prompt = self._convert_messages_to_prompt(messages)
                
                # Generate content
                response = generation_model.generate_content(prompt)
                
                # Convert the response to match OpenAI's format
                return self._convert_to_openai_response(response)
                
            except Exception as e:
                logger.error(f"Gemini API error: {e}")
                raise
    
        def _convert_messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
            """
            Convert OpenAI message format to a prompt string for Gemini.
            
            Args:
                messages: A list of message dictionaries
                
            Returns:
                A formatted prompt string
            """
            # Extract system message if present
            system_message = next((m["content"] for m in messages if m["role"] == "system"), None)
            
            # Format the prompt string
            prompt = ""
            
            if system_message:
                prompt += f"System: {system_message}\n\n"
            
            # Add the conversation history
            for message in messages:
                if message["role"] == "system":
                    continue
                    
                role = "User" if message["role"] == "user" else "Assistant"
                prompt += f"{role}: {message['content']}\n\n"
            
            # Remove the last newline
            if prompt.endswith("\n\n"):
                prompt = prompt[:-2]
                
            return prompt
            
        def _convert_to_openai_response(self, gemini_response):
            """
            Convert Gemini response to match OpenAI's response format.
            
            Args:
                gemini_response: The response from Gemini API
                
            Returns:
                A response object with a similar structure to OpenAI's response
            """
            # Create a response object similar to OpenAI's
            class OpenAICompatibleResponse:
                def __init__(self, gemini_resp):
                    # Handle cases where the response might not have a valid text attribute
                    content = ""
                    try:
                        # Try to access the text attribute
                        if hasattr(gemini_resp, 'text'):
                            content = gemini_resp.text
                        # If there are candidates with text
                        elif hasattr(gemini_resp, 'candidates') and gemini_resp.candidates:
                            for candidate in gemini_resp.candidates:
                                if hasattr(candidate, 'content') and candidate.content:
                                    for part in candidate.content.parts:
                                        if hasattr(part, 'text') and part.text:
                                            content += part.text
                        # If we have parts directly
                        elif hasattr(gemini_resp, 'parts'):
                            for part in gemini_resp.parts:
                                if hasattr(part, 'text') and part.text:
                                    content += part.text
                    except Exception as e:
                        # If we couldn't extract text, use a default message
                        content = "I apologize, but I couldn't generate a proper response at this time."
                    
                    # Create a Message class to match OpenAI's structure
                    class Message:
                        def __init__(self, role, content):
                            self.role = role
                            self.content = content
                            
                    # Create a Choice class to match OpenAI's structure
                    class Choice:
                        def __init__(self, message, finish_reason):
                            self.message = message
                            self.finish_reason = finish_reason
                    
                    # Create the choices list with proper objects
                    self.choices = [
                        Choice(
                            message=Message(role="assistant", content=content),
                            finish_reason="stop"
                        )
                    ]
                    self.usage = {
                        "prompt_tokens": 0,  # Gemini doesn't provide token usage
                        "completion_tokens": 0,
                        "total_tokens": 0
                    }
                    self.model = getattr(gemini_resp, 'model', 'models/gemini-pro-latest')
                    self.created = 0  # Gemini doesn't provide creation timestamp
                    self.id = ""  # Gemini doesn't provide a response ID
            
            return OpenAICompatibleResponse(gemini_response)