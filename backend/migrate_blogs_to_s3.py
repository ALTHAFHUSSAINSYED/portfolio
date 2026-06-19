#!/usr/bin/env python3
"""
Blog Migration Script: Upload Missing Individual Post Files
Uploads each blog's full content to S3 blogs/posts/ directory
Smart: Only uploads files that don't already exist
Timeout: 5 minutes maximum
"""

import os
import sys
import json
import boto3
import signal
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from auto_blogger.publisher import S3BlogStorage

class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("Migration exceeded 5 minute timeout!")

def migrate_individual_posts_to_s3():
    """Upload individual blog post files that are missing from S3"""
    
    print("🚀 Starting Blog Post File Migration to S3")
    print("=" * 60)
    print("⏱️  Timeout: 5 minutes")
    print()
    
    # Set 5 minute timeout
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(300)  # 300 seconds = 5 minutes
    
    try:
        # 1. Read existing static blogs
        frontend_blogs_path = Path(__file__).parent.parent / "frontend" / "public" / "data" / "blogs.json"
        
        if not frontend_blogs_path.exists():
            print(f"❌ ERROR: {frontend_blogs_path} not found!")
            sys.exit(1)
        
        with open(frontend_blogs_path, 'r', encoding='utf-8') as f:
            static_data = json.load(f)
        
        blogs = static_data.get('blogs', []) if isinstance(static_data, dict) else static_data
        
        print(f"✅ Loaded {len(blogs)} blogs from {frontend_blogs_path}")
        print()
        
        # 2. Initialize S3 storage
        s3_bucket = os.getenv("S3_BLOG_BUCKET", "althaf-blogs-storage")
        storage = S3BlogStorage(bucket_name=s3_bucket)
        
        # 3. Check which files already exist
        print("🔍 Checking existing files in S3...")
        s3_client = boto3.client('s3')
        existing_files = set()
        
        try:
            response = s3_client.list_objects_v2(
                Bucket=s3_bucket,
                Prefix='blogs/posts/'
            )
            for obj in response.get('Contents', []):
                if obj['Key'].endswith('.json'):
                    # Extract blog_id from filename
                    filename = obj['Key'].split('/')[-1]
                    blog_id = filename.replace('.json', '')
                    existing_files.add(blog_id)
        except Exception as e:
            print(f"⚠️  Could not list existing files: {e}")
        
        print(f"📊 Found {len(existing_files)} existing post files in S3")
        print()
        
        # 4. Upload missing individual post files
        uploaded = 0
        skipped = 0
        failed = 0
        
        for blog in blogs:
            blog_id = blog.get('id')
            
            if not blog_id:
                print(f"⚠️  Skipping blog without ID: {blog.get('title', 'Unknown')}")
                failed += 1
                continue
            
            # Check if file already exists
            if blog_id in existing_files:
                print(f"⏭️  Skipping {blog_id} (already exists)")
                skipped += 1
                continue
            
            # Upload individual post file
            try:
                print(f"📤 Uploading: {blog_id}...")
                storage.upload_post(blog_id, blog)
                uploaded += 1
                print(f"   ✅ Uploaded: blogs/posts/{blog_id}.json")
            except Exception as e:
                print(f"   ❌ Failed: {e}")
                failed += 1
        
        # 5. Cancel timeout alarm
        signal.alarm(0)
        
        # 6. Summary
        print()
        print("=" * 60)
        print("📊 Migration Summary:")
        print(f"   ✅ Uploaded: {uploaded} files")
        print(f"   ⏭️  Skipped:  {skipped} files (already exist)")
        print(f"   ❌ Failed:   {failed} files")
        print(f"   📍 Location: s3://{s3_bucket}/blogs/posts/")
        print()
        
        if uploaded > 0:
            print("🎉 Migration Complete! All blog detail pages should now work.")
        elif skipped == len(blogs):
            print("✅ All files already exist. No migration needed.")
        else:
            print("⚠️  Some files failed. Check errors above.")
        
        print()
        print("🔗 Test the blogs:")
        print("   https://althafportfolio.site/blogs")
        
    except TimeoutError as e:
        print()
        print("=" * 60)
        print(f"⏱️  TIMEOUT: {e}")
        print("Migration stopped after 5 minutes.")
        print("You may need to run again to complete remaining uploads.")
        sys.exit(1)
    except Exception as e:
        signal.alarm(0)  # Cancel timeout
        print()
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    migrate_individual_posts_to_s3()

