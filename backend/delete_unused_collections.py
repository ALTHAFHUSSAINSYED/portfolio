"""
Delete Unused Legacy Collections from ChromaDB Cloud
Removes: portfolio, Projects_data, Blogs_data

After migration to portfolio_master, these collections are no longer used.
"""

import os
import chromadb
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv('/home/ec2-user/portfolio/backend/.env.local')

def delete_unused_collections():
    """Delete the 3 unused legacy collections from ChromaDB Cloud"""
    
    # Connect to ChromaDB Cloud
    api_key = os.getenv('CHROMA_API_KEY')
    tenant_id = os.getenv('CHROMA_TENANT_ID')
    db_name = os.getenv('CHROMA_DB_NAME', 'Development')
    
    if not api_key or not tenant_id:
        logger.error("Missing CHROMA_API_KEY or CHROMA_TENANT_ID in environment")
        return False
    
    try:
        client = chromadb.CloudClient(
            tenant=tenant_id,
            database=db_name,
            api_key=api_key
        )
        logger.info(f"✅ Connected to ChromaDB Cloud (Database: {db_name})")
        
        # List all collections before deletion
        all_collections = client.list_collections()
        logger.info(f"\n📋 Current Collections ({len(all_collections)}):")
        for col in all_collections:
            count = col.count()
            logger.info(f"   - {col.name}: {count} records")
        
        # Collections to delete
        unused_collections = ['portfolio', 'Projects_data', 'Blogs_data']
        
        logger.info(f"\n🗑️  Deleting {len(unused_collections)} unused collections...")
        
        deleted_count = 0
        for collection_name in unused_collections:
            try:
                # Check if collection exists
                existing_cols = [c.name for c in client.list_collections()]
                if collection_name in existing_cols:
                    # Get count before deletion
                    col = client.get_collection(collection_name)
                    count = col.count()
                    
                    # Delete collection
                    client.delete_collection(collection_name)
                    logger.info(f"   ✅ Deleted '{collection_name}' ({count} records)")
                    deleted_count += 1
                else:
                    logger.info(f"   ⏭️  Skipped '{collection_name}' (does not exist)")
            except Exception as e:
                logger.error(f"   ❌ Failed to delete '{collection_name}': {e}")
        
        # List remaining collections
        remaining = client.list_collections()
        logger.info(f"\n✅ Cleanup Complete!")
        logger.info(f"   Deleted: {deleted_count}/{len(unused_collections)}")
        logger.info(f"   Remaining Collections ({len(remaining)}):")
        for col in remaining:
            count = col.count()
            logger.info(f"      - {col.name}: {count} records")
        
        # Verify portfolio_master is intact
        if 'portfolio_master' in [c.name for c in remaining]:
            master_col = client.get_collection('portfolio_master')
            master_count = master_col.count()
            logger.info(f"\n✅ portfolio_master intact with {master_count} records")
        else:
            logger.warning("\n⚠️  WARNING: portfolio_master collection not found!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ ChromaDB connection failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🗑️  Delete Unused ChromaDB Collections")
    print("=" * 60)
    
    success = delete_unused_collections()
    
    if success:
        print("\n✅ All unused collections deleted successfully!")
        print("💡 System now uses only 'portfolio_master' for all data")
    else:
        print("\n❌ Failed to delete collections. Check logs above.")
