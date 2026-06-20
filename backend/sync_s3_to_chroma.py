import boto3
import chromadb
import json
import os
import logging
from google import genai
from google.genai import types
import time
from datetime import datetime

# Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ChromaSync")

# Configuration
s3 = boto3.client('s3')
bucket = 'althaf-blogs-storage'

# Gemini Setup for Embeddings
try:
    genai_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
except Exception as e:
    logger.warning(f"Failed to initialize Gemini Client for sync: {e}")
    genai_client = None

def get_embedding(text):
    try:
        if not genai_client:
            return None
        result = genai_client.models.embed_content(
            model="gemini-embedding-001",
            contents=text,
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_DOCUMENT",
                output_dimensionality=768
            )
        )
        return result.embeddings[0].values
    except Exception as e:
        logger.error(f"Embedding error: {e}")
        return None

def sync():
    print("🚀 Starting S3 -> ChromaDB Sync...")

    # 1. Get S3 Index
    try:
        resp = s3.get_object(Bucket=bucket, Key='blogs/index.json')
        index = json.loads(resp['Body'].read())
        s3_blogs = index.get('blogs', [])
        s3_ids = {b['id'] for b in s3_blogs}
        print(f"📦 Found {len(s3_blogs)} blogs in S3.")
    except Exception as e:
        print(f"❌ Failed to read S3 index: {e}")
        return

    # 2. Connect to Chroma
    try:
        api_key = os.getenv("CHROMA_API_KEY")
        tenant = os.getenv("CHROMA_TENANT_ID")
        db_name = os.getenv("CHROMA_DB_NAME") # Usage of correct ENV var
        
        if api_key:
            if not db_name:
                db_name = "Development"
            print(f"🔌 Connecting to Chroma Cloud (DB: {db_name})...")
            client = chromadb.CloudClient(
                api_key=api_key,
                tenant=tenant,
                database=db_name
            )
        else:
            print("🔌 Connecting to Local Chroma...")
            client = chromadb.PersistentClient(path="./chroma_db")
            
        collection = client.get_or_create_collection("Blogs_data")
        
        # Get existing IDs
        chroma_count = collection.count()
        existing_ids = set()
        if chroma_count > 0:
            existing = collection.get(limit=chroma_count + 100) # Get all
            existing_ids = set(existing['ids'])
            
        print(f"🧠 Found {chroma_count} blogs in Chroma.")
        
        # 3. Identify Missing
        missing_ids = s3_ids - existing_ids
        print(f"⚠️ Missing {len(missing_ids)} blogs in Chroma.")
        
        if not missing_ids:
            print("✅ All synced!")
            return

        # 4. Sync Missing
        print("🔄 Syncing missing blogs...")
        success_count = 0
        
        for blog_id in missing_ids:
            try:
                print(f"   Processing: {blog_id}")
                # Fetch full content from S3
                resp = s3.get_object(Bucket=bucket, Key=f'blogs/posts/{blog_id}.json')
                blog_data = json.loads(resp['Body'].read())
                
                content = blog_data.get('content')
                if not content:
                    print(f"   ❌ Skiping {blog_id} (No content in JSON)")
                    continue
                
                # Generate embedding
                embed = get_embedding(content)
                if not embed:
                    print(f"   ❌ Skipping {blog_id} (Embedding failed)")
                    continue
                
                # Upsert
                collection.upsert(
                    ids=[blog_id],
                    documents=[content],
                    metadatas=[{
                        "title": blog_data.get('title', 'Unknown'),
                        "category": blog_data.get('category', 'Unknown'),
                        "url": f"https://althafportfolio.site/blogs/{blog_id}",
                        "timestamp": str(int(time.time()))
                    }],
                    embeddings=[embed]
                )
                print(f"   ✅ Synced: {blog_id}")
                success_count += 1
                time.sleep(1) # Rate limit safety
                
            except Exception as e:
                print(f"   ❌ Failed to sync {blog_id}: {e}")
        
        print(f"🎉 Sync Complete. Added {success_count} blogs.")

    except Exception as e:
        print(f"❌ Chroma Connection Error: {e}")

if __name__ == "__main__":
    sync()
