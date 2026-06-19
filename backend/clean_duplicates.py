#!/usr/bin/env python3
"""
Quick blog rewrite script:
1. Delete duplicate blogs (7, 8) to get to 9 total
2. Create placeholder for rewritten blogs
"""

import json
from pathlib import Path

# Read
blogs_file = Path('frontend/public/data/blogs.json')
with open(blogs_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

blogs = data['blogs']
print(f"Starting with {len(blogs)} blogs\n")

# Show all current blogs
for i, b in enumerate(blogs):
    print(f"{i+1}. [{b['category']}] {b['title'][:60]}")

# Identify duplicates by checking titles
titles_seen = {}
duplicates = []

for i, blog in enumerate(blogs):
    title_key = blog['title'][:30].lower()  # Use first 30 chars as key
    if title_key in titles_seen:
        duplicates.append(i)
        print(f"\n❌ Duplicate found: Blog {i+1} is similar to Blog {titles_seen[title_key]+1}")
    else:
        titles_seen[title_key] = i

print(f"\nFound {len(duplicates)} duplicates to remove: {[d+1 for d in duplicates]}")

# Remove duplicates (reverse order to keep indices valid)
for idx in sorted(duplicates, reverse=True):
    removed = blogs.pop(idx)
    print(f"Removed: {removed['title'][:60]}")

# Save
data['blogs'] = blogs
with open(blogs_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"\n✅ Final count: {len(blogs)} blogs")
print("\nRemaining blogs:")
for i, b in enumerate(blogs):
    print(f"  {i+1}. [{b['category']}] {b['title'][:60]}")
