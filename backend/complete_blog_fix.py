#!/usr/bin/env python3
"""
COMPLETE FIX:
1. Delete placeholder blogs
2. Convert markdown to clean plain text (remove #, **, ___, etc.)
3. Fix excessive spacing
4. Ensure uniform font (no formatting that causes size changes)
"""

import json
import re

# Read blogs
with open('frontend/public/data/blogs.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

blogs = data['blogs']
print(f"Starting with {len(blogs)} blogs\n")

# Find ALL placeholder blogs
placeholder_indices = []
for i, blog in enumerate(blogs):
    summary = blog.get('summary', '')
    content = blog.get('content', '')
    title = blog.get('title', '')
    
    # Check for placeholders
    is_placeholder = (
        'Upcoming blog post' in summary or
        'technology trends' in summary.lower() or
        len(content) < 1000 or
        'Latest Insights on Domain-Driven Design' in title or
        'Latest Insights on Multi-Cloud' in title
    )
    
    if is_placeholder:
        placeholder_indices.append(i)
        print(f"FOUND PLACEHOLDER: Blog {i+1} - {title[:60]}")

# Delete placeholders (reverse order)
for idx in sorted(placeholder_indices, reverse=True):
    removed = blogs.pop(idx)
    print(f"✅ DELETED: {removed['title'][:70]}\n")

print(f"\n{'='*70}")
print(f"Remaining: {len(blogs)} blogs")
print(f"{'='*70}\n")

# Fix formatting in all remaining blogs
for i, blog in enumerate(blogs):
    original_content = blog.get('content', '')
    content = original_content
    
    # Remove all markdown formatting
    # 1. Remove headers (# ## ###)
    content = re.sub(r'^#{1,6}\s+', '', content, flags=re.MULTILINE)
    
    # 2. Remove horizontal rules (---)
    content = re.sub(r'^-{3,}$', '', content, flags=re.MULTILINE)
    
    # 3. Remove bold/italic markers but keep text
    content = re.sub(r'\*\*([^\*]+)\*\*', r'\1', content)  # **bold** → bold
    content = re.sub(r'\*([^\*]+)\*', r'\1', content)      # *italic* → italic
    content = re.sub(r'__([^_]+)__', r'\1', content)       # __bold__ → bold
    content = re.sub(r'_([^_]+)_', r'\1', content)         # _italic_ → italic
    
    # 4. Fix excessive newlines (more than 2 → exactly 2)
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    # 5. Remove leading/trailing whitespace from each line
    lines = content.split('\n')
    lines = [line.strip() for line in lines]
    content = '\n'.join(lines)
    
    # 6. Remove the author byline (already in component)
    content = re.sub(r'By Althaf Hussain Syed\s*', '', content)
    content = re.sub(r'DevOps Engineer \| Infrastructure Engineer\s*', '', content)
    
    # 7. Clean up the result
    content = content.strip()
    
    # Update blog
    blog['content'] = content
    
    print(f"✅ Fixed Blog {i+1}: {blog['title'][:65]}")
    print(f"   Before: {len(original_content)} chars, After: {len(content)} chars\n")

# Save
data['blogs'] = blogs
with open('frontend/public/data/blogs.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"\n{'='*70}")
print(f"✅ COMPLETE: {len(blogs)} blogs ready")
print(f"{'='*70}")
print("\nAll blogs now have:")
print("  - No markdown syntax (no # or ** or ___)")
print("  - Clean spacing (max 2 newlines)")
print("  - Uniform text format")
print("  - Placeholder blogs deleted")
