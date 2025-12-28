#!/usr/bin/env python3
"""
Phase A Migration Script: Copy Static Blogs to S3
Migrates existing 11 blogs from frontend/public/data/blogs.json to S3
"""

import os
import sys
import json
import boto3
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from auto_blogger.publisher import S3BlogStorage

def migrate_static_blogs_to_s3():
    """One-time migration: frontend/public/data/blogs.json → S3 blogs/index.json"""
    
    print("🚀 Starting Phase A Migration: Static Blogs → S3")
    print("=" * 60)
    
    # 1. Read existing static blogs
    frontend_blogs_path = Path(__file__).parent.parent / "frontend" / "public" / "data" / "blogs.json"
    
    if not frontend_blogs_path.exists():
        print(f"❌ ERROR: {frontend_blogs_path} not found!")
        sys.exit(1)
    
    with open(frontend_blogs_path, 'r', encoding='utf-8') as f:
        static_data = json.load(f)
    
    # Handle both {blogs: [...]} and [...] formats
    blogs = static_data.get('blogs', []) if isinstance(static_data, dict) else static_data
    
    print(f"✅ Loaded {len(blogs)} static blogs from {frontend_blogs_path}")
    
    # 2. Initialize S3 storage
    s3_bucket = os.getenv("S3_BLOG_BUCKET", "althaf-blogs-storage")
    storage = S3BlogStorage(bucket_name=s3_bucket)
    
    # 3. Check if index.json already exists
    try:
        existing_index = storage.read_index()
        existing_count = len(existing_index.get('blogs', []))
        
        if existing_count > 0:
            print(f"⚠️  WARNING: S3 index.json already has {existing_count} blogs")
            response = input("Overwrite with static blogs? (yes/no): ")
            if response.lower() != 'yes':
                print("❌ Migration cancelled")
                return
    except Exception as e:
        print(f"📝 No existing index.json found (this is expected for first run)")
    
    # 4. Write to S3
    index_data = {"blogs": blogs}
    storage.write_index(index_data)
    
    print(f"✅ Migrated {len(blogs)} blogs to S3: s3://{s3_bucket}/blogs/index.json")
    print()
    print("📊 Migration Summary:")
    print(f"   - Source: {frontend_blogs_path}")
    print(f"   - Destination: s3://{s3_bucket}/blogs/index.json")
    print(f"   - Blog count: {len(blogs)}")
    print()
    print("🎯 Next Steps:")
    print("   1. Verify: aws s3 cp s3://althaf-blogs-storage/blogs/index.json -")
    print("   2. Test auto-blogger to generate new blog")
    print("   3. Verify new blog appears in index.json")
    print()
    print("✅ Phase A Migration Complete!")

if __name__ == "__main__":
    migrate_static_blogs_to_s3()
