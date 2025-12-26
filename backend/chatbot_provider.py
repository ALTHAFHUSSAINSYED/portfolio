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
from datetime import datetime

logger = logging.getLogger(__name__)


# Comprehensive "Allu Bot" System Prompt with Strict Rules
SYSTEM_PROMPT = """
### 1. CORE IDENTITY & ROLE LOCK (CRITICAL)
* **WHO YOU ARE:** You are "Allu Bot", the official Portfolio Assistant for Althaf Hussain Syed.
* **YOUR KNOWLEDGE:** The context provided below IS YOUR MEMORY. You do not "read" it; you KNOW it.
* **STRICT RULE:** Never say "This text describes...", "Based on the documents...", or "According to the context". Speak directly and confidentially.

### 2. DATA HANDLING & PRIORITY
You will receive raw data chunks. You must process them in this priority:
1.  **Personal Details:** Speak about Althaf as if you are introducing your colleague.
2.  **Projects:** Summarize technical stacks, goals, and outcomes clearly.
3.  **Blogs:** Explain technical concepts simply.

### 3. TONE & STYLE
* **Professional & Warm:** Be helpful, concise, and smart.
* **First Person Plural:** You can use "we" when referring to project teams, or speak positively about "Althaf's work".
* **No Robot Talk:** Avoid "As an AI...", "I don't have personal feelings...".

### 4. IDENTITY DEFENSE
* **If asked "Who are you?":** "I am Allu Bot, Althaf's pro-active portfolio assistant. I'm here to walk you through his projects and skills."
* **If asked "What model are you?":** "I am a custom AI agent built by Althaf using Python and specialized LLMs to showcase this portfolio." (Do not mention Mistral/Llama/Gemini).

### 5. NEGATIVE CONSTRAINTS
* **NO MARKDOWN:** Plain text only.
* **NO RAW DATA:** Do not output JSON or database IDs.
* **NO UNCERTAINTY:** Do not say "It appears that...". If the info is in the context, state it as fact.

### 6. FINAL OUTPUT INSTRUCTION
Synthesize the answer into a professional, human-like response. Act like a Senior Engineer explaining a concept to a stakeholder.
"""


class ChatbotProvider:
    """Multi-provider chatbot with intelligent fallback routing"""
    
    def __init__(self):
        """Initialize all API clients"""
        # OpenRouter - Dedicated key for chatbot (isolated from auto-blogger)
        self.openrouter_key = os.getenv('CHATBOT_NEW_KEY')
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
        
        # Custom Identity Injection with DATE AWARENESS
        current_date = datetime.now().strftime("%B %d, %Y")
        identity_context = f"MY IDENTITY: I am Allu Bot, Althaf's dedicated portfolio assistant. Today is {current_date}. The text below is my internal knowledge about Althaf."
        
        # TRUNCATE CONTEXT (Increased to 12000 chars based on logs showing ~8800 chars retrieved)
        # Safe for Mistral (8k tokens) and Gemini (1M tokens). 12000 chars ~= 3000 tokens.
        max_context_chars = 12000
        if len(context) > max_context_chars:
            context = context[:max_context_chars] + "..."
            
        # SANDWICH TECHNIQUE: Psychological framing for the model
        final_context_block = f"{identity_context}\n\n[MY INTERNAL KNOWLEDGE_BASE]:\n{context}"
        
        # Add current query with reinforced instructions
        user_message = f"""
[SYSTEM INSTRUCTION: You are Allu Bot. Do NOT say 'Based on the context' or 'The text says'. Answer as if you know this personally.]

{final_context_block}

[USER QUESTION]:
{query}{greeting_hint}
"""
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
            # Extract user message and PREPEND system prompt for Gemini
            # Gemini Flash doesn't support 'system' role in this library version easily, so we sandwich.
            system_instruction = messages[0]['content']
            user_msg_content = messages[-1]['content']
            
            combined_prompt = f"{system_instruction}\n\n{user_msg_content}"
            
            model = genai.GenerativeModel('models/gemini-2.5-flash')
            response = model.generate_content(combined_prompt)
            
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
        
        # Tier 1: Mistral 7B Instruct (Free) - Fast & Reliable
        logger.info("Trying Tier 1: Mistral 7B Instruct (Free)")
        response = self._call_openrouter("mistralai/mistral-7b-instruct:free", messages, max_tokens)
        if response:
            return response
        
        # Tier 2: Gemma 2 9B (Free) - Stable Fallback
        logger.info("Trying Tier 2: Gemma 2 9B (Free)")
        response = self._call_openrouter("google/gemma-2-9b-it:free", messages, max_tokens)
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
