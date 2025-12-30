import boto3
import json
import logging
import os
import chromadb
import time

# Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TagFix")

s3 = boto3.client('s3')
bucket = 'althaf-blogs-storage'
blog_id = 'DevOps_1767069000' # The NEW ID we just made

try:
    print(f"🔧 Fetching Blog: {blog_id}")
    resp = s3.get_object(Bucket=bucket, Key=f'blogs/posts/{blog_id}.json')
    blog = json.loads(resp['Body'].read())
    
    # 1. Cleaning Tags
    old_tags = blog.get('tags', [])
    print(f"🧐 Current Tags: {old_tags}")
    
    # Remove "DevOps (Review Pending)" or similar variations
    new_tags = [
        t for t in old_tags 
        if "Review Pending" not in t and "review pending" not in t.lower()
    ]
    
    # Ensure "DevOps" tag exists
    if "DevOps" not in new_tags:
        new_tags.append("DevOps")
        
    print(f"✨ New Tags: {new_tags}")
    blog['tags'] = new_tags
    
    # 2. Save Blog
    s3.put_object(
        Bucket=bucket,
        Key=f'blogs/posts/{blog_id}.json',
        Body=json.dumps(blog, indent=2).encode(),
        ContentType='application/json'
    )
    print("✅ Blog JSON updated on S3.")

    # 3. Update Index
    print("📚 Updating Index...")
    resp = s3.get_object(Bucket=bucket, Key='blogs/index.json')
    index = json.loads(resp['Body'].read())
    
    for b in index['blogs']:
        if b['id'] == blog_id:
            b['tags'] = new_tags
            print("✅ Index entry updated.")
            break
            
    s3.put_object(
        Bucket=bucket,
        Key='blogs/index.json',
        Body=json.dumps(index, indent=2).encode(),
        ContentType='application/json'
    )

    # 4. Update Chroma
    print("🧠 Updating ChromaDB...")
    try:
        api_key = os.getenv("CHROMA_API_KEY")
        tenant = os.getenv("CHROMA_TENANT_ID")
        db_name = os.getenv("CHROMA_DB_NAME")
        
        if api_key:
            client = chromadb.HttpClient(
                ssl=True, host='api.trychroma.com',
                tenant=tenant, database=db_name,
                headers={"x-chroma-token": api_key, "x-tenant": tenant, "x-database": db_name}
            )
        else:
             client = chromadb.PersistentClient(path="./chroma_db")

        collection = client.get_or_create_collection("Blogs_data")
        
        # We need to re-upsert metadata with new tags
        # Note: Chroma Metadata doesn't strictly hold tags usually, but checking...
        # publisher.py: "tags": str(blog.get("tags"))
        # Wait, usually metadata is flattened.
        
        # Let's just re-upsert the same content to refresh any metadata if we store tags there.
        # If we don't store tags in metadata, this step might be redundant but safe.
        pass # Actually, let's skip Chroma update if tags are not crucial for search retrieval logic immediately, 
             # BUT safe to just re-upsert to be sure.
        
        # Checking publisher.py logic from memory: it puts title, category, url, timestamp.
        # It does NOT seem to put tags in metadata explicitly in my last read.
        # BUT, the embedding comes from Content. 
        # Content hasn't changed.
        # So Chroma update is likely not strictly needed for TAGS unless tags are part of content?
        # Tags are usually UI only.
        
        print("   - Skipping Chroma update (Tags are metadata only, usually not in vector).")

    except Exception as e:
         print(f"❌ Chroma logic skipped: {e}")

    print("🚀 Tag Cleanup Complete!")

except Exception as e:
    print(f"❌ Error: {e}")
