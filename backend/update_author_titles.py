#!/usr/bin/env python3
"""
Update author titles in blog content:
- Cloud Architect → Infrastructure Engineer
- Infrastructure Specialist → Infrastructure Engineer  
- AWS Solution Architect → Infrastructure Engineer
- Solutions Architect → Infrastructure Engineer
"""

import json
import re
from pathlib import Path

# Read blogs
blogs_file = Path(__file__).parent.parent / "frontend" / "public" / "data" / "blogs.json"
with open(blogs_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

blogs = data['blogs']
print(f"Updating author titles in {len(blogs)} blogs...\n")

updated_count = 0
for i, blog in enumerate(blogs):
    content = blog.get('content', '')
    original_content = content
    
    # Replace all variations of architect/specialist titles
    content = content.replace('Cloud Architect', 'Infrastructure Engineer')
    content = content.replace('Infrastructure Specialist', 'Infrastructure Engineer')
    content = content.replace('AWS Solution Architect', 'Infrastructure Engineer')
    content = content.replace('Solutions Architect', 'Infrastructure Engineer')
    
    # Also add author_title field for consistency
    blog['author'] = 'Althaf Hussain Syed'
    blog['author_title'] = 'DevOps Engineer | Infrastructure Engineer'
    
    if original_content != content:
        blog['content'] = content
        
        # Extract title line to show what changed
        lines = content.split('\n')
        author_line = [l for l in lines if 'DevOps Engineer' in l or 'Infrastructure Engineer' in l]
        
        print(f"{i+1}. {blog['title'][:60]}")
        if author_line:
            print(f"   New: {author_line[0].strip()}")
        print()
        updated_count += 1

# Save
with open(blogs_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print(f"✅ Updated {updated_count} blogs")
print(f"✅ Added author/author_title fields to all 11 blogs")
print(f"✅ Saved to {blogs_file}")
