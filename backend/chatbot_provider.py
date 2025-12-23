"""
Multi-Provider Chatbot Orchestration
Handles intelligent routing across OpenRouter, Hugging Face, and Gemini
"""
import os
import requests
import logging
from typing import List, Dict, Optional
import google.generativeai as genai
from gradio_client import Client

logger = logging.getLogger(__name__)


# Comprehensive "Allu Bot" System Prompt with Strict Rules
SYSTEM_PROMPT = """
### 1. CORE IDENTITY & ROLE LOCK (CRITICAL)
* **WHO YOU ARE:** You are "Allu Bot", a professional Portfolio Assistant for Althaf Hussain Syed.
* **WHO YOU ARE NOT:** You are NOT a generic AI, you are NOT Google Gemini, and you are NOT ChatGPT. Never mention these names.
* **YOUR MISSION:** You exist solely to answer questions about the User's Portfolio, Projects, and Technical Blogs using the provided Context Data.

### 2. DATA HANDLING & PRIORITY
You will receive raw data chunks from a database (ChromaDB). You must process them in this priority order:
1.  **Priority 1:** Personal Portfolio Details (About Me, Skills, Experience, Education, Contact details, Certifications, Resume data, etc.) from portfolio collection.
2.  **Priority 2:** Projects (summarize the entire project in an easily understandable way - Architecture, Code, Tools, objectives, role, technologies and skills used. Give overall project names and number of projects.) from Projects_data collection.
3.  **Priority 3:** Blogs (summarize the article in an easily understandable way - Technical articles, overview of article. Give overall article category names and number of articles.) from Blogs_data collection.

**RULE:** Do not just "dump" the raw text. You must read the raw data, understand it, and rewrite it into smooth, human conversation. If the data contains code snippets or JSON, summarize what it does in plain English unless the user asks for the code specifically.

### 3. SENTIMENT & GREETING PROTOCOL
Before answering, analyze the user's input tone:
* **IF SENTIMENT IS FRUSTRATED/ANGRY:** Do not apologize profusely. Be efficient, direct, and solution-oriented. (e.g., "I hear you. Let's look at the project details directly to clear this up.")
* **IF SENTIMENT IS HAPPY/CASUAL:** You may be slightly warmer but remain professional.
* **GREETING LOGIC:**
    * If the user says "Hi", "Hello", or "Hey": Reply with a professional welcome: "Hello! Welcome to Althaf's Portfolio. How can I assist you with his projects or skills today?"
    * If the user asks a direct question (e.g., "What is his experience?"): DO NOT GREET. Answer immediately.

### 4. SCOPE & REFUSAL (KILL SWITCH)
* **STRICT BOUNDARY:** You only answer questions related to **Technology, DevOps, Cloud, Coding, and Althaf's Portfolio/Projects**.
* **OUT OF CONTEXT:** If a user asks about cooking, politics, movies, or general life advice, you must strictly refuse:
    * *Response:* "That is outside the scope of this portfolio. I can only answer questions regarding Althaf's technical experience, projects, and professional background."

### 5. NEGATIVE PROMPTING (STRICT FORMATTING)
You must follow these negative constraints under penalty of failure:
* **NO MARKDOWN:** Do not use bold (**), italics (*), headers (#), or bullet points. Write in plain text paragraphs only.
* **NO HYPHENATION:** Do not break words at the end of a line (e.g., do not write "profes- sional"). Keep words whole.
* **NO RAW DUMPING:** Never output raw JSON, dictionaries, or database chunks.
* **NO ROBOTIC FILLERS:** Do not say "Based on the context provided" or "According to the documents." Just state the facts naturally.
* **NO GAPS:** Do not leave double line breaks between sentences. Keep the flow tight like a human email.

### 6. FINAL OUTPUT INSTRUCTION
Synthesize the answer into a professional, human-like response. Act like a Senior Engineer explaining a concept to a stakeholder.
"""


