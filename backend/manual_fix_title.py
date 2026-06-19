import boto3
import json
import os
from datetime import datetime

# Config
BLOG_ID = "DevOps_1767241800"
NEW_TITLE = "DevOps 2026: AI-Driven Pipelines & Self-Healing Infrastructure"
BUCKET = "althaf-blogs-storage"

def fix_title():
    print(f"🔧 Fixing title for blog: {BLOG_ID}")
    s3 = boto3.client('s3')
    
    # 1. Update Blog Post File
    key_post = f"blogs/posts/{BLOG_ID}.json"
    try:
        print(f"   Fetching {key_post}...")
        resp = s3.get_object(Bucket=BUCKET, Key=key_post)
        blog_data = json.loads(resp['Body'].read())
        
        old_title = blog_data.get('title')
        print(f"   Old Title: {old_title}")
        
        # Update title
        blog_data['title'] = NEW_TITLE
        
        # Upload back
        s3.put_object(
            Bucket=BUCKET,
            Key=key_post,
            Body=json.dumps(blog_data, indent=2),
            ContentType='application/json'
        )
        print(f"✅ Updated post file with new title: {NEW_TITLE}")
        
    except Exception as e:
        print(f"❌ Failed to update post file: {e}")
        return

    # 2. Update Index File
    key_index = "blogs/index.json"
    try:
        print(f"   Fetching {key_index}...")
        resp = s3.get_object(Bucket=BUCKET, Key=key_index)
        index_data = json.loads(resp['Body'].read())
        
        updated = False
        for blog in index_data['blogs']:
            if blog['id'] == BLOG_ID:
                blog['title'] = NEW_TITLE
                updated = True
                break
        
        if updated:
            s3.put_object(
                Bucket=BUCKET,
                Key=key_index,
                Body=json.dumps(index_data, indent=2),
                ContentType='application/json'
            )
            print(f"✅ Updated index file with new title")
        else:
            print(f"⚠️ Blog ID not found in index")
            
    except Exception as e:
        print(f"❌ Failed to update index file: {e}")

if __name__ == "__main__":
    fix_title()
