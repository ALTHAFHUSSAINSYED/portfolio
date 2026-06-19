"""
Create a complete JSON file with all the generated blogs
"""

import os
import json
import sys
from pathlib import Path

def main():
    # Define the path to the generated blogs directory
    blogs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated_blogs")
    
    # Define the path to the output file
    output_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                              "frontend", "public", "data", "blogs.json")
    
    # Create the output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Check if directory exists
    if not os.path.exists(blogs_dir):
        print(f"Blog directory not found: {blogs_dir}")
        return
    
    blogs = []
    
    # List all JSON files in the directory
    for filename in os.listdir(blogs_dir):
        if filename.endswith('.json'):
            try:
                # Extract category from the filename
                category = filename.split('_')[0].replace('-', ' ')
                
                # Read the blog post from the file
                with open(os.path.join(blogs_dir, filename), 'r', encoding='utf-8') as f:
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
                
                blogs.append(blog)
            except Exception as e:
                print(f"Error reading blog file {filename}: {str(e)}")
    
    # Sort blogs by created_at in descending order
    blogs.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    print(f"Successfully loaded {len(blogs)} local blog posts")
    
    # Save all blogs to the output file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({"blogs": blogs}, f, indent=2)
    
    print(f"Saved all blogs to {output_file}")

if __name__ == "__main__":
    main()