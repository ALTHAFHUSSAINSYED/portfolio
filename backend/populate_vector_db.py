import chromadb
import os
import json
import re
import glob
import google.generativeai as genai
from chromadb import Documents, EmbeddingFunction, Embeddings
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables
load_dotenv()

# --- 1. CONFIGURATION ---
GOOGLE_API_KEY = os.getenv('GEMINI_API_KEY')
MONGO_URL = os.getenv('MONGO_URL')
CHROMA_API_KEY = os.getenv('CHROMA_API_KEY')
CHROMA_TENANT_ID = os.getenv('CHROMA_TENANT_ID')
CHROMA_DB_NAME = os.getenv('CHROMA_DB_NAME', 'Development')

if not GOOGLE_API_KEY:
    print("[ERROR] GEMINI_API_KEY is missing.")
    exit(1)

# Configure Gemini
genai.configure(api_key=GOOGLE_API_KEY)

# --- 2. GEMINI EMBEDDING CLASS ---
class GeminiEmbeddingFunction(EmbeddingFunction):
    def __init__(self):
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
            return [[0.0] * 768 for _ in input]

def clean_text(text):
    if not text: return ""
    return re.sub(r'\s+', ' ', str(text)).strip()

def safe_meta(val):
    return "Unknown" if val is None else str(val)

