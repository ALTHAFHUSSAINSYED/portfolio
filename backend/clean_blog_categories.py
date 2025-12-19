#!/usr/bin/env python3
"""
Clean Blog Categories Script
Removes blogs that don't match the 6 allowed categories from ChromaDB
"""

import os
import chromadb
from dotenv import load_dotenv

load_dotenv()

# 6 Allowed categories
ALLOWED_CATEGORIES = {
    "Cloud Computing",
    "DevOps",
    "AI and ML",
    "Low-Code/No-Code",
    "Software Development",
    "Cybersecurity"
}

def clean_blog_categories():
    """Remove unauthorized blog categories from ChromaDB"""
    try:
        # Initialize ChromaDB client
        chroma_client = chromadb.CloudClient(
            tenant=os.getenv('CHROMA_TENANT'),
            database=os.getenv('CHROMA_DATABASE'),
            api_key=os.getenv('CHROMA_API_KEY')
        )
        
        # Get Blogs_data collection
        collection = chroma_client.get_collection(name="Blogs_data")
        
        # Get all blogs
        results = collection.get()
        
        total_blogs = len(results['ids'])
        print(f"📚 Total blogs in ChromaDB: {total_blogs}")
        print("=" * 60)
        
        # Analyze categories
        category_counts = {}
        ids_to_delete = []
        
        for i, metadata in enumerate(results['metadatas']):
            category = metadata.get('category', 'Unknown')
            
            # Count category
            category_counts[category] = category_counts.get(category, 0) + 1
            
            # Check if category is allowed
            if category not in ALLOWED_CATEGORIES:
                blog_id = results['ids'][i]
                title = metadata.get('title', 'Unknown')
                ids_to_delete.append(blog_id)
                print(f"❌ Will delete: [{category}] {title}")
        
        print("\n" + "=" * 60)
        print("📊 Category Summary:")
        for category, count in sorted(category_counts.items()):
            status = "✅ KEEP" if category in ALLOWED_CATEGORIES else "❌ DELETE"
            print(f"  {status} {category}: {count} blogs")
        
        # Delete unauthorized blogs
        if ids_to_delete:
            print("\n" + "=" * 60)
            print(f"🗑️  Deleting {len(ids_to_delete)} unauthorized blogs...")
            collection.delete(ids=ids_to_delete)
            print(f"✅ Deleted {len(ids_to_delete)} blogs")
            
            # Verify
            new_count = collection.count()
            print(f"✅ Remaining blogs: {new_count}")
        else:
            print("\n✅ All blogs have authorized categories - nothing to delete")
        
        print("\n" + "=" * 60)
        print("✅ CLEANUP COMPLETED")
        
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🧹 Blog Category Cleanup")
    print("=" * 60)
    print("Allowed categories:")
    for i, cat in enumerate(sorted(ALLOWED_CATEGORIES), 1):
        print(f"  {i}. {cat}")
    print("=" * 60)
    
    clean_blog_categories()
