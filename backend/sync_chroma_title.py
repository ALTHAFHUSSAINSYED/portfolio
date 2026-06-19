import os
import chromadb
import logging
from dotenv import load_dotenv

# Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ChromaSync")

# Constants
BLOG_ID = "DevOps_1767241800"
NEW_TITLE = "DevOps 2026: AI-Driven Pipelines & Self-Healing Infrastructure"
COLLECTION_NAME = "Blogs_data"

def sync_chroma_title():
    # Load env vars
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env.local'))
    
    # Init Client
    try:
        api_key = os.getenv("CHROMA_API_KEY")
        tenant = os.getenv("CHROMA_TENANT_ID")
        db_name = os.getenv("CHROMA_DB_NAME", "Development")
        
        client = chromadb.CloudClient(
            api_key=api_key,
            tenant=tenant,
            database=db_name
        )
        
        collection = client.get_collection(COLLECTION_NAME)
        
        # Get current entry
        result = collection.get(ids=[BLOG_ID])
        
        if not result['ids']:
            logger.error(f"❌ Blog ID {BLOG_ID} not found in ChromaDB!")
            return
            
        current_metadata = result['metadatas'][0]
        current_title = current_metadata.get('title')
        
        logger.info(f"Current Title in ChromaDB: '{current_title}'")
        
        if current_title == NEW_TITLE:
            logger.info("✅ Title is already up to date.")
        else:
            logger.info(f"🔄 Updating title to: '{NEW_TITLE}'")
            
            # Update metadata
            current_metadata['title'] = NEW_TITLE
            
            collection.update(
                ids=[BLOG_ID],
                metadatas=[current_metadata]
            )
            logger.info("✅ ChromaDB update successful!")
            
    except Exception as e:
        logger.error(f"❌ ChromaDB Sync Failed: {e}")

if __name__ == "__main__":
    sync_chroma_title()
