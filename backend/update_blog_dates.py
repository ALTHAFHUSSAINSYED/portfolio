#!/usr/bin/env python3
"""
Update blog dates to start from December 12, 2024
Sequential day-by-day for all 11 blogs
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

# Read current blogs
blogs_file = Path(__file__).parent.parent / "frontend" / "public" / "data" / "blogs.json"
with open(blogs_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Update dates starting from Dec 12, 2024
start_date = datetime(2024, 12, 12)
blogs = data['blogs']

print(f"Updating {len(blogs)} blog dates...")
print(f"Starting from: {start_date.strftime('%Y-%m-%d')}\n")

for i, blog in enumerate(blogs):
    new_date = start_date + timedelta(days=i)
    old_date = blog.get('created_at', blog.get('date', 'Unknown'))
    blog['created_at'] = new_date.isoformat()
    if 'date' in blog:
        blog['date'] = new_date.strftime('%Y-%m-%d')
    
    print(f"{i+1}. {blog['title'][:50]}")
    print(f"   Old: {old_date}")
    print(f"   New: {new_date.strftime('%Y-%m-%d')}\n")

# Save updated file
with open(blogs_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print(f"✅ Updated {len(blogs)} blogs in {blogs_file}")
print(f"\nDate range: {start_date.strftime('%Y-%m-%d')} to {(start_date + timedelta(days=len(blogs)-1)).strftime('%Y-%m-%d')}")
