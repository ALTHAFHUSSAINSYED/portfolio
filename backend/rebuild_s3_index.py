#!/usr/bin/env python3
"""
Rebuild S3 blog index to match actual blog files
Scans S3 bucket for actual blog JSON files and rebuilds index.json
"""

import os
import sys
import json
import boto3
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env.local'))

def rebuild_s3_index():
    """Rebuild S3 index.json to match actual blog files"""
    
    bucket_name = os.getenv('S3_BLOG_BUCKET', 'althaf-blogs-storage')
    
    try:
        # Initialize S3 client
        s3 = boto3.client('s3')
        
        print(f"✅ Connected to S3 bucket: {bucket_name}")
        
        # List all blog files in S3
        prefix = 'blogs/posts/'
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        
        if 'Contents' not in response:
            print("❌ No blog files found in S3")
            return
        
        blog_files = [obj['Key'] for obj in response['Contents'] if obj['Key'].endswith('.json')]
        print(f"🔍 Found {len(blog_files)} blog files in S3:")
        
        # Load each blog file and build index
        blogs = []
        for file_key in blog_files:
            try:
                # Download blog file
                obj = s3.get_object(Bucket=bucket_name, Key=file_key)
                blog_data = json.loads(obj['Body'].read().decode('utf-8'))
                
                # Extract blog ID from filename
                blog_id = file_key.split('/')[-1].replace('.json', '')
                
                # Add to index
                index_entry = {
                    'id': blog_id,
                    'title': blog_data.get('title', 'Untitled'),
                    'category': blog_data.get('category', 'Uncategorized'),
                    'summary': blog_data.get('summary', '')[:200],  # First 200 chars
                    'created_at': blog_data.get('created_at', datetime.now().isoformat()),
                    'tags': blog_data.get('tags', []),
                    'author': blog_data.get('author', 'Althaf Hussain Syed')
                }
                
                blogs.append(index_entry)
                print(f"  ✅ {blog_id} | {index_entry['title']}")
                
            except Exception as e:
                print(f"  ❌ Error loading {file_key}: {e}")
        
        # Sort by created_at (newest first)
        blogs.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        # Create new index
        new_index = {
            'blogs': blogs,
            'total': len(blogs),
            'last_updated': datetime.now().isoformat()
        }
        
        print(f"\n📊 New index contains {len(blogs)} blogs")
        
        # Upload new index to S3
        index_key = 'blogs/index.json'
        s3.put_object(
            Bucket=bucket_name,
            Key=index_key,
            Body=json.dumps(new_index, indent=2),
            ContentType='application/json'
        )
        
        print(f"✅ Uploaded new index to S3: {index_key}")
        print("\n🎉 S3 index rebuilt successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    rebuild_s3_index()
