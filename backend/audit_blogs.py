#!/usr/bin/env python3
"""
Comprehensive audit of all blogs to find what needs to be fixed
"""

import json
import re
from datetime import datetime

# Read blogs
with open('frontend/public/data/blogs.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

blogs = data['blogs']

print("=" * 80)
print("COMPREHENSIVE BLOG CONTENT AUDIT")
print("=" * 80)
print(f"\nTotal Blogs: {len(blogs)}\n")

# 1. Check dates
print("\n" + "="*80)
print("1. DATE AUDIT (Need to change 2024 → 2025)")
print("="*80)
date_issues = []
for i, blog in enumerate(blogs):
    date_str = blog.get('created_at', 'NO DATE')
    if '2024' in date_str:
        date_issues.append((i+1, blog['title'][:60], date_str))

print(f"Found {len(date_issues)} blogs with 2024 dates:")
for num, title, date in date_issues:
    print(f"  {num}. {title}")
    print(f"      Current: {date}")
    print(f"      Will change to: {date.replace('2024', '2025')}\n")

# 2. Check for old author titles in content
print("\n" + "="*80)
print("2. AUTHOR TITLE AUDIT (in blog content)")
print("="*80)

old_patterns = [
    "Cloud Architect",
    "AWS Solutions Architect", 
    "AWS Solution Architect",
    "Cloud Infrastructure Specialist",
    "Solutions Architect"
]

title_issues = []
for i, blog in enumerate(blogs):
    content = blog.get('content', '')
    found_issues = []
    
    for pattern in old_patterns:
        if pattern in content:
            # Find the context (line containing the pattern)
            lines = content.split('\n')
            for line in lines:
                if pattern in line:
                    found_issues.append((pattern, line.strip()[:100]))
                    break
    
    if found_issues:
        title_issues.append((i+1, blog['title'][:60], found_issues))

print(f"Found {len(title_issues)} blogs with old author titles:")
for num, title, issues in title_issues:
    print(f"\n  {num}. {title}")
    for pattern, line in issues:
        print(f"      ❌ Found: '{pattern}'")
        print(f"      In line: {line}...")

# 3. Check for CCIM creator reference
print("\n" + "="*80)
print("3. CCIM CREATOR LINE AUDIT")
print("="*80)

ccim_issues = []
for i, blog in enumerate(blogs):
    content = blog.get('content', '')
    if 'Creator of' in content and 'CCIM' in content:
        # Find the full line
        lines = content.split('\n')
        for line in lines:
            if 'Creator of' in line and ('CCIM' in line or 'framework' in line):
                ccim_issues.append((i+1, blog['title'][:60], line.strip()))
                break

print(f"Found {len(ccim_issues)} blogs with CCIM creator reference:")
for num, title, line in ccim_issues:
    print(f"\n  {num}. {title}")
    print(f"      ❌ Line to remove: {line[:150]}...")

# 4. Check "About the Author" sections
print("\n" + "="*80)
print("4. 'ABOUT THE AUTHOR' SECTION AUDIT")
print("="*80)

about_issues = []
for i, blog in enumerate(blogs):
    content = blog.get('content', '')
    if 'About the Author' in content:
        # Extract the "About" section
        match = re.search(r'About the Author.*?\n.*?\n.*?\n', content, re.DOTALL)
        if match:
            about_text = match.group()
            if any(p in about_text for p in old_patterns):
                about_issues.append((i+1, blog['title'][:60], about_text[:200]))

print(f"Found {len(about_issues)} blogs with old info in About section:")
for num, title, about_text in about_issues:
    print(f"\n  {num}. {title}")
    print(f"      Current About section:")
    print(f"      {about_text}...")

# 5. Summary
print("\n" + "="*80)
print("SUMMARY OF REQUIRED CHANGES")
print("="*80)
print(f"✓ Date changes needed: {len(date_issues)} blogs")
print(f"✓ Author title fixes needed: {len(title_issues)} blogs")
print(f"✓ CCIM line removals needed: {len(ccim_issues)} blogs")
print(f"✓ About section fixes needed: {len(about_issues)} blogs")
print(f"\nTotal blogs requiring updates: {len(set([x[0] for x in date_issues + title_issues + ccim_issues + about_issues]))}")
print("="*80)
