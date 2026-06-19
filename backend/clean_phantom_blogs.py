#!/usr/bin/env python3
"""
Clean phantom blog references from MongoDB
Removes blogs with old timestamps (1750492xxx series) that don't exist in S3 or local files
"""

import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def clean_phantom_blogs():
    """Remove phantom blog references from MongoDB"""
    
    # Connect to MongoDB
    mongo_url = os.getenv('MONGO_URL')
    db_name = os.getenv('DB_NAME', 'portfolioDB')
    
    if not mongo_url:
        print("❌ MONGO_URL not found in environment variables")
        return
    
    try:
        client = MongoClient(mongo_url)
        db = client[db_name]
        blogs_collection = db['blogs']
        
        print(f"✅ Connected to MongoDB: {db_name}")
        
        # Count total blogs before cleanup
        total_before = blogs_collection.count_documents({})
        print(f"📊 Total blogs before cleanup: {total_before}")
        
        # Find phantom blogs (old timestamp series: 1750492xxx)
        phantom_query = {
            "id": {"$regex": "^.*_1750492"}
        }
        
        phantom_count = blogs_collection.count_documents(phantom_query)
        print(f"🔍 Found {phantom_count} phantom blogs with timestamp 1750492xxx")
        
        if phantom_count > 0:
            # List phantom blogs before deletion
            print("\n📋 Phantom blogs to be deleted:")
            phantom_blogs = blogs_collection.find(phantom_query)
            for blog in phantom_blogs:
                print(f"  - {blog.get('id')} | {blog.get('title', 'No title')}")
            
            # Ask for confirmation
            confirm = input("\n⚠️  Delete these phantom blogs? (yes/no): ").strip().lower()
            
            if confirm == 'yes':
                # Delete phantom blogs
                result = blogs_collection.delete_many(phantom_query)
                print(f"\n✅ Deleted {result.deleted_count} phantom blogs")
                
                # Count total blogs after cleanup
                total_after = blogs_collection.count_documents({})
                print(f"📊 Total blogs after cleanup: {total_after}")
                
                # List remaining blogs
                print("\n📋 Remaining blogs:")
                remaining_blogs = blogs_collection.find({})
                for blog in remaining_blogs:
                    print(f"  - {blog.get('id')} | {blog.get('title', 'No title')}")
            else:
                print("❌ Cleanup cancelled")
        else:
            print("✅ No phantom blogs found!")
            
            # List all blogs
            print("\n📋 All blogs in MongoDB:")
            all_blogs = blogs_collection.find({})
            for blog in all_blogs:
                print(f"  - {blog.get('id')} | {blog.get('title', 'No title')}")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    clean_phantom_blogs()
