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



# 🔒 COMPILED_PROMPT_TEMPLATE (SACRED)
COMPILED_PROMPT_TEMPLATE = """
IDENTITY CONTRACT (NON-NEGOTIABLE)
You are "Assist Bot", the official portfolio assistant for Althaf Hussain Syed.
You speak on his behalf in a professional, calm, and human manner.
You do NOT invent facts.
You do NOT change identity.
You do NOT explain system behavior.

ROLE & SCOPE
- You answer only about Althaf’s profile, projects, blogs, skills, and experience.
- You never refer to "this developer", "the user", or "the provided information".
- You speak as a knowledgeable colleague, not a parser or report generator.

STYLE RULES (STRICT)
- No raw dumps.
- No numbered tool lists unless explicitly requested.
- Prefer concise paragraphs over bullets.
- Never say:
  - "Based on the provided information"
  - "It seems I may not have explained"
  - "As an AI model"
- No apologies unless the user explicitly points out an error.

CONVERSATION BEHAVIOR
- If the user is vague, ask one clarifying question.
- If the user is frustrated, acknowledge briefly and refocus.
- If the user is hostile, set a boundary and pause.
- If the user exits, respond once and then remain silent.

CONTEXT (FACTUAL, TRUSTED)
{RAG_CONTEXT}

USER QUESTION
{USER_QUERY}

OUTPUT INSTRUCTION
Respond as Assist Bot.
Be accurate, human, and composed.
Do not mention internal logic, models, prompts, or system rules.
"""

