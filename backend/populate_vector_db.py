import chromadb
import os
import json
import re
import glob
import time
import google.generativeai as genai
from chromadb import Documents, EmbeddingFunction, Embeddings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- 1. CONFIGURATION ---
GOOGLE_API_KEY = os.getenv('GEMINI_API_KEY')
if not GOOGLE_API_KEY:
    print("[ERROR] GEMINI_API_KEY is missing.")
    exit(1)

# Configure the Gemini API
genai.configure(api_key=GOOGLE_API_KEY)

# --- 2. DEFINE THE NEW EMBEDDING CLASS ---
class GeminiEmbeddingFunction(EmbeddingFunction):
    def __call__(self, input: Documents) -> Embeddings:
        # We use the specific model you have access to: text-embedding-004
        model = 'models/text-embedding-004'
        
        # Request embeddings from Google
        return [
            genai.embed_content(
                model=model,
                content=text,
                task_type="retrieval_document"
            )['embedding']
            for text in input
        ]

def clean_text(text):
    # Simple cleaner to remove messy whitespace
    text = re.sub(r'\s+', ' ', str(text)).strip()
    return text

def main():
    print("[INFO] Starting Database Sync (Powered by Google Gemini)...")

    # --- 3. CONNECT TO CHROMA DB ---
    try:
        if os.getenv('CHROMA_API_KEY'):
            print("[INFO] Connecting to Chroma Cloud...")
            client = chromadb.CloudClient(
                api_key=os.getenv('CHROMA_API_KEY'),
                tenant=os.getenv('CHROMA_TENANT_ID'),
                database=os.getenv('CHROMA_DB_NAME', 'Development')
            )
        else:
            print("[INFO] Connecting to Local ChromaDB...")
            client = chromadb.PersistentClient(path="chroma_db")
    except Exception as e:
        print(f"[ERROR] Connection Failed: {e}")
        return

    # --- 4. WIPE AND RECREATE COLLECTIONS ---
    # We MUST delete old collections because 384-dim data cannot mix with 768-dim data.
    collections = ["portfolio", "Projects_data", "Blogs_data"]
    
    for col in collections:
        try:
            client.delete_collection(col)
            print(f"[INFO] Deleted old '{col}' collection.")
        except:
            pass # Collection did not exist, which is fine
        
    # Create them FRESH with the new Gemini Function
    portfolio_col = client.create_collection(
        name="portfolio", 
        embedding_function=GeminiEmbeddingFunction()
    )
    projects_col = client.create_collection(
        name="Projects_data", 
        embedding_function=GeminiEmbeddingFunction()
    )
    blogs_col = client.create_collection(
        name="Blogs_data", 
        embedding_function=GeminiEmbeddingFunction()
    )
    print("[SUCCESS] Created fresh collections with Gemini Embeddings (768 dimensions).")

    # --- 5. LOAD PORTFOLIO AND PROJECTS ---
    # Try to find the data file
    json_path = 'portfolio_data.json'
    if not os.path.exists(json_path):
        json_path = 'backend/portfolio_data.json'
    
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"[INFO] Loaded {json_path}")
            
        # Process Projects
        if "projects" in data:
            print(f"[INFO] Syncing {len(data['projects'])} Projects...")
            for i, proj in enumerate(data["projects"]):
                # Create a rich text description for the AI to read
                text = (f"Project: {proj.get('name')}. "
                        f"Summary: {proj.get('summary')}. "
                        f"Tech Stack: {', '.join(proj.get('technologies', []))}. "
                        f"Details: {proj.get('details')}")
                
                clean_doc = clean_text(text)
                
                # Add to 'portfolio' (for general questions)
                portfolio_col.add(
                    ids=[f"proj_{i}"], 
                    documents=[clean_doc], 
                    metadatas=[{"type": "project", "title": proj.get('name')}]
                )
                
                # Add to 'Projects_data' (for project-specific searches)
                projects_col.add(
                    ids=[f"proj_{i}"], 
                    documents=[clean_doc], 
                    metadatas=[{"name": proj.get('name'), "category": "Project"}]
                )

        # Process Skills
        if "skills" in data:
            print("[INFO] Syncing Skills...")
            for cat, skills in data["skills"].items():
                # Convert skill list to string
                skill_list = ", ".join([s['name'] if isinstance(s, dict) else str(s) for s in skills])
                text = f"Skill Category: {cat}. Skills: {skill_list}."
                
                portfolio_col.add(
                    ids=[f"skill_{cat}"], 
                    documents=[clean_text(text)], 
                    metadatas=[{"type": "skill", "category": cat}]
                )

    # --- 6. LOAD BLOGS (From generated_blogs folder) ---
    blog_dir = "generated_blogs"
    if not os.path.exists(blog_dir):
        blog_dir = "backend/generated_blogs"
        
    if os.path.exists(blog_dir):
        files = glob.glob(f"{blog_dir}/*.json")
        if files:
            print(f"[INFO] Syncing {len(files)} Blogs...")
            for i, filepath in enumerate(files):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        blog = json.load(f)
                        # Embed the first 2000 chars of the blog content
                        text = f"Blog Title: {blog.get('title')}. Content: {blog.get('content')[:2000]}..."
                        
                        blogs_col.add(
                            ids=[f"blog_{i}"], 
                            documents=[clean_text(text)], 
                            metadatas=[{"title": blog.get('title'), "type": "blog"}]
                        )
                except:
                    print(f"[WARN] Error reading blog: {filepath}")

    print("[SUCCESS] Database has been completely repopulated!")

if __name__ == "__main__":
    main()

import os
import json
import chromadb
import uuid
import gc
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
        batch_size = 2  # lowered further to 2 to minimize memory usage
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
                gc.collect()

        if ids:
            try:
                projects_col.add(ids=ids, documents=documents, metadatas=metadatas)
                total_added += len(ids)
                print(f"[SUCCESS] Added {len(ids)} projects to ChromaDB (final batch).")
            except Exception as e:
                print(f"[ERROR] Failed to add final batch of projects: {e}")
            ids, documents, metadatas = [], [], []
            gc.collect()
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
