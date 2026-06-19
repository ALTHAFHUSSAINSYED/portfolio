#!/usr/bin/env python3
"""
Fix blog URLs with slashes in IDs by renaming them to use hyphens instead.
This script:
1. Finds blogs with slashes in their IDs in S3
2. Renames them to use hyphens (URL-safe format)
3. Updates index.json
4. Updates ChromaDB embeddings
"""

import boto3
import json
import os
from dotenv import load_dotenv
import chromadb
from datetime import datetime

load_dotenv()

S3_BUCKET = os.getenv('S3_BLOG_BUCKET', 'althaf-blogs-storage')
CHROMA_API_KEY = os.getenv('CHROMA_API_KEY')
CHROMA_TENANT = os.getenv('CHROMA_TENANT') or os.getenv('CHROMA_TENANT_ID')
CHROMA_DATABASE = os.getenv('CHROMA_DATABASE') or os.getenv('CHROMA_DB_NAME')

def fix_blog_urls():
    """Fix all blogs with slashes in their IDs"""
    s3 = boto3.client('s3')
    
    print("=" * 80)
    print("BLOG URL FIXER - Migrating slashes to hyphens in blog IDs")
    print("=" * 80)
    
    # 1. Download index.json
    print("\n1. Downloading index.json from S3...")
    try:
        response = s3.get_object(Bucket=S3_BUCKET, Key='blogs/index.json')
        index_data = json.loads(response['Body'].read().decode('utf-8'))
        blogs = index_data.get('blogs', [])
        print(f"   ✅ Found {len(blogs)} blogs in index")
    except Exception as e:
        print(f"   ❌ Error downloading index.json: {e}")
        return
    
    # 2. Find blogs with slashes
    blogs_to_fix = [b for b in blogs if '/' in b.get('id', '')]
    
    if not blogs_to_fix:
        print("\n✅ No blogs with slashes found. All URLs are correct!")
        return
    
    print(f"\n2. Found {len(blogs_to_fix)} blogs with slashes to fix:")
    for blog in blogs_to_fix:
        print(f"   - {blog['id']}")
    
    # 3. Fix each blog
    fixed_blogs = []
    for blog in blogs_to_fix:
        old_id = blog['id']
        # Replace slashes with hyphens
        new_id = old_id.replace('/', '-')
        
        print(f"\n3. Fixing blog: {old_id} → {new_id}")
        
        try:
            # Download old blog content
            old_key = f"blogs/posts/{old_id}.json"
            try:
                response = s3.get_object(Bucket=S3_BUCKET, Key=old_key)
                blog_content = json.loads(response['Body'].read().decode('utf-8'))
            except:
                # Try alternate path
                old_key = f"blogs/{old_id}.json"
                response = s3.get_object(Bucket=S3_BUCKET, Key=old_key)
                blog_content = json.loads(response['Body'].read().decode('utf-8'))
            
            print(f"   ✅ Downloaded: {old_key}")
            
            # Update blog ID
            blog_content['id'] = new_id
            blog['id'] = new_id
            
            # Upload with new ID
            new_key = f"blogs/posts/{new_id}.json"
            s3.put_object(
                Bucket=S3_BUCKET,
                Key=new_key,
                Body=json.dumps(blog_content, ensure_ascii=False, indent=2),
                ContentType='application/json'
            )
            print(f"   ✅ Uploaded: {new_key}")
            
            # Delete old file
            s3.delete_object(Bucket=S3_BUCKET, Key=old_key)
            print(f"   ✅ Deleted: {old_key}")
            
            fixed_blogs.append({
                'old_id': old_id,
                'new_id': new_id,
                'title': blog.get('title', 'Unknown')
            })
            
        except Exception as e:
            print(f"   ❌ Error fixing {old_id}: {e}")
    
    # 4. Update index.json
    if fixed_blogs:
        print(f"\n4. Updating index.json with {len(fixed_blogs)} fixed blog IDs...")
        try:
            s3.put_object(
                Bucket=S3_BUCKET,
                Key='blogs/index.json',
                Body=json.dumps(index_data, ensure_ascii=False, indent=2),
                ContentType='application/json'
            )
            print("   ✅ index.json updated")
        except Exception as e:
            print(f"   ❌ Error updating index.json: {e}")
    
    # 5. Update ChromaDB
    if fixed_blogs and CHROMA_API_KEY:
        print("\n5. Updating ChromaDB embeddings...")
        try:
            chroma_client = chromadb.CloudClient(
                api_key=CHROMA_API_KEY,
                tenant=CHROMA_TENANT,
                database=CHROMA_DATABASE
            )
            
            collection = chroma_client.get_collection('portfolio_master')
            
            for fix in fixed_blogs:
                old_id = fix['old_id']
                new_id = fix['new_id']
                
                try:
                    # Get existing embedding
                    results = collection.get(ids=[old_id])
                    
                    if results['ids']:
                        # Delete old ID
                        collection.delete(ids=[old_id])
                        
                        # Re-add with new ID
                        collection.upsert(
                            ids=[new_id],
                            documents=results['documents'],
                            metadatas=results['metadatas']
                        )
                        print(f"   ✅ Updated ChromaDB: {old_id} → {new_id}")
                    else:
                        print(f"   ⚠️  Not found in ChromaDB: {old_id}")
                except Exception as e:
                    print(f"   ❌ ChromaDB error for {old_id}: {e}")
                    
        except Exception as e:
            print(f"   ❌ ChromaDB connection error: {e}")
    
    # 6. Summary
    print("\n" + "=" * 80)
    print("MIGRATION SUMMARY")
    print("=" * 80)
    for fix in fixed_blogs:
        print(f"✅ {fix['title']}")
        print(f"   OLD: /blogs/{fix['old_id']}")
        print(f"   NEW: /blogs/{fix['new_id']}")
        print()
    
    print(f"Total blogs fixed: {len(fixed_blogs)}")
    print("=" * 80)

if __name__ == "__main__":
    fix_blog_urls()