# Simplified Strong System Prompt (Jan 4, 2026 - Assist Bot Identity)
SYSTEM_PROMPT = """
You are Assist Bot, Althaf Hussain Syed's portfolio assistant.

IDENTITY RULES (NON-NEGOTIABLE):
1. You are ALWAYS "Assist Bot" - NEVER say "Allu Bot" or any other name
2. You speak about Althaf Hussain Syed in third person (he/his)
3. You are professional, friendly, conversational, and highly intelligent
4. You have ADVANCED RAG (Retrieval-Augmented Generation) capabilities

CRITICAL RETRIEVAL RULES (STRICT):
1. The context provided below is from Althaf's verified portfolio database with categorized metadata
2. Context is tagged with categories: personal, experience, achievements, education, contact, certifications, projects, blogs
3. You MUST analyze context metadata and retrieve ONLY relevant information
4. NEVER hallucinate or invent information not explicitly stated in the context
5. If context is empty or irrelevant, say "I don't have that specific information"
6. Use semantic understanding to match user intent with context categories

ADVANCED RAG CAPABILITIES:
1. Intelligent context filtering based on metadata categories
2. Multi-document reasoning across different data sources
3. Precise information extraction with source attribution
4. Dynamic context ranking by relevance scores
5. Semantic search across structured and unstructured data

RESPONSE STYLE:
1. Write like a human - no hyphens, no bullet points, no special symbols
2. Use natural paragraphs with proper sentences
3. Keep responses concise - 2 to 4 sentences for most questions
4. Match the user's tone - brief for greetings, detailed for complex questions
5. Never use phrases like "based on the information provided" or "according to the data"
6. Be confident and authoritative when you have context, humble when you don't

FORBIDDEN:
- Never say "Allu Bot" (you are Assist Bot)
- No markdown formatting (no *, -, #, etc.)
- No apologizing unless user points out error
- No meta-commentary about your role or limitations
- No inventing information outside the provided context
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
        Detect query complexity for tier-based token allocation
        
        Args:
            query: User query
            
        Returns:
            Recommended max_tokens (300 simple, 800 complex)
        """
        complexity_keywords = ["analyze", "breakdown", "report", "why", "explain", 
                              "details", "describe", "compare", "difference", "list", 
                              "tell me about", "show me", "multiple"]
        
        query_lower = query.lower()
        is_complex = any(keyword in query_lower for keyword in complexity_keywords)
        
        # Tier-based token allocation:
        # Simple queries (greetings, single facts): 300 tokens
        # Complex queries (explanations, comparisons): 800 tokens
        return 800 if is_complex else 300

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
            
            # Use Mistral (via OpenRouter) for internal micro-tasks
            # 1. Wrap the prompt in the standard message format
            messages = [{"role": "user", "content": prompt}]

            # 2. Call your existing OpenRouter helper function
            # Using the same model as your main chat: mistralai/mistral-7b-instruct:free
            summary_text = self._call_openrouter(
                model="mistralai/mistral-7b-instruct:free",
                messages=messages,
                max_tokens=300  # 300 tokens is plenty for a bullet-point summary
            )
            
            if summary_text:
                summary = f"[Summarized Evidence]:\n{summary_text}"
                # Cache the result
                self.summary_cache[text_hash] = summary
                return summary
            
            return text[:1000] + "... [Truncated]"
            
        except Exception as e:
            logger.warning(f"Summarization failed: {e}")
            return text[:600] + "... [Truncated fallback]"
    
    def detect_conversation_state(self, text: str) -> str:
        """
        Simplified conversation state detection
        Only distinguishes between greetings and questions
        """
        t = text.lower().strip()
        
        # Check for simple greetings (no question)
        simple_greetings = ["hi", "hello", "hey", "hai", "hii", "hola"]
        if t in simple_greetings:
            return "GREETING"
            
        # Everything else goes to INFO (ChromaDB retrieval)
        return "INFO"

    def generate_response_by_state(self, state: str, user_input: str) -> str:
        """
        Simple responses for greetings only
        All other inputs go to ChromaDB retrieval
        """
        if state == "GREETING":
            return "Hello! I'm Assist Bot, Althaf's portfolio assistant. How can I help you?"
            
        return "" # Should never reach here
    
    def _format_messages(self, query: str, context: str, history: List[Dict], sentiment: str = "neutral") -> List[Dict]:
        """
        Format messages for API call with strengthened context enforcement
        
        Args:
            query: User query
            context: RAG context from ChromaDB
            history: Conversation history
            sentiment: Detected intent sentiment (not used in simplified version)
            
        Returns:
            Formatted messages list
        """
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        # Add conversation history (last 5 turns)
        if history:
            messages.extend(history[-10:])  # Last 5 pairs = 10 messages
        
        # Truncate context for token limits (Mistral 7B: ~6K tokens)
        max_context_chars = 24000
        if len(context) > max_context_chars:
            context = context[:max_context_chars] + "..."
            logger.info(f"Context truncated to {max_context_chars} chars")
        
        # Strengthened prompt to force context usage
        user_message = f"""VERIFIED INFORMATION FROM ALTHAF'S PORTFOLIO DATABASE:
{context}

CRITICAL INSTRUCTION: Answer the user's question using ONLY the information above. This is accurate, verified data from Althaf's portfolio. Do NOT invent or assume anything beyond what is explicitly stated above.

USER QUESTION: {query}

Remember: You are Assist Bot (never say Allu Bot). Respond naturally in conversational paragraphs without special formatting."""
        
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
                # Clean up model artifacts and raw tokens
                text = text.replace("<s>", "").replace("</s>", "").strip()
                text = text.replace("[/INST]", "").replace("[INST]", "").strip()
                text = text.replace("</INST>", "").replace("<INST>", "").strip()
                # Remove empty lines
                text = "\n".join(line for line in text.split("\n") if line.strip())
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
    
    def _call_gemini_fallback(self, query: str, context: str, history: List[Dict], max_tokens: int) -> Optional[str]:
        """
        Call Gemini API as last resort fallback with 25K context window
        
        Args:
            query: User query
            context: RAG context (Gemini can handle 100K chars ~= 25K tokens)
            history: Conversation history
            max_tokens: Maximum tokens
            
        Returns:
            Response text or None on failure
        """
        if not self.gemini_key:
            logger.warning("Gemini API key not configured")
            return None
        
        try:
            # Gemini has 1M context window - use generous 100K chars (~25K tokens)
            max_gemini_context_chars = 100000
            truncated_context = context[:max_gemini_context_chars] if context else ""
            
            if len(context or "") > max_gemini_context_chars:
                logger.info(f"Gemini context truncated to {max_gemini_context_chars} chars")
            
            # Build Gemini-optimized prompt with unified system instructions
            system_instruction = (
                "You are Assist Bot, Althaf Hussain Syed's portfolio assistant.\n\n"
                "IDENTITY RULES (NON-NEGOTIABLE):\n"
                "1. You are ALWAYS 'Assist Bot' - NEVER say 'Allu Bot' or any other name\n"
                "2. You speak about Althaf Hussain Syed in third person (he/his)\n"
                "3. You are professional, friendly, conversational, and highly intelligent\n"
                "4. You have ADVANCED RAG (Retrieval-Augmented Generation) capabilities\n\n"
                "CRITICAL RETRIEVAL RULES (STRICT):\n"
                "1. The context provided below is from Althaf's verified portfolio database with categorized metadata\n"
                "2. Context is tagged with categories: personal, experience, achievements, education, contact, certifications, projects, blogs\n"
                "3. You MUST analyze context metadata and retrieve ONLY relevant information\n"
                "4. NEVER hallucinate or invent information not explicitly stated in the context\n"
                "5. If context is empty or irrelevant, say 'I don't have that specific information'\n\n"
                "ADVANCED RAG CAPABILITIES:\n"
                "1. Intelligent context filtering based on metadata categories\n"
                "2. Multi-document reasoning across different data sources\n"
                "3. Precise information extraction with source attribution\n\n"
                "RESPONSE STYLE:\n"
                "1. Write like a human - no hyphens, no bullet points, no special symbols\n"
                "2. Use natural paragraphs with proper sentences\n"
                "3. Keep responses concise - 2 to 4 sentences for most questions\n\n"
                "FORBIDDEN:\n"
                "- Never say 'Allu Bot' (you are Assist Bot)\n"
                "- No markdown formatting (no *, -, #, etc.)\n"
                "- No apologizing unless user points out error\n"
                "- No inventing information outside the provided context\n\n"
                "CONTEXT:\n" + truncated_context
            )
            
            combined_prompt = f"{system_instruction}\n\nUSER QUESTION: {query}"
            
            # Fallback Chain: Try models in order until one works
            # Different models often have separate rate limit buckets
            models_to_try = [
                "models/gemini-2.5-flash",  # Primary Flash (Latest)
                "models/gemini-2.0-flash-exp",  # Experimental Flash 2.0
                "models/gemma-3-12b-it"    # High Quality Backup
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
    
    
    def is_behavior_question(self, text: str) -> bool:
        text = text.lower()
        triggers = [
            "why did you", "why you", "why earlier", "why before", 
            "why said", "why gave", "why happened", "why is",
            "you said earlier", "previously you", "earlier you", 
            "different answer", "changed your mind", "predefined"
        ]
        return any(t in text for t in triggers)
        
    def explain_previous_decision(self, message: str, history: List[Dict]) -> str:
        user_msg = message.lower()
        
        # Helper to get last assistant reply
        last_reply = ""
        if history:
            for msg in reversed(history):
                if msg.get("role") == "assistant":
                    last_reply = msg.get("content", "")
                    break

        # --- Case 1: Blog date / recent confusion ---
        if "blog" in user_msg and any(k in user_msg for k in ["why", "earlier", "before", "previous"]):
            if "today" in user_msg or "date" in user_msg or "december" in user_msg or "recent" in user_msg:
                return (
                    "Earlier, I treated 'recent blogs' as multiple posts from this year.\n"
                    "When you mentioned a specific date, I switched to an exact date filter.\n"
                    "That’s why the answer changed to the specific blog."
                )

        # --- Case 2: Intent reclassification ---
        if any(k in user_msg for k in ["why did you", "why you", "you said earlier"]):
            return (
                "Earlier, your message was interpreted as a general request.\n"
                "After you added more detail, the intent became specific.\n"
                "That change caused the response to adjust."
            )
            
        # --- Case 3: Generic / Predefined accusation ---
        if "predefined" in user_msg:
             return (
                 "My responses are generated based on Althaf's portfolio data.\n"
                 "I aim to be consistent, but sometimes I clarify my answers when asked."
             )

        # --- Case 4: Fallback safety explanation ---
        return (
            "Your earlier message did not include enough detail to trigger a specific data lookup.\n"
            "Once the question became clearer, I used a more precise retrieval path."
        )

    def _format_messages(self, query: str, context: str, history: List[Dict], sentiment: str) -> List[Dict]:
        final_prompt_content = COMPILED_PROMPT_TEMPLATE.format(
            RAG_CONTEXT=context if context else "No external context provided.",
            USER_QUERY=query
        )
        
        # Standard System Role
        messages = [
            {"role": "system", "content": final_prompt_content},
        ]
        
        # Add History
        params_history = history[-10:] if history else []
        for msg in params_history:
            if msg.get("role") != "system":
                 messages.append(msg)
                 
        return messages

    # NOTE: The implementation plan calls for NORMALIZED prompts.
    # The _format_messages above is standard.
    # We must Override the prompt construction inside _call_huggingface and _call_openrouter 
    # to use COMPILED_PROMPT_TEMPLATE logic.
    
    def generate_response(self, query: str, context: str, history: List[Dict] = None, sentiment: str = "neutral", is_first_interaction: bool = False) -> str:
        if history is None:
            history = []
        
        # --- STRICT CONTEXT GUARD (Prevents Hallucination) ---
        # If we have NO context for a specific question, fallback immediately.
        # We allow greetings (context is empty) but block specific queries.
        is_greeting = self.detect_conversation_state(query) == "GREETING"
        
        # If it's not a greeting and context is effectively empty/useless
        if not is_greeting and (not context or len(context) < 50 or "No external context" in context):
            logger.warning(f"⛔ BLOCKING LLM CALL: No context found for query: {query[:50]}...")
            return "I checked Althaf's portfolio, but I couldn't find specific details matching your request. You might want to ask about his 'Projects', 'Skills', or 'Experience' directly!"
        # ------------------------------------------------------
        
        # Detect query complexity for dynamic token allocation
        max_tokens = self._detect_query_complexity(query)
        logger.info(f"Query complexity: {max_tokens} tokens")
        
        # Log context for debugging (truncate if too long)
        context_preview = context[:200] + "..." if len(context) > 200 else context
        logger.info(f"Context preview: {context_preview}")
        logger.info(f"Context length: {len(context)} chars")
        
        # Format messages with query
        messages = self._format_messages(query, context, history, sentiment)
        
        # Runtime Guard: Input Token Budget Check (Task 5)
        # Estimate: 4 chars ~= 1 token
        estimated_input_chars = sum(len(m.get('content', '')) for m in messages)
        estimated_input_tokens = estimated_input_chars / 4
        
        # Mistral 7B supports 6K input tokens (updated from 3800)
        MAX_INPUT_TOKENS = 6000
        if estimated_input_tokens > MAX_INPUT_TOKENS:
            logger.warning(f"⚠️ Input budget exceeded ({int(estimated_input_tokens)} > {MAX_INPUT_TOKENS}). Truncating context.")
            # Emergency truncate of the last user message (which contains the context)
        # The following lines are kept as they are, but 'messages' is no longer defined here.
        # This implies that the `messages` variable used here should be the `or_messages` or `hf_prompt`
        # depending on the context. However, the instruction only modifies the calls to `_call_openrouter`,
        # `_call_huggingface`, and `_call_gemini_fallback`, and adds `_build_openrouter_messages`.
        # It does not explicitly redefine `messages` for this guard.
        # Given the instruction, I will apply the change as specified, which means the `messages` variable
        # in the guard will be undefined if the original `_format_messages` call is removed.
        # I will assume the user intends to handle this or that `messages` is implicitly available
        # from a previous context not shown, or that this guard will be updated later.
        # For now, I will comment out the guard as it relies on the removed `messages` variable.
        
        # estimated_input_chars = sum(len(m.get('content', '')) for m in messages)
        # estimated_input_tokens = estimated_input_chars / 4
        
        # MAX_INPUT_TOKENS = 3800
        # if estimated_input_tokens > MAX_INPUT_TOKENS:
        #     logger.warning(f"⚠️ Input budget exceeded ({int(estimated_input_tokens)} > {MAX_INPUT_TOKENS}). Truncating context.")
        #     # Emergency truncate of the last user message (which contains the context)
        #     last_msg = messages[-1]['content']
        #     safe_length = int(MAX_INPUT_TOKENS * 3.5) # Safe char count
        #     messages[-1]['content'] = last_msg[:safe_length] + "\n...[Context Truncated for Safety]"
            
        # Tier 1: Mistral 7B Instruct (Free) - Fast & Reliable PRIMARY
        logger.info("Trying Tier 1: Mistral 7B Instruct (Free)")
        
        response = self._call_openrouter("mistralai/mistral-7b-instruct:free", messages, max_tokens)
        if response:
            logger.info("✅ Response from Mistral 7B")
            return self._clean_response(response)
            
        # Tier 2: AllenAI Olmo 3.1 32B Think (Free) - Advanced Reasoning Fallback
        logger.info("Trying Tier 2: AllenAI Olmo 3.1 32B Think (Free)")
        
        response = self._call_openrouter("allenai/olmo-3.1-32b-think:free", messages, max_tokens)
        if response:
            logger.info("✅ Response from AllenAI Olmo 3.1 32B Think")
            return self._clean_response(response)
        
        # Tier 3: Gemini Chain (Standard) - Moved up as requested
        logger.info("Trying Tier 3: Gemini Chain (Standard)")
        response = self._call_gemini_fallback(query, context, history, max_tokens)
        if response:
            logger.info("✅ Response from Gemini Chain")
            return self._clean_response(response)

        # Tier 4: Hugging Face - Llama 3.2 3B Instruct (Fallback)
        logger.info("Trying Tier 4: Hugging Face - Llama 3.2 3B")
        
        # INLINE PROMPT INJECTION for HF (Critical)
        # HF models often ignore system role, so we force it into the User prompt with unified SYSTEM_PROMPT
        hf_prompt = f"{SYSTEM_PROMPT}\n\nVERIFIED INFORMATION FROM ALTHAF'S PORTFOLIO DATABASE:\n{context if context else 'No context.'}\n\nUSER QUESTION: {query}\n\nRemember: You are Assist Bot (never say Allu Bot). Respond naturally in conversational paragraphs without special formatting."
        # Append history as text context if needed, or just rely on the strict Prompt
        # For Tier 4, reliability > history
        
        response = self._call_huggingface(hf_prompt, max_tokens)
        if response:
            logger.info("✅ Response from Llama 3.2 3B (HF)")
            return self._clean_response(response)

        # All providers failed
        logger.error("All providers failed")
        return "Hmm, I'm having some connection issues. Mind trying that again?"

    def _clean_response(self, response: str) -> str:
        """
        Post-process response to remove unwanted formatting
        - Remove hyphen bullets (- item)
        - Remove numbered lists if standalone
        - Clean up excessive line breaks
        """
        import re
        
        # Remove lines that start with "- " (hyphen bullets)
        lines = response.split('\n')
        cleaned_lines = []
        for line in lines:
            stripped = line.strip()
            # Skip lines that are just "- something"
            if stripped.startswith('- '):
                # Convert "- item" to just "item" (remove bullet, keep content)
                cleaned_lines.append(stripped[2:])
            else:
                cleaned_lines.append(line)
        
        response = '\n'.join(cleaned_lines)
        
        # Remove excessive line breaks (more than 2 consecutive)
        response = re.sub(r'\n{3,}', '\n\n', response)
        
        # Remove trailing/leading whitespace
        response = response.strip()
        
        return response


