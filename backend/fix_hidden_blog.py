import boto3
import json

s3 = boto3.client('s3')
bucket = 'althaf-blogs-storage'
blog_id = 'DevOps_(Review_Pending)_1767069000'

print(f"🔧 Fixing Blog: {blog_id}")

# 1. Get the blog
resp = s3.get_object(Bucket=bucket, Key=f'blogs/posts/{blog_id}.json')
blog = json.loads(resp['Body'].read())

# 2. Fix Metadata
print(f"Old Category: {blog.get('category')}")
blog['category'] = 'DevOps'  # REMOVE (Review Pending)
blog['title'] = "DevOps - Technical Deep Dive" # Ensure clean title
print(f"New Category: {blog.get('category')}")

# 3. Save Blog back to S3
# Note: We keep the filename ID strictly to avoid breaking links if email went out,
# but internally it will now belong to "DevOps" category so it shows up.
s3.put_object(
    Bucket=bucket,
    Key=f'blogs/posts/{blog_id}.json',
    Body=json.dumps(blog, indent=2).encode(),
    ContentType='application/json'
)

# 4. Fix Index
print("📝 Updating Index...")
resp = s3.get_object(Bucket=bucket, Key='blogs/index.json')
index = json.loads(resp['Body'].read())

found = False
for b in index['blogs']:
    if b['id'] == blog_id:
        b['category'] = 'DevOps' # Fix here too
        b['title'] = blog['title']
        found = True
        print("✅ Found and fixed in index")
        break

if not found:
    print("⚠️ Blog not found in index! Adding it...")
    # Add it manually if missing
    new_entry = {
        "id": blog_id,
        "title": blog['title'],
        "summary": blog.get('summary', ''),
        "category": "DevOps",
        "tags": blog.get('tags', []),
        "published": True,
        "created_at": blog.get('created_at')
    }
    index['blogs'].insert(0, new_entry)

# Save Index
s3.put_object(
    Bucket=bucket,
    Key='blogs/index.json',
    Body=json.dumps(index, indent=2).encode(),
    ContentType='application/json'
)

print("✅ Fix Complete! Blog should now be visible in 'DevOps' tab.")
