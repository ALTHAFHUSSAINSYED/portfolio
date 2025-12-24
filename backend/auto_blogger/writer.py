"""
Blog Writer Module
Generates 2500-word technical blogs using Multi-Tier AI models (Gemini Priority)
"""

import os
import logging
import json
import time
import google.generativeai as genai
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from .models.model_config import MODELS_CONFIG, BLOG_SPECS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BlogWriter")

class BlogWriter:
    def __init__(self):
        # Load env vars
        load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '.env'))
        
        # Setup Gemini
        self.gemini_key = os.getenv("GEMINI_BLOG_API_KEY") or os.getenv("GEMINI_API_KEY")
        if self.gemini_key:
            genai.configure(api_key=self.gemini_key)
        else:
            logger.error("No Gemini API Key found!")

        # Load Template
        self.template_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            "BLOG_GENERATION_TEMPLATE.md"
        )
        self.template_content = self._load_template()

    def _load_template(self) -> str:
        """Load the blog generation template"""
        try:
            with open(self.template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to load template: {e}")
            return ""

    def _call_gemini(self, model_id: str, prompt: str) -> Optional[str]:
        """Call Gemini API"""
        try:
            logger.info(f"Calling Gemini model: {model_id}")
            # Map generic IDs to specific ones if needed, or use as is
            model = genai.GenerativeModel(model_id)
            
            # Configure for long output
            generation_config = genai.types.GenerationConfig(
                max_output_tokens=8192,
                temperature=0.7,
            )
            
            response = model.generate_content(prompt, generation_config=generation_config)
            return response.text
        except Exception as e:
            logger.error(f"Gemini call failed for {model_id}: {e}")
            return None

    def generate_blog(self, research_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a complete blog post draft"""
        category = research_data.get("category", "Technology")
        logger.info(f"Starting blog generation for: {category}")

        # Construct Prompt
        prompt = f"""
        YOU ARE AN ELITE TECHNICAL BLOG WRITER.
        
        TASK: Write a 2500-word blog post for the category: {category}
        
        RESEARCH DATA (Use this for content/trends):
        {json.dumps(research_data, indent=2)}
        
        STRICT REQUIREMENTS:
        1. **Word Count:** Target {BLOG_SPECS['target_word_count']} words. Minimum {BLOG_SPECS['min_word_count']}.
        2. **Framework:** Use the "Change-Cost Integration Model (CCIM)" framework explicitly.
        3. **Tone:** Authoritative, "Elite-Tier", opinionated. Define reality, don't just explain it.
        4. **Structure:** Follow the template below EXACTLY.
        5. **No Fluff:** Every sentence must add value. Include code snippets, real-world examples, and "knife sentences" (quotable/sharp).
        
        BLOG TEMPLATE STRUCTURE:
        {self.template_content}
        
        OUTPUT FORMAT:
        Return ONLY the raw Markdown text. Do not include "Here is the blog" or JSON wrapping.
        start with title (h1).
        """

        # Iterate through tiers
        draft_content = None
        used_model = None

        for model_cfg in MODELS_CONFIG:
            logger.info(f"Trying Tier {model_cfg['tier']}: {model_cfg['name']}")
            
            if model_cfg['provider'] == 'gemini':
                draft_content = self._call_gemini(model_cfg['model_id'], prompt)
            
            if draft_content and len(draft_content) > 1000:
                used_model = model_cfg['name']
                logger.info(f"Successfully generated draft using {used_model}")
                break
            else:
                logger.warning(f"Tier {model_cfg['tier']} failed or produced empty output.")

        if not draft_content:
            raise Exception("All model tiers failed to generate blog draft.")

        # Construct Draft Object
        draft = {
            "title": self._extract_title(draft_content),
            "content": draft_content,
            "category": category,
            "research_used": research_data,
            "generated_at": time.time(),
            "model_used": used_model,
            "status": "draft"
        }
        
        return draft

    def _extract_title(self, content: str) -> str:
        """Extract H1 title from markdown"""
        for line in content.split('\n'):
            if line.startswith('# '):
                return line.replace('# ', '').strip()
        return "Untitled Blog Post"

if __name__ == "__main__":
    # Test
    from .researcher import BlogResearcher
    researcher = BlogResearcher()
    res_data = researcher.get_fallback_research("DevOps")
    
    writer = BlogWriter()
    draft = writer.generate_blog(res_data)
    print(f"Generated Draft Title: {draft['title']}")
    print(f"Length: {len(draft['content'])} chars")
