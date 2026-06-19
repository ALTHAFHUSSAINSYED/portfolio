#!/usr/bin/env python3
"""
Delete duplicate blogs (7 & 8) and prepare for rewriting remaining 9 blogs
"""

import json

# Read current blogs
with open('frontend/public/data/blogs.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

blogs = data['blogs']
print(f"Current blog count: {len(blogs)}\n")

# Identify duplicates
print("Checking for duplicates:")
print(f"Blog 2: {blogs[1]['title']}")
print(f"Blog 3: {blogs[2]['title']}")
print(f"Blog 7: {blogs[6]['title']}")
print(f"Blog 8: {blogs[7]['title']}\n")

# Remove blogs at index 6 and 7 (blogs 7 & 8)
removed = []
removed.append(blogs.pop(7))  # Remove blog 8 first (higher index)
removed.append(blogs.pop(6))  # Then remove blog 7

print(f"Removed {len(removed)} duplicate blogs:")
for r in removed:
    print(f"  - {r['title']}")

# Update data
data['blogs'] = blogs

# Save
with open('frontend/public/data/blogs.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"\n✅ New blog count: {len(blogs)}")
print("Remaining blogs:")
for i, b in enumerate(blogs):
    print(f"  {i+1}. [{b['category']}] {b['title'][:60]}")