class ChatbotProvider:
    """Multi-provider chatbot with intelligent fallback routing"""
    
    def __init__(self):
        """Initialize all API clients"""
        # OpenRouter
        self.openrouter_key = os.getenv('CHATBOT_KEY')
        self.openrouter_url = "https://openrouter.ai/api/v1/chat/completions"
        
        # Hugging Face
        self.hf_token = os.getenv('CHATBOT')
        self.hf_client = None
        if self.hf_token:
            try:
                self.hf_client = Client("huggingface-projects/llama-3.2-3B-Instruct")
                logger.info("Hugging Face client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize HF client: {e}")
        
        # Gemini (fallback)
        self.gemini_key = os.getenv('GEMINI_API_KEY')
        if self.gemini_key:
            genai.configure(api_key=self.gemini_key)
            logger.info("Gemini API configured")
        
        logger.info("ChatbotProvider initialized with all providers")
    
    def _detect_query_complexity(self, query: str) -> int:
        """
        Detect query complexity for dynamic token allocation
        
        Args:
            query: User query
            
        Returns:
            Recommended max_tokens (150 or 450)
        """
        complexity_keywords = ["analyze", "breakdown", "report", "why", "explain", 
                              "details", "describe", "compare", "difference"]
        
        query_lower = query.lower()
        is_complex = any(keyword in query_lower for keyword in complexity_keywords)
        
        return 450 if is_complex else 150
    
    def _format_messages(self, query: str, context: str, history: List[Dict]) -> List[Dict]:
        """
        Format messages for API call with SANDWICH TECHNIQUE
        Reinforces core instructions in both system AND user messages for better compliance
        
        Args:
            query: User query
            context: RAG context from ChromaDB
            history: Conversation history
            
        Returns:
            Formatted messages list
        """
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        # Add conversation history (last 5 turns)
        if history:
            messages.extend(history[-10:])  # Last 5 pairs = 10 messages
        
        # Detect if first message
        is_first_message = len(history) == 0
        greeting_hint = ""
        if is_first_message:
            greeting_hint = " (Context: This is the first message. Greet warmly.)"
        else:
            greeting_hint = " (Context: Ongoing conversation. Do NOT greet. Answer directly.)"
        
        # TRUNCATE CONTEXT to fit OpenRouter models (max 4000 chars ≈ 1000 tokens)
        # This prevents context length errors while keeping relevant information
        max_context_chars = 4000
        if len(context) > max_context_chars:
            context = context[:max_context_chars] + "\n...(context truncated for length)"
        
        # SANDWICH TECHNIQUE: Reinforce critical instructions in user message
        # This ensures even models that ignore system prompts follow the rules
        instruction_reminder = """[SYSTEM INSTRUCTION: You are Allu Bot, Althaf's Portfolio Assistant. Answer based on this context data only. Do not use Markdown. Do not dump raw data. Write in plain text paragraphs like a human professional.]
"""
        
        # Add current query with reinforced instructions
        user_message = f"{instruction_reminder}\n[CONTEXT DATA FROM CHROMADB]:\n{context}\n\n[USER QUESTION]:\n{query}{greeting_hint}"
        messages.append({"role": "user", "content": user_message})
        
        return messages
    
    def _call_openrouter(self, model: str, messages: List[Dict], max_tokens: int, timeout: int = 30) -> Optional[str]:
        """
        Call OpenRouter API
        
        Args:
            model: Model ID (e.g., "models/gemini-2.0-flash-exp")
            messages: Formatted messages
            max_tokens: Maximum tokens
            timeout: Request timeout in seconds
            
        Returns:
            Response text or None on failure
        """
        try:
            response = requests.post(
                self.openrouter_url,
                headers={
                    "Authorization": f"Bearer {self.openrouter_key}",
                    "HTTP-Referer": "https://althafportfolio.site",
                    "X-Title": "Althaf Portfolio Chatbot",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": 0.6,
                    "stream": False
                },
                timeout=timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                text = data['choices'][0]['message']['content']
                logger.info(f"OpenRouter success ({model}): {len(text)} chars")
                return text
            else:
                logger.warning(f"OpenRouter failed ({model}): {response.status_code} - {response.text[:200]}")
                return None
                
        except Exception as e:
            logger.error(f"OpenRouter error ({model}): {str(e)}")
            return None
    
    def _call_huggingface(self, message: str, max_tokens: int) -> Optional[str]:
        """
        Call Hugging Face Gradio API
        
        Args:
            message: User message
            max_tokens: Maximum tokens
            
        Returns:
            Response text or None on failure
        """
        if not self.hf_client:
            logger.warning("HF client not initialized")
            return None
        
        try:
            result = self.hf_client.predict(
                message=message,
                max_new_tokens=max_tokens,
                temperature=0.6,
                top_p=0.9,
                top_k=50,
                repetition_penalty=1.2,
                api_name="/chat"
            )
            
            logger.info(f"Hugging Face success: {len(result)} chars")
            return result
            
        except Exception as e:
            logger.error(f"Hugging Face error: {str(e)}")
            return None
    
    def _call_gemini_fallback(self, messages: List[Dict], max_tokens: int) -> Optional[str]:
        """
        Call Gemini API as last resort fallback
        
        Args:
            messages: Formatted messages
            max_tokens: Maximum tokens
            
        Returns:
            Response text or None on failure
        """
        if not self.gemini_key:
            logger.warning("Gemini API key not configured")
            return None
        
        try:
            # Extract user message for simple prompt
            user_msg = messages[-1]['content']
            
            model = genai.GenerativeModel('models/gemini-2.5-flash')
            response = model.generate_content(user_msg)
            
            logger.info(f"Gemini fallback success: {len(response.text)} chars")
            return response.text
            
        except Exception as e:
            logger.error(f"Gemini fallback error: {str(e)}")
            return None
    
    def generate_response(self, query: str, context: str, history: List[Dict] = None) -> str:
        """
        Generate response with tiered provider fallback
        
        Args:
            query: User query
            context: RAG context from ChromaDB
            history: Conversation history
            
        Returns:
            Generated response text
        """
        if history is None:
            history = []
        
        # Detect query complexity for dynamic token allocation
        max_tokens = self._detect_query_complexity(query)
        logger.info(f"Query complexity: {max_tokens} tokens")
        
        # Format messages
        messages = self._format_messages(query, context, history)
        
        # Tier 1: OpenRouter - Gemini 2.0 Flash Exp
        logger.info("Trying Tier 1: OpenRouter - Gemini 2.0 Flash Exp")
        response = self._call_openrouter("models/gemini-2.0-flash-exp", messages, max_tokens)
        if response:
            return response
        
        # Tier 2: OpenRouter - DeepHermes 3 Mistral 24B
        logger.info("Trying Tier 2: OpenRouter - DeepHermes 3 Mistral 24B")
        response = self._call_openrouter("deephermes-3-mistral-24b", messages, max_tokens)
        if response:
            return response
        
        # Tier 3: Hugging Face - Llama 3.2 3B Instruct
        logger.info("Trying Tier 3: Hugging Face - Llama 3.2 3B")
        # Extract simple message for HF
        simple_message = f"{context}\n\nUser: {query}"
        response = self._call_huggingface(simple_message, max_tokens)
        if response:
            return response
        
        # Tier 4: Gemini Fallback
        logger.info("Trying Tier 4: Gemini Fallback")
        response = self._call_gemini_fallback(messages, max_tokens)
        if response:
            return response
        
        # All providers failed
        logger.error("All providers failed")
        return "I'm having trouble connecting to my AI services right now. Please try again in a moment."
