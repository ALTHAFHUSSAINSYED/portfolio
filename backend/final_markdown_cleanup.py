#!/usr/bin/env python3
"""
FINAL FIX: Remove ALL markdown formatting completely
"""

import json
import re

# Read blogs
with open('frontend/public/data/blogs.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

blogs = data['blogs']
print(f"Fixing {len(blogs)} blogs...\n")

for i, blog in enumerate(blogs):
    content = blog['content']
    original_length = len(content)
    
    # Remove ALL # symbols (even mid-line like C# or F#)
    # But be smart - only remove # at start of lines (headers)
    content = re.sub(r'^#+\s*', '', content, flags=re.MULTILINE)
    content = re.sub(r'\n#+\s+', '\n', content)
    
    # Also remove section headers with #
    content = re.sub(r'###\s+', '', content)
    content = re.sub(r'##\s+', '', content)
    content = re.sub(r'#\s+', '', content)
    
    # Remove any remaining standalone # symbols at line starts
    lines = content.split('\n')
    cleaned_lines = []
    for line in lines:
        # If line starts with #, remove it
        if line.strip().startswith('#'):
            line = line.lstrip('#').strip()
        cleaned_lines.append(line)
    content = '\n'.join(cleaned_lines)
    
    # Final cleanup
    content = content.strip()
    
    blog['content'] = content
    
    changed = '✓' if len(content) != original_length else '-'
    print(f"{changed} Blog {i+1}: {blog['title'][:55]}")
    if len(content) != original_length:
        print(f"   Removed {original_length - len(content)} chars\n")

# Save
data['blogs'] = blogs
with open('frontend/public/data/blogs.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"\n✅ ALL BLOGS CLEANED")

# Verify
print("\nVERIFYING...")
any_issues = False
for i, blog in enumerate(blogs):
    content = blog['content']
    has_hash = '#' in content
    has_stars = '**' in content
    
    if has_hash or has_stars:
        print(f"❌ Blog {i+1} still has markdown: # = {has_hash}, ** = {has_stars}")
        any_issues = True

if not any_issues:
    print("✅ All blogs are clean - NO markdown symbols found!")
