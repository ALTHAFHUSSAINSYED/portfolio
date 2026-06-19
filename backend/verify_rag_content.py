import chromadb
import os
from dotenv import load_dotenv

load_dotenv()

CHROMA_API_KEY = os.getenv('CHROMA_API_KEY')
CHROMA_TENANT_ID = os.getenv('CHROMA_TENANT_ID')
CHROMA_DB_NAME = os.getenv('CHROMA_DB_NAME', 'Development')

def main():
    print("--- Verifying RAG Content Length ---")
    
    try:
        if CHROMA_API_KEY:
            client = chromadb.CloudClient(
                api_key=CHROMA_API_KEY,
                tenant=CHROMA_TENANT_ID,
                database=CHROMA_DB_NAME
            )
        else:
            client = chromadb.PersistentClient(path="chroma_db")
            
        blogs_col = client.get_collection("Blogs_data")
        
        # Query for the specific blog
        results = blogs_col.get(where={"title": "How to Scale Enterprise Integration Without Breaking Your Budget: A Low-Code Approach"})
        
        if results['ids']:
            doc_content = results['documents'][0]
            content_len = len(doc_content)
            print(f"\n[FOUND] Blog: '{results['metadatas'][0]['title']}'")
            print(f"Document Content Length: {content_len} characters")
            
            if content_len > 3000:
                print("✅ [PASS] Content length exceeds 3000 chars. Full content is likely present.")
            else:
                print("❌ [FAIL] Content length is <= 3000 chars. Still truncated.")
                
            # Print last 100 chars to verify it's the end of the article
            print(f"\nLast 100 chars of document:\n...{doc_content[-100:]}")
            
        else:
            print("\n[WARN] Blog NOT found in 'Blogs_data'.")
            
    except Exception as e:
        print(f"[ERROR] Verification failed: {e}")

if __name__ == "__main__":
    main()
