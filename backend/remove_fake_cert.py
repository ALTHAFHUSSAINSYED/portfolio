"""
Script to remove fake "Generative AI Certified Professional" certification from ChromaDB
"""
import os
import chromadb
from dotenv import load_dotenv

load_dotenv()

# Connect to ChromaDB
chroma_client = chromadb.CloudClient(
    api_key=os.getenv('CHROMA_API_KEY'),
    tenant=os.getenv('CHROMA_TENANT'),
    database=os.getenv('CHROMA_DATABASE', 'Development')
)

# Get the portfolio collection
collection = chroma_client.get_collection(name='portfolio')

# Get all documents
results = collection.get()

print(f"Total documents in portfolio collection: {len(results['ids'])}")

# Find and delete documents containing the fake certification
deleted_count = 0
for i, (doc_id, document) in enumerate(zip(results['ids'], results['documents'])):
    if 'Generative AI Certified Professional' in document:
        print(f"\n🔍 Found fake certification in document ID: {doc_id}")
        print(f"Preview: {document[:200]}...")
        
        # Delete this document
        collection.delete(ids=[doc_id])
        deleted_count += 1
        print(f"✅ Deleted document {doc_id}")

print(f"\n📊 Summary: Deleted {deleted_count} document(s) containing fake certification")

# Verify deletion
results_after = collection.get()
print(f"Documents remaining: {len(results_after['ids'])}")
# ChromaDB repopulated on Sun, Dec 14, 2025  1:38:25 AM
