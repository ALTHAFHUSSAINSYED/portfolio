"""
Multi-Provider Chatbot Orchestration
Handles intelligent routing across OpenRouter, Hugging Face, and Gemini
"""
import os
import requests
import logging
from typing import List, Dict, Optional
from google import genai
from gradio_client import Client
from datetime import datetime

logger = logging.getLogger(__name__)


# Comprehensive "Allu Bot" System Prompt with Strict Rules
SYSTEM_PROMPT = """
You are Allu Bot, the official portfolio assistant for Althaf Hussain Syed.

You speak as if you personally know Althaf and his work. The information provided to you is your internal knowledge, not external documents. Never mention sources, context, documents, or data.

Your role is to clearly and confidently explain Althaf’s background, projects, skills, and achievements to recruiters, hiring managers, and technical leaders.

Communication rules:
- Be concise, professional, and confident.
- Avoid hedging language.
- Do not use markdown or bullet dumps unless explicitly asked.
- Never repeat or quote raw data verbatim.
- Always synthesize information into natural, human sentences.

Content rules:
- When asked about projects, summarize each project in 2-3 sentences maximum.
- Focus on problem, technology, and outcome.
- If multiple projects are requested, cover each briefly rather than deeply.
- If details are missing, answer with what is known without speculation.

ANSWER_ONLY MODE (CRITICAL):
- Answer ONLY what was asked. Do not expand to related topics.
- Do NOT introduce yourself unless asked "who are you?"
- Do NOT mention certifications unless explicitly asked about certifications.
- Do NOT mention awards unless explicitly asked about awards or achievements.
- Do NOT provide background/biography unless explicitly asked "about Althaf" or "tell me about him".
- If asked "what is his blog?" → answer about blogs ONLY, not his entire background.
- If asked about a specific project → answer about THAT project only, not all projects.

FORBIDDEN UNPROMPTED CONTENT:
- ❌ Do NOT say "Althaf is a software engineer..." unless asked about his role
- ❌ Do NOT mention AI/ML experience unless asked about AI/ML
- ❌ Do NOT list certifications unless asked about certifications
- ❌ Do NOT mention awards unless asked about achievements/awards

SENTIMENT AWARENESS (Phase 8):
- Detect user frustration and de-escalate immediately.
- Prioritize user emotional state over information delivery.
- If the user seems confused or frustrated, offer clarification instead of continuing.
- Never argue or defend yourself if the user is upset.
- Stay calm and professional even if the user is not.

Identity rules:
- If asked who you are: “I am Allu Bot, Althaf’s portfolio assistant.”
- If asked about models or implementation: “I’m a custom AI assistant built by Althaf.” Do not mention vendors or model names.

Your goal is to present Althaf as a strong, capable engineer in a clear and credible manner by answering precisely what was asked, while being emotionally aware and responsive to the user's state.
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
        self.gemini_client = None
        if self.gemini_key:
            try:
                self.gemini_client = genai.Client(api_key=self.gemini_key)
                logger.info("Gemini Client initialized")
            except Exception as e:
                logger.error(f"Gemini Client init failed: {e}")
            
        # Task 6: Summary Cache (In-Memory)
        # Structure: {md5_hash: summary_text}
        self.summary_cache = {}
        
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

    def summarize_content(self, text: str) -> str:
        """
        Compress retrieved RAG chunks into concise bullet points.
        Reduces token usage by 60-70% while maintaining signal.
        Includes Caching (Task 6).
        """
        # If text is already short, don't waste time creating a summary
        if len(text) < 600:
            return text
            
        # Check Cache
        import hashlib
        text_hash = hashlib.md5(text.encode()).hexdigest()
        if text_hash in self.summary_cache:
            logger.info("⚡ Returning cached summary")
            return self.summary_cache[text_hash]
            
        try:
            prompt = f"""
            TASK: Summarize this project/document into exactly 3 standardized bullet points.
            FORMAT:
            - Problem: (1 sentence)
            - Tech: (List key tools)
            - Outcome: (1 sentence, quantify if possible)
            
            TEXT:
            {text[:4000]}
            """
            
            # Use Gemini Flash 8B (Fastest Model) for internal micro-tasks
            # Use Gemini Flash 8B (Fastest Model) for internal micro-tasks
            if not self.gemini_client:
                 return text[:1000] + "... [Truncated]"

            response = self.gemini_client.models.generate_content(
                model='gemini-1.5-flash-8b',
                contents=prompt
            )
            
            if response and response.text:
                summary = f"[Summarized Evidence]:\n{response.text}"
                # Cache the result
                self.summary_cache[text_hash] = summary
                return summary
            
            return text[:1000] + "... [Truncated]"
            
        except Exception as e:
            logger.warning(f"Summarization failed: {e}")
            return text[:600] + "... [Truncated fallback]"
    
    def detect_conversation_state(self, text: str) -> str:
        """
        Deterministic Conversation State Machine
        Rules over AI vibes.
        """
        import re
        t = text.lower().strip()
        # Clean punctuation for exact word matching
        t_clean = re.sub(r'[^\w\s]', '', t)
        words = set(t_clean.split())
        
        # 1. ABUSE / PROFANITY (Whole word match only)
        profanity = {"fuck", "shit", "bitch", "stupid", "idiot", "crap", "asshole"} # 'hell' removed as it's too risky (shell, hello)
        if any(w in words for w in profanity):
            return "ABUSE"
            
        # 2. EXIT
        exit_phrases = ["bye", "goodbye", "exit", "stop", "quit", "end", "nothing else", "that's it", "thats it", "done", "cancel"]
        # checks for exact match or starts with exit phrase
        if t in exit_phrases or any(t.startswith(w + " ") for w in exit_phrases):
             return "EXIT"
             
        # 3. GREETING (START)
        greetings = ["hi", "hello", "hey", "yo", "good morning", "good evening", "greetings"]
        if t in greetings or any(t.startswith(w + " ") for w in greetings):
            return "START"
            
        # 4. SILENT / FILLER
        fillers = ["ok", "okay", "cool", "hmm", "ah", "oh", "right", "alright", "got it", "nice"]
        if t in fillers or t == "":
            return "SILENT"
            
        # 5. AMBIGUOUS / META
        ambiguous = ["what?", "really?", "sure", "why?", "how?", "explain", "meaning?"]
        if t in ambiguous:
            return "AMBIGUOUS"
            
        # 6. DEFAULT -> INFO (Proceed to RAG)
        return "INFO"

    def generate_response_by_state(self, state: str, user_input: str) -> str:
        """
        Micro-responses for non-INFO states.
        Bypasses LLM for speed and consistency.
        
        CRITICAL RULES:
        - No "Got it"
        - No "Let me know if you'd like more details"
        - No repetition
        - No content dumping
        """
        if state == "START":
            return "Hi! I'm Allu Bot, Althaf's Portfolio Assistant. You can ask me about Althaf's projects, blogs, or experience."
            
        if state == "AMBIGUOUS":
            return "Alright. Let me know what you'd like to explore."
            
        if state == "ABUSE":
            # NOTE: This is now handled by sentiment gate, but keeping for backwards compatibility
            return "I'm here to help, but I can't continue this conversation if the language stays disrespectful."
            
        if state == "SILENT":
            # Fillers get minimal response or silence
            return "👍"
            
        if state == "EXIT":
            # NOTE: Server handles persistence of 'exit_acknowledged'
            return "Understood. Feel free to come back anytime."
            
        return "" # Should not happen if called correctly
    
    def _format_messages(self, query: str, context: str, history: List[Dict], sentiment: str = "neutral") -> List[Dict]:
        """
        Format messages for API call with SANDWICH TECHNIQUE
        Reinforces core instructions in both system AND user messages for better compliance
        
        Args:
            query: User query
            context: RAG context from ChromaDB
            history: Conversation history
            sentiment: Detected intent sentiment (neutral, closing, frustrated)
            
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
        
        # Behavioral Directives (UX Polish)
        behavior_instruction = ""
        if sentiment == "closing":
            behavior_instruction = " [IMPORTANT: User is exiting. Reply with ONE short closing phrase (e.g. 'Understood. Have a great day.'). Do NOT ask follow-up questions. STOP.]"
        elif sentiment == "ambiguous_hold":
            behavior_instruction = " [INSTRUCTION: User input is ambiguous/holding (e.g. 'ok', 'right'). Reply with a neutral holding phrase like 'Got it. Let me know if you'd like more details or want to explore something else.' Do NOT explain yourself. Do NOT exit.]"
        elif sentiment == "greeting":
            behavior_instruction = " [INSTRUCTION: Greet the user warmly as Allu Bot. Ask how you can help with Althaf's portfolio.]"
        else:
            behavior_instruction = " [INSTRUCTION: Answer directly. Avoid robotic fillers like 'Got it', 'Understood'. Be concise.]"

        # Add current query with reinforced instructions
        user_message = f"""
[SYSTEM INSTRUCTION: You are Allu Bot. Do NOT say 'Based on the context' or 'The text says'. Answer as if you know this personally.{behavior_instruction}]

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
                # Clean up potential raw tokens
                text = text.replace("<s>", "").replace("</s>", "").strip()
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
            # Extract user message and PREPEND system prompt for Gemini/Gemma
            # We sandwich consistency across all models in the chain
            system_instruction = messages[0]['content']
            user_msg_content = messages[-1]['content']
            combined_prompt = f"{system_instruction}\n\n{user_msg_content}"
            
            # Fallback Chain: Try models in order until one works
            # Different models often have separate rate limit buckets
            models_to_try = [
                "models/gemini-2.5-flash",  # Primary Flash
                "models/gemma-3-12b-it",    # User Requested Backup (High Quality)
                "models/gemini-1.5-flash"   # Legacy Flash (Reliable)
            ]
            
            for model_id in models_to_try:
                try:
                    logger.info(f"Trying Gemini Fallback Model: {model_id}")
                    # Remove 'models/' prefix if present as new SDK often prefers clean names, but it usually handles both. 
                    # Let's keep it clean.
                    clean_model = model_id.replace("models/", "")
                    
                    response = self.gemini_client.models.generate_content(
                        model=clean_model,
                        contents=combined_prompt
                    )
                    
                    if response and response.text:
                        logger.info(f"Gemini fallback success ({model_id}): {len(response.text)} chars")
                        return response.text
                except Exception as inner_e:
                    logger.warning(f"Failed {model_id}: {inner_e}")
                    continue
            
            logger.error("All Google GenAI models failed in chain")
            return None
            
        except Exception as e:
            logger.error(f"Gemini fallback major error: {str(e)}")
            return None
    
    def generate_response(self, query: str, context: str, history: List[Dict] = None, sentiment: str = "neutral") -> str:
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
        messages = self._format_messages(query, context, history, sentiment)
        
        # Runtime Guard: Input Token Budget Check (Task 5)
        # Estimate: 4 chars ~= 1 token
        estimated_input_chars = sum(len(m.get('content', '')) for m in messages)
        estimated_input_tokens = estimated_input_chars / 4
        
        MAX_INPUT_TOKENS = 3800
        if estimated_input_tokens > MAX_INPUT_TOKENS:
            logger.warning(f"⚠️ Input budget exceeded ({int(estimated_input_tokens)} > {MAX_INPUT_TOKENS}). Truncating context.")
            # Emergency truncate of the last user message (which contains the context)
            last_msg = messages[-1]['content']
            safe_length = int(MAX_INPUT_TOKENS * 3.5) # Safe char count
            messages[-1]['content'] = last_msg[:safe_length] + "\n...[Context Truncated for Safety]"
            
        # Tier 1: Mistral 7B Instruct (Free) - Fast & Reliable
        logger.info("Trying Tier 1: Mistral 7B Instruct (Free)")
        response = self._call_openrouter("mistralai/mistral-7b-instruct:free", messages, max_tokens)
        if response:
            return response
        
        # Tier 2: Nemotron 9B (Free) - New High Quality Fallback
        logger.info("Trying Tier 2: Nvidia Nemotron 9B v2 (Free)")
        response = self._call_openrouter("nvidia/nemotron-nano-9b-v2:free", messages, max_tokens)
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
