#!/usr/bin/env python3
"""
Fix all blog issues:
1. Delete placeholder blogs
2. Fix markdown formatting (remove # symbols, fix spacing)
3. Convert to plain HTML-friendly format
"""

import json
import re

# Read blogs
with open('frontend/public/data/blogs.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

blogs = data['blogs']
print(f"Starting with {len(blogs)} blogs\n")

# Find placeholder blogs
placeholder_indices = []
for i, blog in enumerate(blogs):
    summary = blog.get('summary', '')
    content = blog.get('content', '')
    
    if 'Upcoming blog post' in summary or len(content) < 500:
        placeholder_indices.append(i)
        print(f"Found placeholder: Blog {i+1} - {blog['title'][:50]}")

# Delete placeholders (reverse order)
for idx in sorted(placeholder_indices, reverse=True):
    removed = blogs.pop(idx)
    print(f"Deleted: {removed['title'][:60]}")

print(f"\nRemaining: {len(blogs)} blogs\n")

# Fix markdown formatting in remaining blogs
for i, blog in enumerate(blogs):
    content = blog.get('content', '')
    
    # Remove markdown headers (# ## ###)
    content = re.sub(r'^#+\s+', '', content, flags=re.MULTILINE)
    
    # Remove excessive newlines (more than 2 consecutive)
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    # Remove markdown bold (**text** → text or keep for emphasis)
    # Actually keep bold, just ensure it's clean
    
    # Remove special characters that shouldn't be there
    content = content.replace('---\n', '\n')  # Remove horizontal rules
    
    # Clean up spacing before/after paragraphs
    content = content.strip()
    
    blog['content'] = content
    print(f"Fixed Blog {i+1}: {blog['title'][:50]}")

# Save
data['blogs'] = blogs
with open('frontend/public/data/blogs.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"\n✅ Complete: {len(blogs)} blogs cleaned and ready")
