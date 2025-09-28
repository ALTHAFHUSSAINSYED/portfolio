"""
Script to generate blog posts for all categories directly, without API calls
"""

import os
import sys
import time
import json
from datetime import datetime
import logging
import random

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("DirectBlogGenerator")

# Import the agent service module directly
import agent_service

# List of all the categories we want to generate blogs for
CATEGORIES = [
    "Cloud Computing",
    "AI and ML",
    "DevOps",
    "Software Development",
    "Databases",
    "Cybersecurity",
    "Blockchain",
    "Quantum Computing",
    "Edge Computing",
    "IoT Development",
    "Low-Code/No-Code",
    "Frontend Development"
]

def generate_blogs_for_categories():
    """Generate one blog post for each of the 12 categories directly using agent_service"""
    logger.info(f"Starting to generate {len(CATEGORIES)} blog posts...")
    
    # Track successful generations
    successful = []
    failed = []
    
    for category in CATEGORIES:
        logger.info(f"Generating blog post for category: {category}")
        
        # Define a topic for each category to have more specific content
        topic_mapping = {
            "Cloud Computing": "Multi-Cloud Deployment Strategies for Enterprise Applications",
            "AI and ML": "Implementing MLOps Pipelines for Production AI Systems",
            "DevOps": "GitOps Workflow for Kubernetes Applications",
            "Software Development": "Domain-Driven Design in Modern Software Development",
            "Databases": "Database Sharding Strategies for High-Scale Applications",
            "Cybersecurity": "Implementing Zero Trust Architecture in Modern Applications",
            "Blockchain": "Smart Contract Development Best Practices",
            "Quantum Computing": "Quantum-Safe Cryptography Implementation Strategies",
            "Edge Computing": "Edge-Cloud Hybrid Application Development",
            "IoT Development": "Building Scalable IoT Architecture Patterns",
            "Low-Code/No-Code": "Enterprise Integration with Low-Code Platforms",
            "Frontend Development": "Micro-Frontend Architecture Implementation Strategies"
        }
        
        # Get the specific topic for this category
        topic = topic_mapping.get(category)
        
        # If no specific mapping, use a default topic
        if not topic:
            topic = f"Latest Trends in {category}"
        
        try:
            # Try to generate a blog post using the agent_service directly
            logger.info(f"Generating blog for topic: {topic}")
            
            # Call the generate_blog_now function from agent_service
            blog = agent_service.generate_blog_now(topic)
            
            if blog:
                logger.info(f"Successfully generated blog: {blog.get('title', 'Untitled')}")
                
                # Add category to the blog post
                blog['category'] = category
                
                # Convert MongoDB datetime to string for JSON serialization if needed
                if isinstance(blog.get("created_at"), datetime):
                    blog["created_at"] = blog["created_at"].isoformat()
                
                successful.append({
                    "category": category,
                    "title": blog.get('title', 'Untitled'),
                    "summary": blog.get('summary', '')[:100] + '...' if blog.get('summary') else ''
                })
                
                # Save the generated blog to a file for reference
                output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated_blogs")
                os.makedirs(output_dir, exist_ok=True)
                
                # Create a sanitized filename from the title
                sanitized_title = "".join([c if c.isalnum() or c in [' ', '-'] else '_' for c in blog.get('title', 'Untitled')])
                sanitized_title = sanitized_title[:50]  # Limit length
                
                # Save to JSON file
                # Replace both spaces and slashes to make a valid filename
                safe_category = category.replace(' ', '_').replace('/', '_')
                filename = f"{safe_category}_{int(time.time())}.json"
                filepath = os.path.join(output_dir, filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(blog, f, indent=2, ensure_ascii=False)
                
                logger.info(f"Saved blog to {filepath}")
                
            else:
                logger.error(f"Failed to generate blog post for {category}: No content returned")
                failed.append(category)
                
        except Exception as e:
            logger.error(f"Failed to generate blog for {category}: {str(e)}")
            failed.append(category)
        
        # Sleep between requests to avoid overloading
        time.sleep(2)
    
    # Print summary
    logger.info("=" * 80)
    logger.info("GENERATION COMPLETE")
    logger.info("=" * 80)
    logger.info(f"Successfully generated {len(successful)} out of {len(CATEGORIES)} blogs")
    
    if successful:
        logger.info("\nGenerated Blog Posts:")
        for i, blog in enumerate(successful, 1):
            logger.info(f"{i}. Category: {blog['category']}")
            logger.info(f"   Title: {blog['title']}")
            logger.info(f"   Summary: {blog['summary']}")
            logger.info("")
    
    if failed:
        logger.info("\nFailed categories:")
        for category in failed:
            logger.info(f"- {category}")
    
    return successful, failed

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print(" DIRECT BLOG GENERATOR ".center(80, "="))
    print("=" * 80)
    print("\nThis script will generate one blog post for each of the 12 technical categories.")
    print("This will directly use the agent_service module without going through the API.")
    print("This may take several minutes to complete as each blog post is generated with AI.\n")
    
    input("Press Enter to continue...")
    
    successful, failed = generate_blogs_for_categories()
    
    print("\n" + "=" * 80)
    print(" GENERATION COMPLETE ".center(80, "="))
    print("=" * 80)