#!/usr/bin/env python3
import json

with open('frontend/public/data/blogs.json', 'r', encoding='utf-8') as f:
    blogs = json.load(f)['blogs']

content = blogs[0]['content']

print("Finding all # symbols in Blog 1...")
print("="*70)

lines_with_hash = []
for i, line in enumerate(content.split('\n')):
    if '#' in line:
        lines_with_hash.append((i+1, line))

print(f"Found {len(lines_with_hash)} lines with # symbols\n")
print("First 15 occurrences:")
print("-"*70)
for line_num, line in lines_with_hash[:15]:
    print(f"Line {line_num}: {line[:75]}")

