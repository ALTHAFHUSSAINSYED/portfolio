#!/usr/bin/env python3
import json
import re

with open('frontend/public/data/blogs.json', 'r', encoding='utf-8') as f:
    blogs = json.load(f)['blogs']

print("="*70)
print("CHECKING FOR MARKDOWN HEADERS (# at start of line)")
print("="*70)

all_clean = True

for i, blog in enumerate(blogs):
    content = blog['content']
    
    # Find lines that START with # (markdown headers)
    markdown_headers = []
    for line_num, line in enumerate(content.split('\n')):
        stripped = line.lstrip()
        if stripped.startswith('#') and len(stripped) > 1 and stripped[1] == ' ':
            # This is a markdown header like "# Title" or "## Section"
            markdown_headers.append((line_num+1, line[:70]))
    
    if markdown_headers:
        print(f"\n❌ Blog {i+1}: {blog['title'][:50]}")
        print(f"   Found {len(markdown_headers)} markdown headers:")
        for line_num, line in markdown_headers[:5]:
            print(f"   Line {line_num}: {line}")
        all_clean = False
    else:
        print(f"✅ Blog {i+1}: {blog['title'][:55]} - NO markdown headers")

print("\n" + "="*70)
if all_clean:
    print("✅✅✅ ALL BLOGS ARE CLEAN - No markdown headers found!")
    print("\nNote: # symbols like 'Pillar #1' are NORMAL text, not markdown")
else:
    print("❌ Some blogs still have markdown headers")
print("="*70)
