import chromadb
import os
from dotenv import load_dotenv

load_dotenv()

CHROMA_API_KEY = os.getenv('CHROMA_API_KEY')
CHROMA_TENANT_ID = os.getenv('CHROMA_TENANT_ID')
CHROMA_DB_NAME = os.getenv('CHROMA_DB_NAME', 'Development')

def main():
    print("--- Checking Chroma DB State ---")
    
    try:
        if CHROMA_API_KEY:
            print("[INFO] Connecting to Chroma Cloud...")
            client = chromadb.CloudClient(
                api_key=CHROMA_API_KEY,
                tenant=CHROMA_TENANT_ID,
                database=CHROMA_DB_NAME
            )
        else:
            print("[INFO] Connecting to Local ChromaDB...")
            client = chromadb.PersistentClient(path="chroma_db")
            
        collections = client.list_collections()
        print(f"\nTotal Collections Found: {len(collections)}")
        
        for col in collections:
            count = col.count()
            print(f"- Collection Name: {col.name} | Item Count: {count}")
            
    except Exception as e:
        print(f"[ERROR] Failed to query Chroma DB: {e}")

    # Check for specific blog
    try:
        blogs_col = client.get_collection("Blogs_data")
        results = blogs_col.get(where={"title": "How to Scale Enterprise Integration Without Breaking Your Budget: A Low-Code Approach"})
        if results['ids']:
            print(f"\n[CONFIRMED] Blog found: '{results['metadatas'][0]['title']}'")
            print(f"Category: {results['metadatas'][0]['category']}")
        else:
            print("\n[WARN] Blog NOT found in 'Blogs_data'.")
    except Exception as e:
        print(f"[WARN] Could not verify specific blog: {e}")

if __name__ == "__main__":
    main()
