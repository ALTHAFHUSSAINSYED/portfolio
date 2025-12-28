import json

with open('frontend/public/data/blogs.json', 'r', encoding='utf-8') as f:
    blogs = json.load(f)['blogs']

print(f"Current blog count: {len(blogs)}")
print("\n" + "="*70)
print("All blogs:")
print("="*70)
for i, blog in enumerate(blogs):
    print(f"{i+1}. {blog['title']}")
    print(f"   Content: {len(blog.get('content', ''))} chars")
    print()
