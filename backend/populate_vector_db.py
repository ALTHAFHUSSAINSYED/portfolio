import chromadb
import os
import json
import re
import glob
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
try:
    genai.configure(api_key=GOOGLE_API_KEY)
except Exception as e:
    print(f"[WARN] Gemini configuration warning: {e}")

# --- 2. DEFINE THE NEW EMBEDDING CLASS ---
class GeminiEmbeddingFunction(EmbeddingFunction):
    def __init__(self):

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
        try:
            genai.configure(api_key=GOOGLE_API_KEY)
        except Exception as e:
            print(f"[WARN] Gemini configuration warning: {e}")

        # --- 2. DEFINE THE NEW EMBEDDING CLASS ---
        class GeminiEmbeddingFunction(EmbeddingFunction):
            def __init__(self):
                # Dummy init to silence DeprecationWarning
                pass

            def __call__(self, input: Documents) -> Embeddings:
                model = 'models/text-embedding-004'
                try:
                    return [
                        genai.embed_content(
                            model=model,
                            content=text,
                            task_type="retrieval_document"
                        )['embedding']
                        for text in input
                    ]
                except Exception as e:
                    print(f"[ERROR] Embedding failed: {e}")
                    # Return empty embedding on failure to prevent full crash (fallback)
                    return [[0.0] * 768 for _ in input]

        def clean_text(text):
            # Simple cleaner to remove messy whitespace
            if not text: return ""
            text = re.sub(r'\s+', ' ', str(text)).strip()
            return text

        def safe_meta(val):
            """CRITICAL FIX: Ensure metadata is never None"""
            if val is None:
                return "Unknown"
            return str(val)

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
            collections = ["portfolio", "Projects_data", "Blogs_data"]
    
            for col in collections:
                try:
                    client.delete_collection(col)
                    print(f"[INFO] Deleted old '{col}' collection.")
                except:
                    pass 
        
            portfolio_col = client.create_collection(name="portfolio", embedding_function=GeminiEmbeddingFunction())
            projects_col = client.create_collection(name="Projects_data", embedding_function=GeminiEmbeddingFunction())
            blogs_col = client.create_collection(name="Blogs_data", embedding_function=GeminiEmbeddingFunction())
            print("[SUCCESS] Created fresh collections with Gemini Embeddings (768 dimensions).")

            # --- 5. LOAD PORTFOLIO AND PROJECTS ---
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
                        # Construct text safely
                        name = safe_meta(proj.get('name'))
                        summary = safe_meta(proj.get('summary'))
                        tech = ", ".join(proj.get('technologies', []))
                        details = safe_meta(proj.get('details'))
                
                        text = f"Project: {name}. Summary: {summary}. Tech Stack: {tech}. Details: {details}"
                        clean_doc = clean_text(text)
                
                        # Add to 'portfolio'
                        portfolio_col.add(
                            ids=[f"proj_{i}"], 
                            documents=[clean_doc], 
                            metadatas=[{"type": "project", "title": name}]
                        )
                
                        # Add to 'Projects_data'
                        projects_col.add(
                            ids=[f"proj_{i}"], 
                            documents=[clean_doc], 
                            metadatas=[{"name": name, "category": "Project"}]
                        )

                # Process Skills
                if "skills" in data:
                    print("[INFO] Syncing Skills...")
                    for cat, skills in data["skills"].items():
                        cat_safe = safe_meta(cat)
                        skill_list = ", ".join([safe_meta(s['name'] if isinstance(s, dict) else s) for s in skills])
                        text = f"Skill Category: {cat_safe}. Skills: {skill_list}."
                
                        portfolio_col.add(
                            ids=[f"skill_{cat_safe}"], 
                            documents=[clean_text(text)], 
                            metadatas=[{"type": "skill", "category": cat_safe}]
                        )

            # --- 6. LOAD BLOGS ---
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
                                title = safe_meta(blog.get('title'))
                                content = safe_meta(blog.get('content'))
                                text = f"Blog Title: {title}. Content: {content[:2000]}..."
                        
                                blogs_col.add(
                                    ids=[f"blog_{i}"], 
                                    documents=[clean_text(text)], 
                                    metadatas=[{"title": title, "type": "blog"}]
                                )
                        except Exception as e:
                            print(f"[WARN] Skipped blog {filepath}: {e}")

            print("[SUCCESS] Database has been completely repopulated!")

        if __name__ == "__main__":
            main()
