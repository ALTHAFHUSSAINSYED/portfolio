import boto3
import json
import os

# Config
BUCKET = "althaf-blogs-storage"
INDEX_KEY = "blogs/index.json"
POSTS_PREFIX = "blogs/posts/"

def prune_index():
    print("🔍 Connectng to S3...")
    s3 = boto3.client('s3')
    
    # 1. Fetch Index
    try:
        print(f"   Fetching {INDEX_KEY}...")
        resp = s3.get_object(Bucket=BUCKET, Key=INDEX_KEY)
        index_data = json.loads(resp['Body'].read())
        initial_count = len(index_data.get('blogs', []))
        print(f"   Index contains {initial_count} blogs.")
    except Exception as e:
        print(f"❌ Failed to fetch index: {e}")
        return

    # 2. List Actual Post Files
    try:
        print(f"   Listing objects in {POSTS_PREFIX}...")
        paginator = s3.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=BUCKET, Prefix=POSTS_PREFIX)
        
        actual_files = set()
        for page in pages:
            if 'Contents' in page:
                for obj in page['Contents']:
                    # Extract ID from filename: blogs/posts/ID.json -> ID
                    key = obj['Key']
                    if key.endswith('.json'):
                        filename = key.split('/')[-1]
                        blog_id = filename.replace('.json', '')
                        actual_files.add(blog_id)
        
        print(f"   Found {len(actual_files)} actual post files in S3.")
        
    except Exception as e:
        print(f"❌ Failed to list objects: {e}")
        return

    # 3. Identify & Prune Ghosts
    valid_blogs = []
    ghosts = []
    
    for blog in index_data.get('blogs', []):
        bid = blog.get('id')
        if bid in actual_files:
            valid_blogs.append(blog)
        else:
            ghosts.append(bid)
            
    # 4. Report & Update
    if ghosts:
        print(f"⚠️ Found {len(ghosts)} GHOST entries in index (Missing files):")
        for g in ghosts:
            print(f"   - {g}")
            
        index_data['blogs'] = valid_blogs
        
        # Determine strict or recent sort if needed, but for now just preserving order of valid ones
        # Sort by date just to be clean
        index_data['blogs'].sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        print(f"💾 Updating index.json (Removing {len(ghosts)} items)...")
        
        s3.put_object(
            Bucket=BUCKET,
            Key=INDEX_KEY,
            Body=json.dumps(index_data, indent=2),
            ContentType='application/json'
        )
        print("✅ Index Pruned Successfully!")
    else:
        print("✅ Index is already clean. No ghosts found.")

if __name__ == "__main__":
    prune_index()
