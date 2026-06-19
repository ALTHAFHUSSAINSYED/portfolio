#!/usr/bin/env python3
"""
Delete blogs from specific categories in MongoDB and ChromaDB
Categories to delete:
- Frontend Development
- IoT Development
- Blockchain
- Databases
- Edge Computing
- Quantum Computing
"""

import os
import sys
from dotenv import load_dotenv
from pymongo import MongoClient
import chromadb

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env.local'))

# Categories to delete
CATEGORIES_TO_DELETE = [
    'Frontend Development',
    'IoT Development',
    'Blockchain',
    'Databases',
    'Edge Computing',
    'Quantum Computing'
]

def delete_from_mongodb():
    """Delete blogs from MongoDB"""
    mongo_url = os.getenv('MONGO_URL') or os.getenv('MONGODB_URI')
    
    if not mongo_url:
        print("❌ Error: MONGO_URL not found in environment variables")
        return
    
    try:
        print("\n🔗 Connecting to MongoDB...")
        client = MongoClient(mongo_url)
        db = client['portfolio']
        blogs_collection = db['blogs']
        
        # Count blogs to delete
        count = blogs_collection.count_documents({"category": {"$in": CATEGORIES_TO_DELETE}})
        print(f"📊 Found {count} blogs to delete from MongoDB")
        
        if count == 0:
            print("✅ No blogs found with these categories in MongoDB")
            return
        
        # List blogs to be deleted
        blogs_to_delete = list(blogs_collection.find({"category": {"$in": CATEGORIES_TO_DELETE}}, {"title": 1, "category": 1}))
        print("\n📝 Blogs to delete:")
        for blog in blogs_to_delete:
            print(f"   - {blog['title']} ({blog['category']})")
        
        # Delete the blogs
        result = blogs_collection.delete_many({"category": {"$in": CATEGORIES_TO_DELETE}})
        print(f"\n✅ Deleted {result.deleted_count} blogs from MongoDB")
        
        client.close()
    except Exception as e:
        print(f"❌ Error deleting from MongoDB: {e}")

def delete_from_chromadb():
    """Delete blogs from ChromaDB"""
    chroma_api_key = os.getenv('CHROMADB_API_KEY')
    chroma_tenant = os.getenv('CHROMADB_TENANT', 'default_tenant')
    chroma_database = os.getenv('CHROMADB_DATABASE', 'default_database')
    
    if not chroma_api_key:
        print("❌ Error: CHROMADB_API_KEY not found in environment variables")
        return
    
    try:
        print("\n🔗 Connecting to ChromaDB...")
        client = chromadb.CloudClient(
            tenant=chroma_tenant,
            database=chroma_database,
            api_key=chroma_api_key
        )
        
        collection = client.get_or_create_collection(name="portfolio_blogs")
        
        # Get all documents
        all_docs = collection.get()
        
        if not all_docs or not all_docs['ids']:
            print("✅ No documents found in ChromaDB")
            return
        
        # Filter IDs to delete based on metadata category
        ids_to_delete = []
        for i, metadata in enumerate(all_docs['metadatas']):
            if metadata and metadata.get('category') in CATEGORIES_TO_DELETE:
                ids_to_delete.append(all_docs['ids'][i])
        
        print(f"📊 Found {len(ids_to_delete)} blogs to delete from ChromaDB")
        
        if len(ids_to_delete) == 0:
            print("✅ No blogs found with these categories in ChromaDB")
            return
        
        # Delete the documents
        collection.delete(ids=ids_to_delete)
        print(f"✅ Deleted {len(ids_to_delete)} blogs from ChromaDB")
        
    except Exception as e:
        print(f"❌ Error deleting from ChromaDB: {e}")

def main():
    print("="*60)
    print("🗑️  CATEGORY DELETION SCRIPT")
    print("="*60)
    print("\nDeleting blogs from these categories:")
    for cat in CATEGORIES_TO_DELETE:
        print(f"  ❌ {cat}")
    
    print("\n" + "="*60)
    
    # Delete from MongoDB
    delete_from_mongodb()
    
    # Delete from ChromaDB
    delete_from_chromadb()
    
    print("\n" + "="*60)
    print("✅ Deletion complete!")
    print("="*60)

if __name__ == "__main__":
    main()
