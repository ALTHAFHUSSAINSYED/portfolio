"""
Fix published_date metadata for existing blogs in ChromaDB.
Reads from S3, extracts created_at (not createdAt), updates ChromaDB.
"""
import os
import boto3
import json
import chromadb
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def main():
    print("🔧 Fixing published_date in ChromaDB for existing blogs...")
    
    # Connect to S3
    s3 = boto3.client('s3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name='us-east-1'
    )
    
    # Connect to ChromaDB
    client = chromadb.CloudClient(
        api_key=os.getenv('CHROMA_API_KEY'),
        tenant=os.getenv('CHROMA_TENANT'),
        database=os.getenv('CHROMA_DATABASE')
    )
    
    collection = client.get_collection('portfolio_master')
    
    # Get all blog files from S3
    response = s3.list_objects_v2(Bucket='althaf-blogs-storage', Prefix='blogs/posts/')
    blog_files = [obj['Key'] for obj in response.get('Contents', []) if obj['Key'].endswith('.json')]
    
    print(f"Found {len(blog_files)} blog files in S3")
    
    fixed_count = 0
    skipped_count = 0
    
    for blog_key in blog_files:
        try:
            # Read blog from S3
            response = s3.get_object(Bucket='althaf-blogs-storage', Key=blog_key)
            blog = json.loads(response['Body'].read())
            
            blog_id = blog.get('id', blog_key.split('/')[-1].replace('.json', ''))
            created_at = blog.get('created_at', '')
            
            if not created_at:
                print(f"⚠️  {blog_id}: No created_at field, skipping")
                skipped_count += 1
                continue
            
            # Extract published_date (YYYY-MM-DD)
            published_date = created_at[:10] if len(created_at) >= 10 else ''
            
            if not published_date:
                print(f"⚠️  {blog_id}: Invalid created_at format: {created_at}")
                skipped_count += 1
                continue
            
            # Check if blog exists in ChromaDB
            try:
                existing = collection.get(ids=[blog_id])
                if not existing or not existing['ids']:
                    print(f"⚠️  {blog_id}: Not found in ChromaDB, skipping")
                    skipped_count += 1
                    continue
                
                # Get current metadata
                current_meta = existing['metadatas'][0]
                current_pub_date = current_meta.get('published_date', 'N/A')
                
                if current_pub_date == published_date:
                    print(f"✅ {blog_id}: Already correct ({published_date})")
                    skipped_count += 1
                    continue
                
                # Update metadata
                updated_meta = current_meta.copy()
                updated_meta['published_date'] = published_date
                
                # Update in ChromaDB
                collection.update(
                    ids=[blog_id],
                    metadatas=[updated_meta]
                )
                
                print(f"✅ {blog_id}: Fixed {current_pub_date} → {published_date}")
                fixed_count += 1
                
            except Exception as e:
                print(f"❌ {blog_id}: ChromaDB error - {e}")
                skipped_count += 1
                continue
            
        except Exception as e:
            print(f"❌ {blog_key}: S3 error - {e}")
            skipped_count += 1
            continue
    
    print(f"\n✅ Fixed: {fixed_count}")
    print(f"⚠️  Skipped: {skipped_count}")
    print(f"📊 Total: {len(blog_files)}")

if __name__ == "__main__":
    main()
