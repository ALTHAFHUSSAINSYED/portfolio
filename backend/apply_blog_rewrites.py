#!/usr/bin/env python3
"""
Update blogs.json with all 9 rewritten blogs
"""

import json
from pathlib import Path

# Map blog files to blog indices
blog_files = {
    0: 'backend/blog_rewrites/blog_01_lowcode.md',
    1: 'backend/blog_rewrites/blog_02_zerotrust.md',
    2: 'backend/blog_rewrites/blog_03_ddd.md',
    3: 'backend/blog_rewrites/blog_04_gitops.md',
    4: 'backend/blog_rewrites/blog_05_mlops.md',
    5: 'backend/blog_rewrites/blog_06_multicloud.md',
    6: 'backend/blog_rewrites/blog_07_gitops_modern.md',
    7: 'backend/blog_rewrites/blog_08_mlops_deployment.md',
    8: 'backend/blog_rewrites/blog_09_multicloud_insights.md',
}

# Read blogs.json
with open('frontend/public/data/blogs.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

blogs = data['blogs']
print(f"Updating {len(blogs)} blogs with rewritten content...\n")

# Update each blog
for idx, filepath in blog_files.items():
    if idx < len(blogs):
        with open(filepath, 'r', encoding='utf-8') as f:
            new_content = f.read()
        
        blogs[idx]['content'] = new_content
        print(f"✅ Blog {idx+1}: {blogs[idx]['title'][:60]}... ({len(new_content)} chars)")

# Save updated blogs
data['blogs'] = blogs
with open('frontend/public/data/blogs.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"\n✅ All 9 blogs updated in blogs.json")
print(f"Total content: {sum(len(b['content']) for b in blogs):,} characters")
