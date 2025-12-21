import os
import json
import chromadb
import uuid
from chromadb.config import Settings
from dotenv import load_dotenv

# Load environment variables
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
    print("[CONNECT] Using Local ChromaDB (backend/chroma_db)...")
    return chromadb.PersistentClient(path="chroma_db")

def populate_db():
    print("="*50)
    print("[START] Starting Database Population")
    print("="*50)

    # 1. Connect
    client = get_chroma_client()

    # 2. Get/Create Collections
    # We use get_or_create to avoid errors if they don't exist
    portfolio_col = client.get_or_create_collection("portfolio")
    projects_col = client.get_or_create_collection("Projects_data")
    
    print("[INFO] Collections ready: portfolio, Projects_data")

    # 3. Load Data from JSON
    # We look for the file in the current directory or 'backend/'
    json_path = "portfolio_data.json"
    if not os.path.exists(json_path):
        json_path = "backend/portfolio_data.json"
    
    if not os.path.exists(json_path):
        print(f"[ERROR] Could not find {json_path}")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 4. Sync Projects (The part that was crashing)
    print("[INFO] Syncing Projects...")
    
    if "projects" in data:
        # Clear existing to avoid duplicates? 
        # Ideally, we verify before adding, but for populate script, 
        # deleting old data ensures clean state.
        try:
            existing_ids = projects_col.get()['ids']
            if existing_ids:
                projects_col.delete(ids=existing_ids)
                print(f"[INFO] Cleared {len(existing_ids)} old projects.")
        except:
            pass

        ids = []
        documents = []
        metadatas = []

        for proj in data["projects"]:
            # Generate a consistent ID or use existing
            p_id = proj.get("id", str(uuid.uuid4()))
            
            # Create a rich document text for embedding
            # We combine all fields so the AI can search everything
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

        if ids:
            projects_col.add(ids=ids, documents=documents, metadatas=metadatas)
            print(f"[SUCCESS] Added {len(ids)} projects to ChromaDB.")
        else:
            print("[WARN] No projects found in JSON.")

    # 5. Sync Resume/Portfolio Info
    print("[INFO] Syncing Resume & Skills...")
    # (Add logic here if you populate the 'portfolio' collection too)
    # ...

    print("="*50)
    print("[DONE] Database Population Complete")
    print("="*50)

if __name__ == "__main__":
    populate_db()
        name="portfolio",
        embedding_function=LocalEmbeddingFunction()
    )
    
    # 3. LOAD JSON
    path = 'portfolio_data.json' if os.path.exists('portfolio_data.json') else 'backend/portfolio_data.json'
    with open(path, 'r') as f: 
        data = json.load(f)

    docs, metas, ids = [], [], []

    # 4. PROCESS PERSONAL INFO
    info = data.get('personalInfo', {})
    if info:
        text = f"Candidate: {info.get('name')}. Role: {info.get('title')}. Summary: {info.get('summary')}. Contact: {info.get('email')}, {info.get('location')}."
        docs.append(clean(text))
        metas.append({"type": "resume", "name": info.get('name'), "email": info.get('email')})
        ids.append("info")

    # 5. PROCESS SKILLS
    for cat, items in data.get('skills', {}).items():
        s_list = [i['name'] if isinstance(i, dict) else str(i) for i in items]
        docs.append(f"Category: {cat}. Skills: {', '.join(s_list)}.")
        metas.append({"type": "skill", "category": cat})
        ids.append(f"skill_{cat}")

    # 6. PROCESS EXPERIENCE
    for i, exp in enumerate(data.get('experience', [])):
        responsibilities = exp.get('responsibilities', []) if isinstance(exp.get('responsibilities'), list) else []
        achievements = exp.get('achievements', []) if isinstance(exp.get('achievements'), list) else []
        
        text = f"Role: {exp.get('position')} at {exp.get('company')}. Duration: {exp.get('duration')}. "
        if responsibilities:
            text += f"Responsibilities: {' '.join(responsibilities)}. "
        if achievements:
            text += f"Achievements: {' '.join(achievements)}."
        
        docs.append(clean(text))
        metas.append({"type": "experience", "company": exp.get('company')})
        ids.append(f"exp_{i}")

    # 7. PROCESS CERTIFICATIONS
    for i, cert in enumerate(data.get('certifications', [])):
        text = f"Certification: {cert.get('name')} from {cert.get('issuer')}. Year: {cert.get('year')}. Category: {cert.get('category')}."
        docs.append(clean(text))
        metas.append({"type": "certification", "category": cert.get('category')})
        ids.append(f"cert_{i}")

    # 8. ADD TO CHROMADB
    if docs:
        coll.add(documents=docs, metadatas=metas, ids=ids)
        print(f"✅ Portfolio Synced to ChromaDB ({len(docs)} items).")
    else:
        print("⚠️ No portfolio data found to sync")

if __name__ == "__main__": 
    main()
