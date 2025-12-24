"""
Blog Critic Module
Validates blog drafts against 'feedback.md' (Elite-Tier Gate) using Gemini.
"""

import os
import logging
import json
import google.generativeai as genai
from typing import Dict, Any
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BlogCritic")

class BlogCritic:
    def __init__(self):
        # Load env vars
        load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '.env'))
        
        # Setup Gemini
        self.gemini_key = os.getenv("GEMINI_BLOG_API_KEY") or os.getenv("GEMINI_API_KEY")
        if self.gemini_key:
            genai.configure(api_key=self.gemini_key)
        
        # Load Feedback Checklist
        self.feedback_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            "feedback.md"
        )
        self.checklist_content = self._load_checklist()

    def _load_checklist(self) -> str:
        try:
            with open(self.feedback_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to load feedback.md: {e}")
            return ""

    def evaluate(self, draft: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate draft against elite criteria"""
        logger.info(f"Evaluating draft: {draft.get('title')}")
        
        prompt = f"""
        YOU ARE AN ELITE BLOG EDITOR AND CRITIC.
        
        TASK: Evaluate the following blog post against the "Elite-Tier Requirements" provided below.
        
        BLOG CONTENT:
        {draft.get('content')}
        
        CRITICISM CRITERIA (feedback.md):
        {self.checklist_content}
        
        INSTRUCTIONS:
        1. Score the blog from 0-100 based on the "Brutal Scorecard".
        2. Identify "Knife Sentences" (Must have 3+).
        3. Check for specific "Enemy Identification".
        4. Verify "CCIM Framework" usage.
        5. Check if the tone is "Authoritative/Aggressive" (not just educational).
        
        OUTPUT JSON FORMAT ONLY:
        {{
            "score": <0-100 integer>,
            "passed": <boolean, true if score >= 92>,
            "feedback": {{
                "worldview": <0-10>,
                "intellectual_risk": <0-10>,
                "authority": <0-10>,
                "sharpness": <0-10>,
                "framework": <0-10>
            }},
            "knife_sentences_found": [<list of strings>],
            "required_edits": [<list of specific actionable changes if failed>]
        }}
        """
        
        try:
            model = genai.GenerativeModel('gemini-2.0-flash-lite-preview-02-05') # Fast evaluation
            response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
            result = json.loads(response.text)
            
            logger.info(f"Evaluation Score: {result.get('score')}")
            return result
            
        except Exception as e:
            logger.error(f"Evaluation failed: {e}")
            # Fail-safe return
            return {"score": 0, "passed": False, "error": str(e)}

if __name__ == "__main__":
    # Test
    critic = BlogCritic()
    # Mock draft for testing import
    draft = {"title": "Test", "content": "# Test Blog\n This is a test."}
    res = critic.evaluate(draft)
    print(json.dumps(res, indent=2))
