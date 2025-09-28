"""
Helper module to read locally generated blog posts from JSON files
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LocalBlogsReader")

def get_local_blogs():
    """Read all locally generated blog posts from the generated_blogs directory"""
    try:
        # Define the path to the generated blogs directory
        blog_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated_blogs")
        
        # Check if directory exists
        if not os.path.exists(blog_dir):
            logger.warning(f"Blog directory not found: {blog_dir}")
            return []
            
        blogs = []
        
        # List all JSON files in the directory
        for filename in os.listdir(blog_dir):
            if filename.endswith('.json'):
                try:
                    # Extract category from the filename
                    category = filename.split('_')[0].replace('-', ' ')
                    
                    # Read the blog post from the file
                    with open(os.path.join(blog_dir, filename), 'r', encoding='utf-8') as f:
                        blog = json.load(f)
                        
                    # Ensure the blog has the required fields
                    if not blog.get('title'):
                        continue
                        
                    # Add or update category if not present or if it needs fixing
                    if not blog.get('category'):
                        blog['category'] = category.replace('_', ' ')
                    
                    # Add id if not present
                    if not blog.get('id'):
                        blog['id'] = filename.split('.')[0]
                        
                    # Add published flag
                    blog['published'] = True
                    
                    # Format created_at if it's not already a string
                    if not isinstance(blog.get('created_at'), str):
                        blog['created_at'] = datetime.now().isoformat()
                        
                    blogs.append(blog)
                except Exception as e:
                    logger.error(f"Error reading blog file {filename}: {str(e)}")
        
        # Sort blogs by created_at in descending order
        blogs.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        logger.info(f"Successfully loaded {len(blogs)} local blog posts")
        return blogs
    except Exception as e:
        logger.error(f"Error reading local blogs: {str(e)}")
        return []

if __name__ == "__main__":
    # Test the function
    blogs = get_local_blogs()
    for blog in blogs:
        print(f"Title: {blog['title']}")
        print(f"Category: {blog['category']}")
        print("-" * 40)