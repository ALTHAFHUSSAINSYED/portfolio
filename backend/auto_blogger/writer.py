"""
Auto-Blogger Writer Module (Agentic Architecture)
Orchestrates the multi-agent generation pipeline:
1. Research Context -> Outliner (Llama 405B) -> Blog Outline
2. Outline Sections -> Drafter (Llama 8B) -> Full Content (Section by Section)
"""

import logging
import os
import json
import re
import time
from typing import Dict, List, Optional
from openai import OpenAI
from backend.auto_blogger.models.model_config import AGENT_ROLES, BLOG_SPECS
from backend.auto_blogger.job_state import get_job_state_manager
from backend.auto_blogger.logger_utils import (
    setup_section_logger,
    setup_agent_logger,
    log_api_call,
    log_section_completion,
    create_job_metadata,
    update_job_metadata,
    IST
)
from datetime import datetime

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BlogWriterAgent")

def strip_leaked_instructions(content: str) -> str:
    """Remove leaked prompt instructions from generated content"""
    import re
    
    # Remove SEO Implementation sections
    content = re.sub(
        r'####?\s*SEO Implementation.*?(?=\n##|\Z)',
        '',
        content,
        flags=re.DOTALL | re.IGNORECASE
    )
    
    # Remove meta description instructions
    content = re.sub(
        r'(?:1\.|•)\s*Meta Descriptions:.*?(?=\n(?:2\.|##)|\Z)',
        '',
        content,
        flags=re.DOTALL | re.IGNORECASE
    )
    
    # Remove "To enhance the search engine optimization" phrases
    content = re.sub(
        r'To enhance the search engine optimization.*?(?=\n##|\Z)',
        '',
        content,
        flags=re.DOTALL | re.IGNORECASE
    )
    
    # Clean up excessive whitespace
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    return content.strip()

def extract_json_from_response(content: str, logger) -> dict:
    """
    Multi-strategy JSON extraction with fallback methods.
    Tries progressively more aggressive extraction techniques.
    
    Strategies:
    1. Strip <think> tags (DeepSeek R1 specific)
    2. Look for ```json ... ``` code blocks
    3. Strip all markdown code blocks
    4. Extract JSON object {...}
    5. Try JSON repair for common errors
    6. Try entire cleaned content
    7. Last resort: find first { to last }
    """
    import json
    import re
    
    logger.debug(f"🔍 Raw model response (first 500 chars): {content[:500]}")
    logger.debug(f"🔍 Response length: {len(content)} chars")
    
    # Strategy 1: Strip DeepSeek <think> tags
    content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
    
    # Strategy 2: Look for ```json ... ``` code blocks first
    json_block_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
    if json_block_match:
        try:
            result = json.loads(json_block_match.group(1))
            logger.info("✅ JSON extracted from ```json block")
            return result
        except json.JSONDecodeError as e:
            logger.warning(f"⚠️ Found ```json block but parsing failed: {e}")
    
    # Strategy 3: Strip all markdown code blocks
    clean_content = content.replace('```json', '').replace('```', '').strip()
    
    # Strategy 4: Extract JSON object {...} with improved regex
    # Use non-greedy matching and handle nested braces better
    dict_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', clean_content, re.DOTALL)
    if dict_match:
        try:
            result = json.loads(dict_match.group(0))
            logger.info("✅ JSON extracted via regex {...} matching")
            return result
        except json.JSONDecodeError as e:
            logger.warning(f"⚠️ Extracted {{ }} but parsing failed: {e}")
            
            # Strategy 5: Try to repair common JSON errors
            try:
                from json_repair import repair_json
                repaired = repair_json(dict_match.group(0))
                result = json.loads(repaired)
                logger.info("✅ JSON repair successful!")
                return result
            except ImportError:
                logger.warning("⚠️ json_repair library not installed, skipping repair")
            except Exception as repair_error:
                logger.warning(f"⚠️ JSON repair failed: {repair_error}")
    
    # Strategy 6: Try the entire cleaned content
    try:
        result = json.loads(clean_content)
        logger.info("✅ JSON parsed from entire cleaned content")
        return result
    except json.JSONDecodeError:
        pass
    
    # Strategy 7: Last resort - look for any JSON-like structure
    # Find the first { and last }
    first_brace = clean_content.find('{')
    last_brace = clean_content.rfind('}')
    
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        potential_json = clean_content[first_brace:last_brace+1]
        try:
            result = json.loads(potential_json)
            logger.info("✅ JSON extracted via first/last brace matching")
            return result
        except json.JSONDecodeError:
            pass
    
    # All strategies failed
    logger.error(f"❌ All JSON extraction strategies failed")
    logger.error(f"Content preview: {clean_content[:200]}...")
    raise ValueError("Invalid JSON format - could not extract valid JSON from response")

