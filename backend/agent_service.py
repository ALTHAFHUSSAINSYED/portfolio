import logging
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('AlluAgent')

def generate_blog_now(topic=None):
    """
    Generate a blog post on-demand using the new auto-blogger system.
    This delegates to the auto_blogger modules for quality content generation.
    """
    try:
        from backend.auto_blogger.researcher import BlogResearcher
        from backend.auto_blogger.writer import BlogWriter
        from backend.auto_blogger.critic import BlogCritic
        from backend.auto_blogger.publisher import BlogPublisher
        
        logger.info(f"On-demand blog generation requested for topic: {topic}")
        
        # Determine category from topic or use default
        category = "Software_Development"  # Default category
        if topic:
            topic_lower = topic.lower()
            if any(kw in topic_lower for kw in ['ai', 'machine learning', 'ml', 'neural']):
                category = "AI_and_ML"
            elif any(kw in topic_lower for kw in ['cloud', 'aws', 'azure', 'gcp']):
                category = "Cloud_Computing"
            elif any(kw in topic_lower for kw in ['security', 'cyber', 'encryption']):
                category = "Cybersecurity"
            elif any(kw in topic_lower for kw in ['devops', 'ci', 'cd', 'jenkins', 'docker', 'kubernetes']):
                category = "DevOps"
            elif any(kw in topic_lower for kw in ['low-code', 'no-code']):
                category = "Low-Code_No-Code"
        
        # 1. Research
        researcher = BlogResearcher()
        research_data = researcher.analyze_trends(category)
        logger.info("Research phase completed")
        
        # 2. Write Draft
        writer = BlogWriter()
        draft = writer.generate_blog(category, research_data)
        logger.info("Draft generation completed")
        
        # 3. Critique (single pass for on-demand generation)
        critic = BlogCritic()
        passed, review_json = critic.evaluate(draft.get('content', ''), category)
        
        try:
            review = json.loads(review_json)
            score = review.get('score', 0)
            logger.info(f"Critique score: {score}")
            
            # If failed, try one revision (Using text content)
            if not passed and score < 85:
                logger.info("Draft below threshold, revising...")
                # Note: draft is a dict from writer.generate_blog, we need content
                content = draft.get('content', '')
                revised_content = writer.revise_blog(content, review)
                draft['content'] = revised_content
                
                # Re-evaluate
                passed, review_json = critic.evaluate(revised_content, category)
        except Exception as e:
            logger.warning(f"Critique parsing error: {e}, proceeding anyway")
        
        # 4. Publish
        publisher = BlogPublisher()
        # Publisher expects the full blog dict object
        url = publisher.publish(draft)
        logger.info(f"Blog published successfully: {url}")
        
        # Return in expected format
        return {
            "title": draft.get("title"),
            "content": draft.get("content"),
            "category": draft.get("category"),
            "tags": draft.get("tags", []),
            "url": url,
            "published": True
        }
        
    except Exception as e:
        logger.error(f"Auto-blogger generation failed: {e}")
        
        # Fallback if all else fails
        current_date = datetime.now()
        return {
            "title": f"Blog Generation Error",
            "content": f"Unable to generate blog at this time. Error: {str(e)}",
            "topic": topic or "General",
            "created_at": current_date,
            "tags": ["error"],
            "published": False
        }