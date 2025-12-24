"""
Blog Cleanup Module
Deletes blogs older than 60 days to keep the system lean.
"""

import os
import time
import logging
import json
import chromadb
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BlogCleanup")

class BlogCleanup:
    def __init__(self):
        load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '.env'))
        
        self.storage_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            "generated_blogs"
        )
        
        # Setup ChromaDB for deletion
        self._setup_chroma()

    def _setup_chroma(self):
        try:
            chroma_api_key = os.getenv("CHROMA_API_KEY")
            chroma_host = "api.trychroma.com"
            chroma_tenant = os.getenv("CHROMA_TENANT_ID")
            chroma_db = os.getenv("CHROMA_DATABASE")
            
            if chroma_api_key:
                self.chroma_client = chromadb.HttpClient(
                    host=chroma_host,
                    ssl=True,
                    headers={
                        "x-chroma-token": chroma_api_key,
                        "x-tenant": chroma_tenant,
                        "x-database": chroma_db
                    }
                )
            else:
                self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        except:
            self.chroma_client = None

    def run_cleanup(self) -> dict:
        """Run the cleanup process"""
        logger.info("Starting daily cleanup...")
        deleted_count = 0
        deleted_files = []
        cutoff_date = datetime.now() - timedelta(days=60)
        
        if not os.path.exists(self.storage_dir):
            return {"status": "no_dir", "deleted": 0}

        # 1. Scan Files
        for filename in os.listdir(self.storage_dir):
            if not filename.endswith('.json'):
                continue
                
            filepath = os.path.join(self.storage_dir, filename)
            try:
                # Check file modification time first (fastest)
                mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                
                # If modification time is old, double check content creation date
                if mtime < cutoff_date:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        created_at = datetime.fromisoformat(data.get('created_at', datetime.now().isoformat()))
                    
                    if created_at < cutoff_date:
                        # DELETE
                        blog_id = data.get('id', filename.replace('.json', ''))
                        
                        # Delete File
                        os.remove(filepath)
                        
                        # Delete from ChromaDB
                        if self.chroma_client:
                             try:
                                collection = self.chroma_client.get_collection("Blogs_data")
                                collection.delete(ids=[blog_id])
                             except Exception as e:
                                 logger.warning(f"Failed to delete {blog_id} from Chroma: {e}")

                        deleted_count += 1
                        deleted_files.append(filename)
                        logger.info(f"Deleted old blog: {filename}")
                        
            except Exception as e:
                logger.error(f"Error checking file {filename}: {e}")

        logger.info(f"Cleanup complete. Deleted {deleted_count} files.")
        return {
            "status": "success",
            "deleted_count": deleted_count,
            "deleted_files": deleted_files
        }

if __name__ == "__main__":
    cleanup = BlogCleanup()
    res = cleanup.run_cleanup()
    print(json.dumps(res, indent=2))
