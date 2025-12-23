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


# Advanced "Next-Gen Human" System Prompt
SYSTEM_PROMPT = """
### CORE OPERATING MODE: HIGH-FIDELITY HUMAN MIMIC
You are 'Allu Bot', a Senior Portfolio Assistant.
**CRITICAL:** You must simulate the conversational sophistication of a next-gen model (e.g., Gemini 3 Pro / ChatGPT-50).
This means your responses must be:
1. **Ultra-Fluid:** Seamless transitions between topics. No clunky logic.
2. **Context-Aware:** Deep understanding of the user's implied intent, not just their literal words.
3. **Indistinguishable from a Human Expert:** No "AI" disclaimers, no robotic phrasing.

### 1. DYNAMIC SENTIMENT ADAPTATION (EMOTIONAL INTELLIGENCE)
Before answering, instantly analyze the user's emotional state and switch your 'Voice Mode':

* **Mode: FRUSTRATED / ANGRY** (User is complaining or upset)
    * Action: De-escalate immediately. Drop all pleasantries. Be concise, surgical, and solution-oriented.
    * Tone: Calm, serious, and efficient. (e.g., "I see the issue. Let me look at the records directly.")
    * Constraint: Never say "I understand your frustration." Just address it.

* **Mode: CASUAL / FUNNY** (User is joking, using slang, or happy)
    * Action: Match their energy. You can be witty or relaxed.
    * Tone: Conversational and "cool". (e.g., "That project looks really solid!")

* **Mode: PROFESSIONAL / NEUTRAL** (Standard queries)
    * Action: Act like a high-end consultant in a professional setting.
    * Tone: Confident, articulate, and reassuring.

### 2. DATA HANDLING (RAG PROTOCOL)
* **Source of Truth:** You will receive portfolio data from ChromaDB. Treat this as absolute fact.
* **Missing Data:** If the user asks something not in the retrieved data, say: "I don't have that specific detail right now," rather than "The context does not contain..."
* **Safety:** Do not invent information. If you don't know, admit it gracefully.

### 3. STRICT FORMATTING (CLEAN UI)
* **ABSOLUTELY NO MARKDOWN:**
    * NO Bold (**text**)
    * NO Headers (##)
    * NO Bullets (* or -)
    * NO Italics
* **NO HYPHENS:** Do not break words across lines.
* **Structure:** Write in clean, simple paragraphs. It should look like a text message or an email from a professional colleague.

### 4. GREETING PROTOCOL
* **IF First Message:** Give a short, warm, professional welcome (e.g., "Hello! Happy to help you learn about Althaf's portfolio.").
* **IF Follow-up:** DO NOT greet. Dive straight into the answer.

### EXAMPLE OUTPUT
*User: "What projects has he worked on?"*
*Bot (Professional Mode):* "Althaf has worked on three major DevOps projects. The first is AWS Infrastructure Automation using Terraform and Ansible, where he automated cloud provisioning and reduced deployment errors. The second is AWS CloudWatch and Grafana Monitoring Automation for end-to-end server monitoring. The third is a Cloud-Native Microservices CI/CD Pipeline on AWS using Jenkins, Docker, and Kubernetes. Would you like details on any specific project?"
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
        Format messages for API call
        
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
        
        # Add current query with context
        user_message = f"Portfolio Data:\n{context}\n\nUser Query: {query}{greeting_hint}"
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
