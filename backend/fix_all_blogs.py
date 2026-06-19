#!/usr/bin/env python3
"""
Comprehensive fix for all blog content issues:
1. Change 2024 → 2025 in all dates
2. Replace old author titles with "DevOps Engineer | Infrastructure Engineer"
3. Remove CCIM creator line
"""

import json
import re

# Read blogs
with open('frontend/public/data/blogs.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

blogs = data['blogs']
print(f"Processing {len(blogs)} blogs...\n")

updated_count = 0

for i, blog in enumerate(blogs):
    original_content = blog.get('content', '')
    original_date = blog.get('created_at', '')
    modified = False
    
    # 1. Fix dates (2024 → 2025)
    if '2024' in original_date:
        blog['created_at'] = original_date.replace('2024', '2025')
        if 'date' in blog and '2024' in str(blog['date']):
            blog['date'] = blog['date'].replace('2024', '2025')
        modified = True
        print(f"{i+1}. Date fixed: {blog['title'][:50]}")
    
    # 2. Fix author titles in content
    content = original_content
    
    # Replace old author title patterns
    replacements = [
        ('DevOps Engineer | AWS Solutions Architect | Cloud Infrastructure Specialist', 
         'DevOps Engineer | Cloud Infrastructure Engineer'),
        ('DevOps Engineer | Cloud Architect | Infrastructure Specialist',
         'DevOps Engineer | Cloud Infrastructure Engineer'),
        ('DevOps Engineer | Cloud Architect',
         'DevOps Engineer | Infrastructure Engineer'),
        ('DevOps Engineer | AWS Solutions Architect',
         'DevOps Engineer | Cloud Infrastructure Engineer'),
        ('Cloud Infrastructure Specialist',
         'Cloud Infrastructure Engineer'),
        ('AWS Solutions Architect',
         'Cloud Infrastructure Engineer'),
        ('Solutions Architect',
         'Infrastructure Engineer'),
    ]
    
    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
            modified = True
            print(f"{i+1}. Replaced: '{old}' → '{new}'")
    
    # 3. Remove CCIM creator line (entire sentence/paragraph)
    ccim_patterns = [
        r'Creator of the Change-Cost Integration Model \(CCIM\) framework for enterprise integration strategy\.\s*',
        r'Creator of the.*?CCIM.*?framework.*?\.\s*',
        r'Recognized for creating the.*?CCIM.*?\.\s*',
    ]
    
    for pattern in ccim_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            content = re.sub(pattern, '', content, flags=re.IGNORECASE)
            modified = True
            print(f"{i+1}. Removed CCIM creator line")
    
    # 4. Update content if modified
    if content != original_content:
        blog['content'] = content
    
    # 5. Ensure author_title field is correct
    blog['author'] = 'Althaf Hussain Syed'
    blog['author_title'] = 'DevOps Engineer | Infrastructure Engineer'
    
    if modified:
        updated_count += 1
        print(f"   ✅ Blog {i+1} updated\n")

# Save
with open('frontend/public/data/blogs.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"\n{'='*60}")
print(f"COMPLETE: Updated {updated_count} blogs")
print(f"{'='*60}")
print("\nChanges made:")
print("✓ Changed all 2024 dates to 2025")
print("✓ Replaced old author titles with standard format")
print("✓ Removed CCIM creator references")
print("✓ Set author_title field to: 'DevOps Engineer | Infrastructure Engineer'")
