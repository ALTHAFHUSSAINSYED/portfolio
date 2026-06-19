import boto3
import chromadb
import json
import os
import logging

# Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ChromaDebug")

# 1. Check S3 Count
s3 = boto3.client('s3')
bucket = 'althaf-blogs-storage'
try:
    resp = s3.get_object(Bucket=bucket, Key='blogs/index.json')
    index = json.loads(resp['Body'].read())
    s3_blogs = index.get('blogs', [])
    print(f"📦 S3 Total Blogs: {len(s3_blogs)}")
    s3_ids = [b['id'] for b in s3_blogs]
    print(f"   Latest 3 in S3: {s3_ids[:3]}")
except Exception as e:
    print(f"❌ S3 Error: {e}")
    s3_ids = []

# 2. Check ChromaDB Count
try:
    # Try cloud first
    chroma_api_key = os.getenv("CHROMA_API_KEY")
    chroma_tenant = os.getenv("CHROMA_TENANT_ID", "default_tenant")
    chroma_db = os.getenv("CHROMA_DATABASE", "default_database")
    
    if chroma_api_key:
        print("🔍 Connecting to Chroma Cloud...")
        client = chromadb.HttpClient(
            ssl=True,
            host='api.trychroma.com',
            tenant=chroma_tenant,
            database=chroma_db,
            headers={
                "x-chroma-token": chroma_api_key,
                "x-tenant": chroma_tenant,
                "x-database": chroma_db
            }
        )
    else:
        print("🔍 Connecting to Local Chroma...")
        client = chromadb.PersistentClient(path="./chroma_db")

    collection = client.get_or_create_collection("Blogs_data")
    count = collection.count()
    print(f"🧠 ChromaDB Total Blogs: {count}")
    
    # Get IDs
    if count > 0:
        results = collection.get(limit=100) # Get all IDs
        chroma_ids = results['ids']
        missing = [bid for bid in s3_ids if bid not in chroma_ids]
        print(f"⚠️ Missing from Chroma ({len(missing)}): {missing}")
    else:
        print("⚠️ Chroma is EMPTY.")

except Exception as e:
    print(f"❌ Chroma Error: {e}")