class BlogWriter:
    def __init__(self):
        self.api_key = os.getenv("BLOG_KEY") or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            logger.error("Create CHATBOT_KEY env var for OpenRouter access.")
            raise ValueError("Missing OpenRouter API Key")
        
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
            default_headers={
                "HTTP-Referer": "https://portfolio-site.com",
                "X-Title": "Auto-Blogger Agent"
            }
        )
        print(f"DEBUG: Initialized Writer with Key: {self.api_key[:10]}...")

    def generate_blog(self, category: str, research_data: Dict, job_id: str = None) -> str:
        """
        Main entry point for the Agentic Pipeline.
        Phase 1: Outline Generation
        Phase 2: Section-by-Section Drafting (Resumable)
        Phase 3: Assembly
        
        Args:
            category: Blog category
            research_data: Research context
            job_id: Optional job ID for resume capability
        """
        job_mgr = get_job_state_manager()
        
        # Load or create job
        if job_id:
            job = job_mgr.load_job(job_id)
            if not job:
                raise ValueError(f"Job {job_id} not found")
        else:
            # Create new job (legacy path)
            job_id = job_mgr.create_job(category)
            job = job_mgr.load_job(job_id)
        
        logger.info(f"🚀 Starting Agentic Generation for: {category} (Job: {job_id})")
        
        # Create job metadata log
        create_job_metadata(job_id, category, datetime.now(IST))
        
        # Step 1: Generate Outline (if not already done)
        if not job.get('outline'):
            logger.info("Generating outline...")
            outline = self._agent_outliner(category, research_data, job_id)
            if not outline:
                raise RuntimeError("Agent 1 (Outliner) failed to produce a valid outline.")
            job_mgr.save_outline(job_id, outline)
            job = job_mgr.load_job(job_id)  # Reload
        else:
            outline = job['outline']
            # Handle dict format
            if isinstance(outline, dict):
                logger.info(f"✅ Outline exists: {outline.get('title', 'Unknown')}, resuming...")
            else:
                logger.info(f"✅ Outline exists ({len(outline)} sections), resuming...")
        
        # Extract metadata and sections from outline
        if isinstance(outline, dict):
            blog_title = outline.get('title')
            blog_summary = outline.get('summary', '')
            sections = outline.get('sections', [])
            
            # Validate title is not generic
            if not blog_title or "Technical Deep Dive" in blog_title:
                logger.error(f"❌ Outline has generic/missing title: {blog_title}")
                logger.error("Outline data: %s", outline)
                raise ValueError(f"Outliner failed to generate proper title. Got: {blog_title}")
        else:
            # Old format - list of sections (should not happen with new outliner)
            logger.error("❌ Outline is old list format, not dict with title/summary")
            raise ValueError(f"Outliner returned old format (list). Expected dict with title/summary/sections.")
        
        # Validate sections is a list
        if not isinstance(sections, list):
            logger.error(f"❌ Expected sections to be list, got {type(sections)}")
            raise ValueError(f"Invalid sections format: {type(sections)}")
        
        if not sections:
            logger.error("❌ No sections found in outline")
            raise ValueError("Outline has no sections to draft")
        
        logger.info(f"✅ Outline Ready with {len(sections)} sections. Starting Section Drafting Loop (Agent 2)...")
        job_mgr.update_status(job_id, "DRAFTING")

        # Step 2: Loop through sections and draft content (RESUMABLE)
        full_content = self._agent_drafter_loop(category, sections, research_data, job_id)
        
        logger.info(f"🎉 Blog Generation Complete! Length: {len(full_content)} chars")
        
        # Clean Model Artifacts (BOS/EOS tokens)
        full_content = full_content.replace("<s>", "").replace("</s>", "")
        
        # Update job metadata
        update_job_metadata(job_id, {"status": "generated", "completed_at": datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S IST')})
        
        # Fallback Summary Logic
        if not blog_summary:
            logger.warning("Summary missing from outline. Generating fallback summary from content...")
            # Extract first 200 chars, clean markdown headers
            clean_excerpt = full_content.replace("#", "").replace("*", "").strip()[:200]
            last_space = clean_excerpt.rfind(" ")
            if last_space != -1:
                clean_excerpt = clean_excerpt[:last_space]
            blog_summary = f"{clean_excerpt}..."

        # ✅ Strip any leaked SEO instructions or prompt artifacts
        full_content = strip_leaked_instructions(full_content)

        # Return dict with metadata + content
        return {
            "title": blog_title,
            "summary": blog_summary,
            "content": full_content,
            "category": category
        }

    def _agent_outliner(self, category: str, research_data: Dict, job_id: str = None) -> List[str]:
        """
        Agent 1: The Architect
        Uses a robust model to create a structured outline based on research.
        Returns a list of section headings.
        """
        model_cfg = AGENT_ROLES["orchestrator"]
        model_id = model_cfg["primary"]
        
        prompt = f"""
        You are an elite technical blog architect.
        Topic: {category}
        
        RESEARCH SUMMARY:
        {json.dumps(research_data, indent=2)}

        TASK:
        Create a detailed structural outline for a 2500-word technical blog.
        
        CRITICAL TITLE REQUIREMENTS:
        - Title MUST be unique and specific (NOT generic like "Technical Deep Dive")
        - Title should reflect CURRENT TRENDS from the research data
        - Title should be engaging and descriptive
        - Include year (2026) or specific technologies/approaches
        
        GOOD TITLE EXAMPLES:
        - "DevOps in 2026: AI-Driven Pipelines and Self-Healing Infrastructure"
        - "The Rise of Platform Engineering: DevOps' Next Evolution"
        - "Building Resilient Microservices with Kubernetes: A Production Guide"
        
        BAD TITLE EXAMPLES (DO NOT USE):
        - "DevOps - Technical Deep Dive"
        - "Understanding {category}"
        - "{category} Best Practices"
        
        STRUCTURE REQUIREMENTS:
        Generate THREE things:
        1. A UNIQUE, DESCRIPTIVE TITLE (see examples above)
        2. A 2-3 SENTENCE SUMMARY for preview cards
        3. Section outline following this flow:
           - Introduction (Hook + Problem Statement)
           - Core Concept Deep Dive
           - Technical Implementation / How-To (Code heavy)
           - Real-World Use Cases
           - Best Practices / Challenges
           - Future Trends
           - Conclusion

        OUTPUT FORMAT (JSON ONLY):
        {{
            "title": "Unique, specific, engaging title here (NOT generic)",
            "summary": "2-3 sentence preview explaining what this blog covers",
            "sections": ["Introduction: ...", "Section 1: ...", "Conclusion"]
        }}
        
        Do not write the blog content. Just return the JSON structure.
        """

        try:
            models_to_try = [model_cfg["primary"], model_cfg["fallback"]]
            
            for model_id in models_to_try:
                try:
                    logger.info(f"🤖 Output Agent calling {model_id}...")
                    response = self.client.chat.completions.create(
                        model=model_id,
                        messages=[
                            {
                                "role": "system", 
                                "content": "You are a JSON-only API. Respond ONLY with valid JSON. No explanations, no markdown, no extra text. Just pure JSON."
                            },
                            {
                                "role": "user", 
                                "content": prompt
                            }
                        ],
                        max_tokens=2000,
                        temperature=model_cfg["temperature"]
                    )
                    content = response.choices[0].message.content
                    
                    # Use the new robust JSON extraction function
                    outline_data = extract_json_from_response(content, logger)
                    
                    # Validate structure
                    if isinstance(outline_data, dict) and 'sections' in outline_data:
                        sections = outline_data['sections']
                        title = outline_data.get('title')
                        summary = outline_data.get('summary', '')
                        
                        # Validate title is present and not generic
                        generic_titles = ['Technical Deep Dive', 'Understanding', 'Best Practices']
                        if not title or any(generic in title for generic in generic_titles):
                            logger.error(f"❌ Invalid title from outliner: {title}")
                            raise ValueError(f"Invalid title from outliner: {title}")
                        
                        if isinstance(sections, list) and len(sections) > 0:
                            logger.info(f"📋 Outline created:")
                            logger.info(f"   Title: {title}")
                            logger.info(f"   Summary: {summary[:100]}...")
                            logger.info(f"   Sections: {len(sections)}")
                            
                            # Store metadata in outline for later use
                            return {
                                "title": title,
                                "summary": summary,
                                "sections": sections
                            }
                        else:
                            raise ValueError("Invalid outline structure - sections is not a valid list")
                    else:
                        # Old format or invalid structure
                        if isinstance(outline_data, list):
                            logger.error("❌ Received old list format from outliner - this should not happen!")
                            raise ValueError(f"Outliner model {model_id} failed to follow instructions. Returned list instead of dict with title/summary.")
                        else:
                            logger.error(f"❌ Invalid outline structure: {type(outline_data)}")
                            raise ValueError("Invalid outline format - missing 'sections' key")

                except Exception as e:
                    logger.warning(f"⚠️ Model {model_id} failed: {e}")
                    if model_id == models_to_try[-1]:
                        logger.error("❌ All models failed for Outliner.")
                        return None
                    time.sleep(2)
                    continue
            
            return None # Should be unreachable if logic is correct, but safe fallback
                
        except Exception as e:
            logger.error(f"Writer Agent Error: {e}")
            print(f"DEBUG: WRITER EXCEPTION: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _agent_drafter_loop(self, category: str, sections: List[str], research_data: Dict, job_id: str) -> str:
        """
        Agent 2: The Builder (Loop)
        Uses Llama 8B to write each section individually to maintain context and depth.
        
        Args:
            category: Blog category
            sections: List of section headings (NOT outline dict)
            research_data: Research context
            job_id: Job identifier for state management
        """
        model_cfg = AGENT_ROLES["drafter"]
        model_id = model_cfg["primary"]
        job_mgr = get_job_state_manager()
        
        # Validate input
        if not isinstance(sections, list):
            raise TypeError(f"Expected sections to be list, got {type(sections)}")
        
        # Load existing sections from MongoDB
        job = job_mgr.load_job(job_id)
        completed_sections = job_mgr.get_completed_sections(job_id)
        
        full_draft = []
        
        for index, section in enumerate(sections):
            # CHECK: Skip if already completed
            if index in completed_sections:
                logger.info(f"⏭️ Section {index + 1}/{len(sections)} already completed, skipping: {section}")
                full_draft.append(completed_sections[index])
                continue
            
            # Setup section logger
            section_logger = setup_section_logger(job_id, index, section)
            section_logger.info(f"Starting Section {index + 1}/{len(sections)}: {section}")
            logger.info(f"✍️ Drafting Section {index + 1}/{len(sections)}: {section}")
            
            # Context Chunking: Send strict context to avoid 8k limit
            # Send: Research summary + Current Section Goal + Previous 200 words (for flow)
            prev_context = full_draft[-1][-500:] if full_draft else "Start of blog."
            
            prompt = f"""
            You are a technical writer drafting ONE section of a blog.
            Blog Topic: {category}
            Current Section: "{section}"
            
            Global Context (Research):
            {json.dumps(research_data)[:3000]} # Truncated to save tokens
            
            Previous Paragraph (Connect to this):
            "...{prev_context}"
            
            TASK:
            Write the full content for the section "{section}".
            - Length: Approx 300-400 words.
            - Style: Authoritative, technical, engaging.
            - If this is a code section, provide valid code snippets.
            - Don't write "Here is the section". Just write the content.
            """

            models_to_try = [model_cfg["primary"], model_cfg["fallback"]]
            
            try_count = 0
            success = False
            
            while try_count < 2 and not success:  # Retry loop (logic error here in original, fixing to iterate models)
                 # Better logic: Try Primary (2 attempts) -> Fallback (2 attempts)
                 # Creating unified list of attempts: [Primary, Primary, Fallback, Fallback]
                 attempt_queue = [models_to_try[0], models_to_try[0], models_to_try[1], models_to_try[1]]
                 
                 for attempt_model in attempt_queue:
                    try:
                        logger.info(f"Trying model: {attempt_model}")
                        response = self.client.chat.completions.create(
                            model=attempt_model,
                            messages=[{"role": "user", "content": prompt}],
                            max_tokens=model_cfg["max_tokens"],
                            temperature=model_cfg["temperature"]
                        )
                        content = response.choices[0].message.content.strip()
                        
                        # ATOMIC VALIDATION: Is this section complete?
                        if self._validate_section(content):
                            # Success! Format and Append
                            if not content.startswith("#"):
                                formatted_section = f"\n\n## {section}\n\n{content}"
                            else:
                                formatted_section = f"\n\n{content}"
                            
                            # SAVE TO MONGODB IMMEDIATELY
                            job_mgr.save_section(job_id, index, formatted_section)
                            section_logger.info(f"✅ Section {index} saved to MongoDB")
                            
                            # Log metrics
                            word_count = len(content.split())
                            char_count = len(content)
                            log_section_completion(section_logger, index, word_count, char_count)
                            
                            full_draft.append(formatted_section)
                            success = True
                            time.sleep(15)
                            break
                        else:
                            logger.warning(f"⚠️ Generated section incomplete/cut-off. Discarding entirely. (Attempt {attempt + 1})")
                            # Do NOT append partial content. Retry or Fail completely.
                            
                    except Exception as e:
                         logger.warning(f"Drafting error ({attempt_model}): {e}")
                         time.sleep(5)
                 
                 if success: break
                 try_count = 2 # Force exit if queue exhausted (failed all models)
            
            if not success:
                 logger.error(f"❌ Failed to draft section: {section}. Skipping.")
                 # ATOMIC FAIL: Do not append header. Do not append error token. Just SKIP.
                 # The blog will be shorter, but 100% clean.
        
        # Assemble and return the complete blog
        # No more post-processing trim needed because we validated atomic sections upstream
        complete_blog = "\n".join(full_draft)
        
        logger.info(f"✅ Blog assembly complete: {len(complete_blog)} characters (Atomic Verified)")
        return complete_blog

    def _validate_section(self, content: str) -> bool:
        """
        Atomic Section Validator:
        Returns True if section looks complete.
        Returns False if it looks cut-off or broken.
        """
        if not content or len(content) < 50:
            return False
            
        # Structure check: Does it terminate properly?
        stripped = content.rstrip()
        
        # Safe endings
        if stripped.endswith("```"): return True
        if stripped.endswith("}"): return True
        if stripped.endswith("]"): return True
        
        # Punctuation check
        terminators = ['.', '!', '?', '"', ')']
        if any(stripped.endswith(t) for t in terminators):
            return True
            
        return False

    
    def revise_blog(self, draft: str, feedback: Dict) -> str:
        """
        Refines the draft based on Critic's specific feedback.
        """
        logger.info("🔧 Writer Agent: Revising draft based on feedback...")
        
        model_cfg = AGENT_ROLES["drafter"]
        model_id = model_cfg["primary"]
        
        prompt = f"""
        You are a technical editor refining a blog post.
        
        CRITIC FEEDBACK (WEAKNESSES TO FIX):
        {json.dumps(feedback.get('weaknesses', []), indent=2)}
        
        CURRENT DRAFT:
        {draft[:6000]} # Truncated
        
        TASK:
        Rewrite the blog to address the weaknesses.
        - Improve clarity and depth.
        - Fix any mentioned structural issues.
        - Maintain the original markdown formatting.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=model_id,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000, # Revision limit
                temperature=model_cfg["temperature"]
            )
            revised_content = response.choices[0].message.content.strip()
            return revised_content
        except Exception as e:
            logger.error(f"❌ Revision failed: {e}")
            return draft # Return original if revision fails
