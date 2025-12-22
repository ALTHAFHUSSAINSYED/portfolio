import chromadb
import os
from dotenv import load_dotenv

load_dotenv()

CHROMA_API_KEY = os.getenv('CHROMA_API_KEY')
CHROMA_TENANT_ID = os.getenv('CHROMA_TENANT_ID')
CHROMA_DB_NAME = os.getenv('CHROMA_DB_NAME', 'Development')

def main():
    print("--- Verifying Project Details ---")
    
    try:
        if CHROMA_API_KEY:
            client = chromadb.CloudClient(
                api_key=CHROMA_API_KEY,
                tenant=CHROMA_TENANT_ID,
                database=CHROMA_DB_NAME
            )
        else:
            client = chromadb.PersistentClient(path="chroma_db")
            
        projects_col = client.get_collection("Projects_data")
        
        # Query for the specific project ID
        # Note: The populate script uses the MongoDB _id as the Chroma ID, or a slug. 
        # Let's check if 'aws-cloudwatch-grafana-monitoring' is the ID or if we need to search by metadata.
        # Based on user input, they expect the ID to be 'aws-cloudwatch-grafana-monitoring'.
        
        target_id = "aws-cloudwatch-grafana-monitoring"
        
        # Try fetching by ID first
        results_by_id = projects_col.get(ids=[target_id])
        
        if results_by_id['ids']:
            print(f"\n[FOUND] Project found by ID: '{target_id}'")
            doc_content = results_by_id['documents'][0]
            print(f"Document Content Length: {len(doc_content)} characters")
            print("-" * 20)
            print(doc_content)
            print("-" * 20)
            return

        # If not found by ID, try searching metadata or just listing all to see what's there
        print(f"\n[WARN] Project ID '{target_id}' not found directly. Listing all project IDs...")
        all_projects = projects_col.get()
        for idx, pid in enumerate(all_projects['ids']):
            print(f"- {pid}")
            
    except Exception as e:
        print(f"[ERROR] Verification failed: {e}")

if __name__ == "__main__":
    main()