def main():
    print("🚀 [START] Starting Database Population...")

    # --- 3. CONNECT TO CHROMA DB ---
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
    except Exception as e:
        print(f"[ERROR] Chroma Connection Failed: {e}")
        return

    # --- 4. PREPARE COLLECTIONS ---
    # We delete and recreate to ensure a fresh sync
    for name in ["portfolio", "Projects_data", "Blogs_data"]:
        try:
            client.delete_collection(name)
            print(f"[INFO] Cleared old collection: {name}")
        except:
            pass

    portfolio_col = client.create_collection("portfolio", embedding_function=GeminiEmbeddingFunction())
    projects_col = client.create_collection("Projects_data", embedding_function=GeminiEmbeddingFunction())
    blogs_col = client.create_collection("Blogs_data", embedding_function=GeminiEmbeddingFunction())
    
    print("✅ Collections Ready.")

    # ==========================================
    # 1. SYNC BLOGS -> 'Blogs_data'
    # ==========================================
    blog_dir = "generated_blogs"
    if not os.path.exists(blog_dir):
        blog_dir = "backend/generated_blogs" # Fallback if running from root

    if os.path.exists(blog_dir):
        files = glob.glob(f"{blog_dir}/*.json")
        print(f"[SYNC] Found {len(files)} Blogs. Syncing to 'Blogs_data'...")
        
        for i, filepath in enumerate(files):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    blog = json.load(f)
                    title = safe_meta(blog.get('title'))
                    content = safe_meta(blog.get('content'))
                    
                    # Store structured blog data
                    text = f"Blog Title: {title}. Content: {content[:15000]}..." # Limit chunk size
                    
                    blogs_col.add(
                        ids=[f"blog_{i}"], 
                        documents=[clean_text(text)], 
                        metadatas=[{"title": title, "type": "blog", "category": safe_meta(blog.get('tags', ['General'])[0])}]
                    )
            except Exception as e:
                print(f"[WARN] Skipped blog {filepath}: {e}")
    else:
        print("[WARN] No generated_blogs directory found.")

    # ==========================================
    # 2. SYNC PROJECTS -> 'Projects_data' (FROM MONGODB)
    # ==========================================
    if MONGO_URL:
        try:
            print("[SYNC] Connecting to MongoDB to fetch Projects...")
            mongo_client = MongoClient(MONGO_URL)
            db = mongo_client[os.getenv('DB_NAME', 'portfolioDB')]
            projects_cursor = db.projects.find({})
            
            count = 0
            for p in projects_cursor:
                p_name = safe_meta(p.get('name') or p.get('title'))
                p_summary = safe_meta(p.get('summary'))
                p_details = safe_meta(p.get('details'))
                p_tech = ", ".join(p.get('technologies', []))
                
                # Create rich context for the project
                text = f"Project: {p_name}. Tech Stack: {p_tech}. Summary: {p_summary}. Implementation Details: {p_details}"
                
                projects_col.add(
                    ids=[str(p.get('id', p.get('_id')))],
                    documents=[clean_text(text)],
                    metadatas=[{"name": p_name, "category": "Project", "source": "MongoDB"}]
                )
                count += 1
            print(f"✅ Synced {count} Projects from MongoDB to 'Projects_data'.")
        except Exception as e:
            print(f"[ERROR] Failed to sync projects from MongoDB: {e}")
    else:
        print("[WARN] MONGO_URL not set. Skipping Project Sync.")

    # ==========================================
    # 3. SYNC PORTFOLIO -> 'portfolio' (Resume, Skills, Experience, etc.)
    # ==========================================
    print("[SYNC] Syncing Complete Portfolio to 'portfolio'...")

    # A. Robust Resume Path Detection
    # Look in current dir, parent dir, or specifically in backend/
    current_dir = os.path.dirname(os.path.abspath(__file__))
    possible_paths = [
        os.path.join(current_dir, "Resume Details.txt"),       # Same dir as script
        os.path.join(current_dir, "../Resume Details.txt"),    # Parent dir
        "Resume Details.txt",                                  # CWD
        "backend/Resume Details.txt"                           # From root
    ]
    
    resume_found = False
    for path in possible_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    resume_content = f.read()
                    if resume_content:
                        portfolio_col.add(
                            ids=["resume_full"],
                            documents=[clean_text(resume_content)],
                            metadatas=[{"type": "resume", "title": "Full Resume"}]
                        )
                        print(f"✅ Resume synced from: {path}")
                        resume_found = True
                        break
            except Exception as e:
                print(f"[WARN] Error reading resume at {path}: {e}")

    if not resume_found:
        print("[WARN] ❌ Resume Details.txt NOT found in any expected location.")

    # B. Sync ALL Sections from JSON
    json_path = 'portfolio_data.json'
    if not os.path.exists(json_path): json_path = 'backend/portfolio_data.json'
    
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # 1. Experience (CRITICAL MISSING PIECE)
            if "experience" in data:
                for i, exp in enumerate(data["experience"]):
                    # Create a rich text description of the job
                    text = f"Role: {exp.get('role')} at {exp.get('company')}. " \
                           f"Duration: {exp.get('duration')}. " \
                           f"Description: {exp.get('description')} " \
                           f"Key Achievements: {', '.join(exp.get('achievements', []))}"
                    
                    portfolio_col.add(
                        ids=[f"exp_{i}"],
                        documents=[clean_text(text)],
                        metadatas=[{"type": "experience", "company": safe_meta(exp.get('company'))}]
                    )
                print(f"✅ Synced {len(data['experience'])} Experience entries.")

            # 2. Skills
            if "skills" in data:
                for cat, skills in data["skills"].items():
                    skill_str = ", ".join([s['name'] if isinstance(s, dict) else s for s in skills])
                    text = f"Skill Category: {cat}. Skills: {skill_str}."
                    portfolio_col.add(
                        ids=[f"skill_{cat}"],
                        documents=[clean_text(text)],
                        metadatas=[{"type": "skill", "category": cat}]
                    )
                print("✅ Synced Skills.")

            # 3. Education
            if "education" in data:
                for i, edu in enumerate(data["education"]):
                    text = f"Education: {edu.get('degree')} at {edu.get('institution')}. Year: {edu.get('year')}."
                    portfolio_col.add(
                        ids=[f"edu_{i}"],
                        documents=[clean_text(text)],
                        metadatas=[{"type": "education"}]
                    )
                print("✅ Synced Education.")
                    
            # 4. Certifications
            if "certifications" in data:
                for i, cert in enumerate(data["certifications"]):
                    text = f"Certification: {cert.get('name')} from {cert.get('issuer')}."
                    portfolio_col.add(
                        ids=[f"cert_{i}"],
                        documents=[clean_text(text)],
                        metadatas=[{"type": "certification"}]
                    )
                print("✅ Synced Certifications.")

            # 5. Achievements (MISSING)
            if "achievements" in data:
                for i, ach in enumerate(data["achievements"]):
                    text = f"Achievement: {ach.get('title')}. Details: {ach.get('description')}"
                    portfolio_col.add(
                        ids=[f"ach_{i}"],
                        documents=[clean_text(text)],
                        metadatas=[{"type": "achievement"}]
                    )
                print("✅ Synced Achievements.")

            # 6. Personal Info (MISSING)
            if "personal_info" in data:
                info = data["personal_info"]
                text = f"Personal Profile: {info.get('name')}. Title: {info.get('title')}. " \
                       f"Summary: {info.get('summary')}. Location: {info.get('location')}."
                portfolio_col.add(
                    ids=["personal_info"],
                    documents=[clean_text(text)],
                    metadatas=[{"type": "personal_info"}]
                )
                print("✅ Synced Personal Info.")

                # 7. Contacts (Specific Request)
                # Create a specialized document just for contact details for easy retrieval
                contact_text = f"Email: {info.get('email')}. Phone: {info.get('phone')}. " \
                               f"LinkedIn: {info.get('linkedin')}. Location: {info.get('location')}."
                portfolio_col.add(
                    ids=["contacts_info"],
                    documents=[clean_text(contact_text)],
                    metadatas=[{"type": "contacts", "email": safe_meta(info.get('email'))}]
                )
                print("✅ Synced Contacts.")

    else:
        print("[ERROR] ❌ portfolio_data.json not found.")

    print("🎉 [SUCCESS] All Data (Projects, Blogs, FULL Portfolio) Synced Successfully!")

if __name__ == "__main__":
    main()