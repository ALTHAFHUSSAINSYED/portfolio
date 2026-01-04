"""
Check if today's blog is in S3 index.json
"""

import boto3
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_s3_index():
    """Download and check S3 index.json for today's blog"""
    
    bucket = "althaf-blogs-storage"
    index_key = "blogs/index.json"
    today_blog_id = "Cloud_Computing_1767414600"
    
    try:
        s3 = boto3.client("s3")
        
        # Download index.json
        response = s3.get_object(Bucket=bucket, Key=index_key)
        index_data = json.loads(response['Body'].read().decode('utf-8'))
        
        blogs = index_data.get('blogs', [])
        logger.info(f"📊 S3 index.json contains {len(blogs)} blogs")
        
        # Check for today's blog
        found = False
        for blog in blogs:
            if blog.get('id') == today_blog_id:
                logger.info(f"\n✅ TODAY'S BLOG FOUND IN S3 INDEX!")
                logger.info(f"   ID: {blog.get('id')}")
                logger.info(f"   Title: {blog.get('title')}")
                logger.info(f"   Category: {blog.get('category')}")
                logger.info(f"   Created: {blog.get('createdAt')}")
                found = True
                break
        
        if not found:
            logger.warning(f"\n❌ TODAY'S BLOG NOT IN S3 INDEX!")
            logger.info(f"   Expected ID: {today_blog_id}")
            logger.info(f"\n📋 Latest 5 blogs in index:")
            for blog in blogs[:5]:
                logger.info(f"   - {blog.get('id')}: {blog.get('title')}")
        
        return found
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    check_s3_index()
