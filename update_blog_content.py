import json

# Read the elite-tier blog content
with open('backend/generated_blog_sample_1.md', 'r', encoding='utf-8') as f:
    elite_content = f.read()

# Read current blogs.json
with open('frontend/public/data/blogs.json', 'r', encoding='utf-8') as f:
    blogs_data = json.load(f)

# Find and update the Low-Code blog
blogs = blogs_data['blogs'] if isinstance(blogs_data, dict) else blogs_data

for blog in blogs:
    if blog['id'] == 'Low-Code_No-Code_1759057460':
        # Update with elite-tier content
        blog['content'] = elite_content
        print(f"✅ Updated blog: {blog['title']}")
        print(f"   Content length: {len(elite_content)} characters")
        break

# Write back to blogs.json
with open('frontend/public/data/blogs.json', 'w', encoding='utf-8') as f:
    if isinstance(blogs_data, dict):
        json.dump(blogs_data, f, indent=2, ensure_ascii=False)
    else:
        json.dump(blogs, f, indent=2, ensure_ascii=False)

print("✅ blogs.json updated successfully!")
