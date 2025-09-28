"""
Test script for read_local_blogs.py
"""

import os
import sys
import json
from pathlib import Path

# Add the parent directory to sys.path to allow importing the module
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# Import the function to test
from read_local_blogs import get_local_blogs

def main():
    print("Testing local blogs reader...")
    
    # Get the local blogs
    blogs = get_local_blogs()
    
    # Print the number of blogs found
    print(f"Found {len(blogs)} local blog posts")
    
    # Print details of the first few blogs
    for i, blog in enumerate(blogs[:3]):
        print(f"\nBlog #{i+1}:")
        print(f"  Title: {blog['title']}")
        print(f"  Category: {blog['category']}")
        print(f"  Tags: {', '.join(blog.get('tags', []))}")
        print(f"  Created: {blog.get('created_at', 'Unknown')}")
    
    # Print unique categories
    categories = set(blog.get('category', '') for blog in blogs)
    print(f"\nUnique categories: {', '.join(sorted(categories))}")
    
    # Save to a test output file
    output_file = os.path.join(current_dir, "test_blogs_output.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(blogs, f, indent=2)
    
    print(f"\nSaved blog data to {output_file}")

if __name__ == "__main__":
    main()