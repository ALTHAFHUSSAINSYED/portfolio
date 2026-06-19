#!/usr/bin/env python3
"""
Complete verification:
1. Check blog format is clean
2. List exact file paths for all storage locations
"""

import json
import os

print("="*80)
print("COMPLETE BLOG VERIFICATION REPORT")
print("="*80)

# Read blogs
with open('frontend/public/data/blogs.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

blogs = data['blogs']

print(f"\n📊 BLOG COUNT: {len(blogs)} blogs")

# Check each blog
print("\n" + "="*80)
print("FORMAT VERIFICATION:")
print("="*80)

for i, blog in enumerate(blogs):
    content = blog['content']
    title = blog['title']
    
    # Check for markdown
    has_markdown_header = False
    for line in content.split('\n'):
        stripped = line.lstrip()
        if stripped.startswith('#') and len(stripped) > 1 and stripped[1] == ' ':
            has_markdown_header = True
            break
    
    has_bold = '**' in content
    has_underline = '__' in content
    
    status = "✅ CLEAN" if not (has_markdown_header or has_bold or has_underline) else "❌ HAS ISSUES"
    
    print(f"\n{i+1}. {title[:65]}")
    print(f"   Status: {status}")
    print(f"   Content: {len(content)} chars")
    if has_markdown_header:
        print(f"   ⚠️  Has markdown headers")
    if has_bold:
        print(f"   ⚠️  Has ** bold markers")
    if has_underline:
        print(f"   ⚠️  Has __ underline markers")

# File paths
print("\n" + "="*80)
print("📁 EXACT FILE PATHS WHERE BLOGS ARE STORED:")
print("="*80)

print("\n1️⃣  LOCAL REPOSITORY:")
print(f"   File: {os.path.abspath('frontend/public/data/blogs.json')}")
print(f"   Exists: {'YES ✅' if os.path.exists('frontend/public/data/blogs.json') else 'NO ❌'}")

print("\n2️⃣  REMOTE REPOSITORY (GitHub):")
print(f"   URL: https://github.com/ALTHAFHUSSAINSYED/portfolio")
print(f"   Branch: main")
print(f"   File Path: frontend/public/data/blogs.json")
print(f"   Full URL: https://github.com/ALTHAFHUSSAINSYED/portfolio/blob/main/frontend/public/data/blogs.json")

print("\n3️⃣  S3 BUCKET:")
print(f"   Bucket Name: althaf-blogs-storage")
print(f"   File Path: blogs/index.json")
print(f"   Full S3 URI: s3://althaf-blogs-storage/blogs/index.json")
print(f"   Region: (Check AWS Console or EC2 environment)")

print("\n4️⃣  BACKEND API:")
print(f"   API Endpoint: https://api.althafportfolio.site/api/blogs")
print(f"   Data Source: Reads from S3 bucket (s3://althaf-blogs-storage/blogs/index.json)")
print(f"   Backend Code: backend/server.py (blog routes)")

print("\n5️⃣  AMPLIFY (Frontend Deployment):")
print(f"   App URL: https://www.althafportfolio.site")
print(f"   Build Source: GitHub repository (main branch)")
print(f"   Deployed File: build artifacts include blogs.json")
print(f"   Access URL: https://www.althafportfolio.site/blogs")

print("\n6️⃣  EC2 INSTANCE (Auto-Blogger):")
print(f"   Instance: Production EC2 running auto-blogger")
print(f"   Local Path: /home/ubuntu/portfolio/frontend/public/data/blogs.json (estimated)")
print(f"   Syncs TO: S3 bucket when new blogs generated")
print(f"   Pulls FROM: GitHub repository (git pull)")

print("\n" + "="*80)
print("VERIFICATION COMPLETE")
print("="*80)
