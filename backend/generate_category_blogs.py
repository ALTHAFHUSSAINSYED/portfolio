"""
Script to generate blog posts for all categories
This will create one blog post for each of the 12 technical categories
"""

import os
import sys
import requests
import time
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("BlogGenerator")

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
    """Generate one blog post for each of the 12 categories"""
    logger.info(f"Starting to generate {len(CATEGORIES)} blog posts...")
    
    # API endpoints to try (will use the first that works)
    base_urls = [
        'http://localhost:5000',  # Local development
        '',  # Same domain (relative URL)
        'https://althaf-portfolio.onrender.com',
        'https://althaf-portfolio.vercel.app'
    ]
    
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
        
        # Try different API endpoints
        success = False
        for base_url in base_urls:
            try:
                logger.info(f"Trying endpoint: {base_url}/api/generate-blog")
                
                response = requests.post(
                    f"{base_url}/api/generate-blog",
                    json={"topic": topic},
                    timeout=120  # Allow up to 2 minutes for generation
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"Successfully generated blog: {result.get('title')}")
                    successful.append({
                        "category": category,
                        "title": result.get('title'),
                        "summary": result.get('summary')
                    })
                    success = True
                    break
                else:
                    logger.warning(f"Failed with status {response.status_code} at {base_url}")
            except Exception as e:
                logger.error(f"Error with {base_url}: {str(e)}")
        
        if not success:
            logger.error(f"Failed to generate blog for {category}")
            failed.append(category)
        
        # Sleep between requests to avoid overloading the API
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
            logger.info(f"   Summary: {blog['summary'][:100]}...")
            logger.info("")
    
    if failed:
        logger.info("\nFailed categories:")
        for category in failed:
            logger.info(f"- {category}")
    
    return successful, failed

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print(" PORTFOLIO BLOG GENERATOR ".center(80, "="))
    print("=" * 80)
    print("\nThis script will generate one blog post for each of the 12 technical categories.")
    print("This may take several minutes to complete as each blog post is generated with AI.\n")
    
    input("Press Enter to continue...")
    
    successful, failed = generate_blogs_for_categories()
    
    print("\n" + "=" * 80)
    print(" GENERATION COMPLETE ".center(80, "="))
    print("=" * 80)