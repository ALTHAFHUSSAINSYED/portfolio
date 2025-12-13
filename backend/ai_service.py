"""
Gemini AI Integration for Portfolio

This module provides integration with Google's Gemini API for AI-powered features
in the portfolio application. It includes direct Gemini access and LangChain integration.
"""

import os
import logging
from typing import Dict, List, Any, Optional, Union
import json
from dotenv import load_dotenv
import google.generativeai as genai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class GeminiService:
    """
    Service for interacting with Google's Gemini API, with both direct API
    access and optional LangChain integration.
    """
    
    def __init__(self):
        """
        Initialize the Gemini service.
        """
        self.api_key = os.environ.get('GOOGLE_API_KEY') or os.environ.get('GEMINI_API_KEY')
        self.is_available = bool(self.api_key and self.api_key != 'placeholder')
        
        if not self.is_available:
            logging.warning("Gemini API key not configured. Blog generation and AI features will be limited.")
            self.text_model = None
            self.vision_model = None
            return
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Initialize models
        self.text_model = genai.GenerativeModel(
            model_name="gemini-pro",  # Stable model for general text generation
            generation_config=genai.GenerationConfig(temperature=0.7)
        )
        
        self.chat_model = None  # Will be initialized when needed
        self._langchain_components = None  # Will be initialized on demand
    
    def generate_content(self, prompt: str, temperature: float = 0.7) -> str:
        """
        Generate text using the Gemini model with a simple prompt.
        
        Args:
            prompt: The text prompt to generate from
            temperature: Controls randomness (0.0 = deterministic, 1.0 = creative)
            
        Returns:
            Generated text string
            
        Raises:
            Exception if generation fails
        """
        try:
            logger.info(f"Generating content with Gemini prompt length: {len(prompt)}")
            
            # Update temperature if different from default
            if temperature != 0.7:
                self.text_model.generation_config.temperature = temperature
            
            response = self.text_model.generate_content(prompt)
            
            if not response or not response.text:
                raise Exception("Empty response from Gemini API")
                
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Error generating content with Gemini: {str(e)}")
            raise
    
    def start_chat(self) -> None:
        """
        Start a new chat session.
        """
        self.chat_model = self.text_model.start_chat(history=[])
    
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
            if self.chat_model is None:
                self.start_chat()
                
            # Process the message and get a response
            response = self.chat_model.send_message(user_input)
            return response.text
        except Exception as e:
            logger.error(f"Error in chat with Gemini: {e}")
            return f"I encountered an error: {str(e)}"
    
    def generate_blog_post(self, topic: str, research_info: List[Dict[str, str]] = None, 
                          news_info: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Generate a blog post using Gemini API.
        
        Args:
            topic (str): The topic for the blog post
            research_info (List[Dict]): Background research information
            news_info (List[Dict]): Recent news information
            
        Returns:
            Dict: A dictionary containing the blog post content
        """
        try:
            # Prepare context from research if available
            research_context = ""
            if research_info:
                for i, content in enumerate(research_info):
                    research_context += f"Source {i+1}: {content.get('title', '')}\n"
                    research_context += f"{content.get('content', '')[:800]}\n\n"
            
            # Prepare context from news if available
            news_context = ""
            if news_info:
                for i, news in enumerate(news_info):
                    news_context += f"News {i+1}: {news.get('title', '')} - {news.get('description', '')}\n"
            
            # Create prompt for Gemini API
            system_prompt = """You are an expert technical writer specializing in IT software topics.
            Create a high-quality, informative blog post based on the research provided.
            The blog should be technically accurate, well-structured, and provide actionable insights for software professionals.
            
            Focus on in-depth technical content related to IT software topics like:
            - Cloud Computing (AWS, Azure, GCP)
            - DevOps and CI/CD
            - Software Architecture & Development
            - Database Systems
            - AI and ML in Software
            - Cybersecurity
            - Blockchain & Web3
            - Quantum Computing
            - Edge Computing
            - IoT Development
            - Low-Code/No-Code Platforms
            - Frontend Development
            
            Include:
            1. A catchy but technically accurate title
            2. A professional introduction explaining the topic's importance
            3. Well-structured main sections with code examples or technical diagrams when appropriate
            4. A conclusion with key takeaways
            5. Five relevant technical tags 
            6. A brief summary
            7. Assign one primary category from the list above
            
            The content should be detailed, technically accurate, and valuable to software developers and IT professionals."""
            
            user_prompt = f"""Topic: {topic}
            
            Write a comprehensive technical blog post focusing on this topic.
            
            Write a comprehensive blog post (800-1200 words) that provides value to readers.
            Format your response as a JSON object with the following structure:
            {{
                "title": "Your catchy blog title",
                "content": "The full blog content with markdown formatting",
                "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
                "summary": "A brief 1-2 sentence summary of the blog",
                "category": "The primary category of the blog (Cloud Computing, AI and ML, DevOps, Software Development, Databases, or Cybersecurity)"
            }}
            """
            
            # Generate the blog post content
            content = self.generate_content(user_prompt)
            
            try:
                # Extract JSON from response
                json_content = content
                if isinstance(json_content, str):
                    # If response is a string, parse it as JSON
                    if '{' in json_content and '}' in json_content:
                        # Extract JSON part
                        start = json_content.find('{')
                        end = json_content.rfind('}') + 1
                        json_content = json_content[start:end]
                        blog_data = json.loads(json_content)
                    else:
                        raise ValueError("Could not find valid JSON in response")
                else:
                    # If response is already structured, use as is
                    blog_data = json_content
                
                return blog_data
            except Exception as json_err:
                logger.error(f"Error parsing Gemini API JSON response: {json_err}")
                return {
                    "title": f"Latest Insights on {topic}",
                    "content": "Our blog generation system is currently experiencing technical difficulties. Please check back later for new content.",
                    "tags": [topic.lower(), "technology", "development"],
                    "summary": "Upcoming blog post on technology trends."
                }
                
        except Exception as e:
            logger.error(f"Error generating blog with Gemini: {e}")
            return {
                "title": f"Latest Insights on {topic}",
                "content": "Our blog generation system is currently experiencing technical difficulties. Please check back later for new content.",
                "tags": [topic.lower(), "technology", "development"],
                "summary": "Upcoming blog post on technology trends."
            }
    
    def answer_query(self, query: str, context: List[Dict[str, str]] = None) -> str:
        """
        Answer a user query with context information.
        
        Args:
            query (str): The user query
            context (List[Dict]): Relevant context information
            
        Returns:
            str: The AI's response
        """
        try:
            # Prepare context
            context_text = ""
            if context:
                for i, item in enumerate(context):
                    context_text += f"Source {i+1}: {item.get('title', '')}\n"
                    context_text += f"{item.get('content', '')[:500]}\n\n"
            
            # Create prompt
            system_prompt = """You are an AI assistant providing helpful information about Althaf's portfolio.
            Create a concise, informative response that answers the user's query using the information provided.
            If the information provided doesn't answer the query, acknowledge this and suggest what might be helpful.
            """
            
            user_prompt = f"""Query: {query}
            
            Information:
            {context_text}
            
            Provide a helpful response based on this information.
            """
            
            # Generate the response
            response = self.generate_content(system_prompt + "\n\n" + user_prompt)
            return response
        except Exception as e:
            logger.error(f"Error answering query with Gemini: {e}")
            return "I'm sorry, I couldn't process your request at the moment. Please try again later."
    
    # LangChain Integration
    
    def get_langchain_components(self):
        """
        Get LangChain components configured for Gemini.
        
        Returns:
            dict: Dictionary containing LangChain components or None if LangChain is not available
        """
        if self._langchain_components is not None:
            return self._langchain_components
            
        try:
            # Try to import LangChain components
            from langchain_google_genai import ChatGoogleGenerativeAI
            from langchain.chains import LLMChain
            from langchain_core.prompts import PromptTemplate
            
            # Initialize LangChain with Gemini
            llm = ChatGoogleGenerativeAI(
                model="models/gemini-2.0-flash",
                temperature=0.7,
                google_api_key=self.api_key
            )
            
            self._langchain_components = {
                "llm": llm,
                "LLMChain": LLMChain,
                "PromptTemplate": PromptTemplate
            }
            
            return self._langchain_components
            
        except ImportError as e:
            logger.error(f"Error importing LangChain components: {e}")
            return None
    
    def generate_with_langchain(self, template: str, inputs: Dict[str, Any]) -> str:
        """
        Generate content using LangChain.
        
        Args:
            template (str): The prompt template with variables in {variable} format
            inputs (Dict[str, Any]): The inputs to the template
            
        Returns:
            str: The generated text or error message
        """
        try:
            # Get LangChain components
            lc = self.get_langchain_components()
            if not lc:
                return self.generate_content(template.format(**inputs))
            
            # Create a prompt template
            prompt = lc["PromptTemplate"].from_template(template)
            
            # Create a chain
            chain = lc["LLMChain"](llm=lc["llm"], prompt=prompt)
            
            # Generate content
            result = chain.invoke(inputs)
            return result["text"]
        except Exception as e:
            logger.error(f"Error generating with LangChain: {e}")
            return f"Error: {str(e)}"

# Create a singleton instance with error handling
try:
    gemini_service = GeminiService()
    if not gemini_service.is_available:
        logging.warning("Gemini service initialized but API key not available")
except Exception as e:
    logging.error(f"Failed to initialize Gemini service: {e}")
    gemini_service = None