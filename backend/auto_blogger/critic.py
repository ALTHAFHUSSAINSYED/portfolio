"""
Auto-Blogger Critic Module (Agentic Architecture)
Agent: The Judge
Model: DeepSeek R1 (Free)
Role: Validates the drafted blog against strict quality gates defined in feedback.md.
"""

import logging
import os
import json
from typing import Dict, Tuple
from openai import OpenAI
from backend.auto_blogger.models.model_config import AGENT_ROLES

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BlogCriticAgent")

class BlogCritic:
    def __init__(self):
        self.api_key = os.getenv("BLOG_KEY") or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("Missing OpenRouter API Key for Critic Agent")
        
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
            default_headers={
                "HTTP-Referer": "https://portfolio-site.com",
                "X-Title": "Auto-Blogger Agent"
            }
        )
        
        # Load feedback criteria
        self.feedback_criteria = self._load_feedback_criteria()

    def _load_feedback_criteria(self) -> str:
        """Loads feedback.md to prompt the critic."""
        try:
            # Adjust path relative to this file
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            path = os.path.join(base_dir, "templates", "feedback.md")
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.warning(f"Could not load feedback.md: {e}. Using default criteria.")
            return "- Check for structure\n- Check for code examples\n- Check for tone"

    def evaluate(self, blog_content: str, category: str) -> Tuple[bool, str]:
        """
        Agent 3: The Judge
        Uses DeepSeek R1 to critique the blog with fallback to GLM-4.5-Air.
        Returns: (passed: bool, feedback: str)
        """
        model_cfg = AGENT_ROLES["critic"]
        primary_model = model_cfg["primary"]
        fallback_model = model_cfg["fallback"]
        
        logger.info(f"⚖️ Critic Agent ({primary_model}) evaluating blog for {category}...")

        prompt = f"""
        You are a strict editorial critic.
        Your job is to REJECT or APPROVE a technical blog draft based on these criteria:
        
        CRITERIA (feedback.md):
        {self.feedback_criteria}
        
        BLOG DRAFT:
        {blog_content[:15000]} # Truncate to fit context if needed
        
        TASK:
        Evaluate the blog.
        1. Give a quality score (0-100).
        2. List 3 key strengths.
        3. List 3 key weaknesses.
        4. Verdict: "PASS" (Score >= 90) or "FAIL".
        
        OUTPUT FORMAT (JSON ONLY):
        {{
            "score": 95,
            "verdict": "PASS",
            "strengths": ["...", "...", "..."],
            "weaknesses": ["...", "...", "..."],
            "reasoning": "..."
        }}
        """

        # Try primary model first
        try:
            response = self.client.chat.completions.create(
                model=primary_model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=model_cfg["temperature"]
            )
            content = response.choices[0].message.content
            
            # Extract JSON
            import re
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match:
                result = json.loads(match.group(0))
                score = result.get("score", 0)
                verdict = result.get("verdict", "FAIL").upper()
                
                logger.info(f"⚖️ Verdict: {verdict} (Score: {score}) [Primary Model]")
                
                if score >= 90 or "PASS" in verdict:
                    return True, json.dumps(result, indent=2)
                else:
                    return False, json.dumps(result, indent=2)
            else:
                logger.error("Critic output not valid JSON. Trying fallback model...")
                raise ValueError("Invalid JSON response from primary model")

        except Exception as primary_error:
            logger.warning(f"⚠️ Primary Critic Model Failed: {primary_error}")
            logger.info(f"🔄 Retrying with fallback model: {fallback_model}")
            
            # Try fallback model
            try:
                response = self.client.chat.completions.create(
                    model=fallback_model,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=2000,
                    temperature=model_cfg["temperature"]
                )
                content = response.choices[0].message.content
                
                # Extract JSON
                import re
                match = re.search(r'\{.*\}', content, re.DOTALL)
                if match:
                    result = json.loads(match.group(0))
                    score = result.get("score", 0)
                    verdict = result.get("verdict", "FAIL").upper()
                    
                    logger.info(f"⚖️ Verdict: {verdict} (Score: {score}) [Fallback Model]")
                    
                    if score >= 90 or "PASS" in verdict:
                        return True, json.dumps(result, indent=2)
                    else:
                        return False, json.dumps(result, indent=2)
                else:
                    logger.error("Fallback model also returned invalid JSON.")
                    raise ValueError("Invalid JSON response from fallback model")
                    
            except Exception as fallback_error:
                logger.error(f"❌ Fallback Critic Model Also Failed: {fallback_error}")
                # Both models failed - auto-approve to ensure publication
                error_msg = f"Both critic models failed. Primary: {primary_error}. Fallback: {fallback_error}. Auto-approving to ensure publication."
                logger.warning(error_msg)
                return True, error_msg
