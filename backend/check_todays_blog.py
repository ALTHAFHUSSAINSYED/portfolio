"""
Check if today's blog (Cloud_Computing_1767414600) is in portfolio_master
"""

import os
import chromadb
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv('/home/ec2-user/portfolio/backend/.env.local')

def check_todays_blog():
    """Check if today's blog exists in portfolio_master"""
    
    # Connect to ChromaDB Cloud
    api_key = os.getenv('CHROMA_API_KEY')
    tenant_id = os.getenv('CHROMA_TENANT_ID')
    db_name = os.getenv('CHROMA_DB_NAME', 'Development')
    
    try:
        client = chromadb.CloudClient(
            tenant=tenant_id,
            database=db_name,
            api_key=api_key
        )
        logger.info(f"✅ Connected to ChromaDB Cloud")
        
        # Get portfolio_master collection
        collection = client.get_collection('portfolio_master')
        total_count = collection.count()
        logger.info(f"📊 portfolio_master: {total_count} total records")
        
        # Query for blog entries (category='blog')
        results = collection.get(
            where={"category": "blog"},
            include=["metadatas", "documents"]
        )
        
        logger.info(f"\n📚 Blog entries in portfolio_master: {len(results['ids'])}")
        
        # Check for today's blog
        today_blog_id = "Cloud_Computing_1767414600"
        
        for i, blog_id in enumerate(results['ids']):
            metadata = results['metadatas'][i]
            title = metadata.get('title', 'N/A')
            url = metadata.get('url', 'N/A')
            
            if blog_id == today_blog_id:
                logger.info(f"\n✅ TODAY'S BLOG FOUND!")
                logger.info(f"   ID: {blog_id}")
                logger.info(f"   Title: {title}")
                logger.info(f"   URL: {url}")
                logger.info(f"   Metadata: {metadata}")
                return True
        
        logger.warning(f"\n❌ TODAY'S BLOG NOT FOUND!")
        logger.info(f"   Expected ID: {today_blog_id}")
        logger.info(f"\n📋 Available blog IDs:")
        for blog_id in results['ids'][:10]:  # Show first 10
            logger.info(f"   - {blog_id}")
        
        return False
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    check_todays_blog()
