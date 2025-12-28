#!/usr/bin/env python3
import json

# Read blogs
with open('frontend/public/data/blogs.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

blog = data['blogs'][0]
content = blog['content']

print("="*70)
print("VERIFICATION: Blog Content Format Check")
print("="*70)
print(f"\nBlog Title: {blog['title'][:60]}")
print(f"Content Length: {len(content)} chars\n")

print("First 600 characters:")
print("-"*70)
print(content[:600])
print("-"*70)

print("\n\nMarkdown Symbol Check:")
print(f"  - Has # symbols: {'YES ❌' if '#' in content else 'NO ✅'}")
print(f"  - Has ** markers: {'YES ❌' if '**' in content else 'NO ✅'}")
print(f"  - Has __ markers: {'YES ❌' if '__' in content else 'NO ✅'}")
print(f"  - Has --- lines: {'YES ❌' if '---' in content[:1000] else 'NO ✅'}")

print("\n\nSpacing Check:")
lines = content.split('\n')
max_consecutive_empty = 0
current_empty = 0
for line in lines:
    if line.strip() == '':
        current_empty += 1
        max_consecutive_empty = max(max_consecutive_empty, current_empty)
    else:
        current_empty = 0

print(f"  - Max consecutive empty lines: {max_consecutive_empty} {'✅' if max_consecutive_empty <= 2 else '❌'}")
print(f"  - Total lines: {len(lines)}")

print("\n" + "="*70)
print("FORMAT VERIFICATION COMPLETE")
print("="*70)
