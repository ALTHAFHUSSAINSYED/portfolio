
import os
import json
import chromadb
import uuid
from dotenv import load_dotenv

# Load environment variables yes and now
load_dotenv()

def get_chroma_client():
    """
    Returns a ChromaDB client.
    Tries Cloud first, then falls back to Local if keys are missing.
    """
    api_key = os.getenv('CHROMA_API_KEY')
    tenant_id = os.getenv('CHROMA_TENANT_ID')
    db_name = os.getenv('CHROMA_DB_NAME', 'Development')

    # 1. Try Cloud Connection
    if api_key and tenant_id:
        try:
            print("[CONNECT] Attempting to connect to Chroma Cloud...")
            client = chromadb.CloudClient(
                api_key=api_key,
                tenant=tenant_id,
                database=db_name
            )
            print("[SUCCESS] Connected to Chroma Cloud.")
            return client
        except Exception as e:
            print(f"[ERROR] Cloud connection failed: {e}")
            print("[WARN] Falling back to Local Mode...")

    # 2. Local Fallback
    # Try different paths to ensure we find the folder
    possible_paths = ["chroma_db", "backend/chroma_db", "./chroma_db"]
    path = "chroma_db"
    
    for p in possible_paths:
        if os.path.exists(p):
            path = p
            break
            
    print(f"[CONNECT] Using Local ChromaDB at: {path}")
    return chromadb.PersistentClient(path=path)

def populate_db():
    print("="*50)
    print("[INFO] Starting Database Population")
    print("="*50)

    # 1. Connect
    client = get_chroma_client()

    # 2. Get/Create Collections
    # We use get_or_create to avoid errors if they don't exist
    try:
        portfolio_col = client.get_or_create_collection("portfolio")
        projects_col = client.get_or_create_collection("Projects_data")
        print("[INFO] Collections ready: portfolio, Projects_data")
    except Exception as e:
        print(f"[ERROR] Failed to get collections: {e}")
        return

    # 3. Load Data from JSON
    # Look for the file in current or parent directory
    json_paths = ["portfolio_data.json", "backend/portfolio_data.json", "../portfolio_data.json"]
    json_path = None
    
    for p in json_paths:
        if os.path.exists(p):
            json_path = p
            break
    
    if not json_path:
        print("[ERROR] Could not find portfolio_data.json")
        return

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"[INFO] Loaded JSON data from {json_path}")
    except Exception as e:
        print(f"[ERROR] Failed to read JSON file: {e}")
        return

    # 4. Sync Projects
    print("[INFO] Syncing Projects (Resume/Skills/Experience/Certifications)...")
    
    if "projects" in data:
        # Optional: Clear existing data to prevent duplicates
        try:
            existing_ids = projects_col.get()['ids']
            if existing_ids:
                projects_col.delete(ids=existing_ids)
                print(f"[INFO] Cleared {len(existing_ids)} old projects.")
        except Exception as e:
            print(f"[WARN] Could not clear old projects: {e}")


        ids = []
        documents = []
        metadatas = []
        batch_size = 100
        total_added = 0

        for proj in data["projects"]:
            # Generate a consistent ID
            p_id = proj.get("id", str(uuid.uuid4()))

            # Create text for embedding
            full_text = (
                f"Title: {proj.get('name', '')}\n"
                f"Summary: {proj.get('summary', '')}\n"
                f"Tech Stack: {', '.join(proj.get('technologies', []))}\n"
                f"Details: {proj.get('details', '')}\n"
                f"Key Outcomes: {proj.get('key_outcomes', '')}"
            )

            ids.append(p_id)
            documents.append(full_text)
            metadatas.append({
                "name": proj.get("name", "Unknown"),
                "category": "Project"
            })

            if len(ids) == batch_size:
                try:
                    projects_col.add(ids=ids, documents=documents, metadatas=metadatas)
                    total_added += len(ids)
                    print(f"[SUCCESS] Added {len(ids)} projects to ChromaDB (batch).")
                except Exception as e:
                    print(f"[ERROR] Failed to add batch of projects: {e}")
                ids, documents, metadatas = [], [], []

        if ids:
            try:
                projects_col.add(ids=ids, documents=documents, metadatas=metadatas)
                total_added += len(ids)
                print(f"[SUCCESS] Added {len(ids)} projects to ChromaDB (final batch).")
            except Exception as e:
                print(f"[ERROR] Failed to add final batch of projects: {e}")
        if total_added == 0:
            print("[WARN] No projects found in JSON.")

    # 5. Sync Resume/Portfolio Info (Optional)
    # You can add logic here if you need to populate the 'portfolio' collection
    # ...

    print("="*50)
    print("[DONE] Database Population Complete")
    print("="*50)

if __name__ == "__main__":
    try:
        populate_db()
    except Exception as e:
        print(f"[CRITICAL ERROR] Script crashed: {e}")
