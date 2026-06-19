import chromadb
import os
from dotenv import load_dotenv

load_dotenv()

CHROMA_API_KEY = os.getenv('CHROMA_API_KEY')
CHROMA_TENANT_ID = os.getenv('CHROMA_TENANT_ID')
CHROMA_DB_NAME = os.getenv('CHROMA_DB_NAME', 'Development')

def main():
    print("--- Verifying SKILLS in Chroma DB ---")
    try:
        client = chromadb.CloudClient(
            api_key=CHROMA_API_KEY,
            tenant=CHROMA_TENANT_ID,
            database=CHROMA_DB_NAME
        )
        
        col = client.get_collection("portfolio")
        
        # 1. List all IDs to find skill-related ones
        print("\n[INFO] searching for 'skill_' IDs...")
        all_data = col.get() # Get all metadata/ids
        skill_ids = [id for id in all_data['ids'] if 'skill' in id]
        
        if not skill_ids:
            print("[WARN] No IDs found starting with 'skill_'")
        else:
            print(f"[FOUND] {len(skill_ids)} Skill entries:")
            results = col.get(ids=skill_ids)
            for i in range(len(results['ids'])):
                print(f"\nID: {results['ids'][i]}")
                print(f"Content: {results['documents'][i]}")
                print(f"Meta: {results['metadatas'][i]}")
                
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    main()
