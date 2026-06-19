#!/usr/bin/env python3
"""
Fix ChromaDB embedding for migrated blog using correct Gemini model
"""
import os
import sys
import boto3
import json
import google.generativeai as genai
import chromadb
from chromadb.config import Settings

def main():
    print("=" * 80)
    print("CHROMADB EMBEDDING FIX - Using Gemini text-embedding-004")
    print("=" * 80)
    
    # Configure Gemini
    gemini_key = os.getenv('GEMINI_API_KEY')
    if not gemini_key:
        print("❌ GEMINI_API_KEY not found")
        return 1
    
    genai.configure(api_key=gemini_key)
    print("✅ Gemini configured")
    
    # Connect to S3
    s3 = boto3.client('s3')
    blog_id = 'Low-Code-No-Code_1767673800'
    key = f'blogs/posts/{blog_id}.json'
    
    print(f"\n1. Downloading blog from S3: {key}")
    try:
        response = s3.get_object(Bucket='althaf-blogs-storage', Key=key)
        blog_data = json.loads(response['Body'].read())
        print(f"   ✅ Title: {blog_data['title'][:70]}...")
    except Exception as e:
        print(f"   ❌ Failed to download: {e}")
        return 1
    
    # Generate Gemini embedding
    print("\n2. Generating Gemini embedding (768 dimensions)...")
    content = f"{blog_data['title']}\n{blog_data.get('summary', '')}\n{blog_data.get('content', '')[:1000]}"
    try:
        result = genai.embed_content(
            model='models/text-embedding-004',
            content=content,
            task_type='retrieval_document'
        )
        embedding = result['embedding']
        print(f"   ✅ Generated embedding: {len(embedding)} dimensions")
    except Exception as e:
        print(f"   ❌ Failed to generate embedding: {e}")
        return 1
    
    # Connect to ChromaDB
    print("\n3. Connecting to ChromaDB Cloud...")
    try:
        chroma_client = chromadb.CloudClient(
            tenant=os.getenv('CHROMA_TENANT'),
            database=os.getenv('CHROMA_DATABASE'),
            api_key=os.getenv('CHROMA_API_KEY'),
            settings=Settings(allow_reset=True, anonymized_telemetry=False)
        )
        collection = chroma_client.get_collection('portfolio_master')
        print(f"   ✅ Connected to collection: portfolio_master")
    except Exception as e:
        print(f"   ❌ Failed to connect: {e}")
        return 1
    
    # Delete old blog ID
    print("\n4. Deleting old blog ID from ChromaDB...")
    old_id = 'Low-Code/No-Code_1767673800'
    try:
        collection.delete(ids=[old_id])
        print(f"   ✅ Deleted: {old_id}")
    except Exception as e:
        print(f"   ⚠️  Old ID not found (already deleted): {str(e)[:100]}")
    
    # Add new blog with correct embedding
    print("\n5. Adding new blog to ChromaDB...")
    metadata = {
        'type': 'blogs',
        'category': blog_data.get('category', 'Low-Code/No-Code'),
        'title': blog_data['title'],
        'blog_id': blog_id,
        'created_at': blog_data.get('created_at', '2026-01-06'),
        'metadata_category': 'blogs'
    }
    
    try:
        collection.add(
            ids=[blog_id],
            embeddings=[embedding],
            documents=[content],
            metadatas=[metadata]
        )
        print(f"   ✅ Added: {blog_id}")
        print(f"   Title: {blog_data['title'][:70]}...")
        print(f"   Category: {metadata['category']}")
    except Exception as e:
        print(f"   ❌ Failed to add: {e}")
        return 1
    
    print("\n" + "=" * 80)
    print("✅ CHROMADB EMBEDDING FIXED SUCCESSFULLY")
    print("=" * 80)
    return 0

if __name__ == '__main__':
    sys.exit(main())
