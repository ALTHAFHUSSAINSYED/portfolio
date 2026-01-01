import chromadb
import os
import json
import re
import glob
import boto3
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

# ChromaDB Migration Toggle (Task 13)
USE_LEGACY_COLLECTIONS = os.getenv('USE_LEGACY_COLLECTIONS', 'false').lower() == 'true'
print(f"ChromaDB Sync Mode: {'LEGACY (3 collections)' if USE_LEGACY_COLLECTIONS else 'DUAL-WRITE (legacy + portfolio_master)'}")

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

def dual_write_with_category(client, embed_function, uid, doc, meta, category, subcategory=None):
    """Helper function for dual-write with category tagging (Task 13)
    
    Writes data to both legacy collection AND portfolio_master with category tags.
    
    Args:
        client: ChromaDB client
        embed_function: GeminiEmbeddingFunction instance
        uid: Unique ID for the document
        doc: Document text content
        meta: Original metadata dict
        category: Main category ('profile', 'project', 'blog')
        subcategory: Optional subcategory (e.g., blog's DevOps/Cloud category)
    
    Returns:
        Tuple (legacy_success, master_success)
    """
    legacy_success = False
    master_success = False
    
    # Determine legacy collection based on category
    if category == 'profile':
        legacy_col_name = 'portfolio'
    elif category == 'project':
        legacy_col_name = 'Projects_data'
    elif category == 'blog':
        legacy_col_name = 'Blogs_data'
    else:
        print(f"[WARN] Unknown category '{category}' for ID {uid}")
        return (False, False)
    
    try:
        # 1. Write to legacy collection (if enabled)
        if USE_LEGACY_COLLECTIONS or True:  # Always write to legacy during dual-write phase
            legacy_col = client.get_or_create_collection(legacy_col_name, embedding_function=embed_function)
            existing = legacy_col.get(ids=[uid])
            if not existing or not existing['ids']:
                legacy_col.add(ids=[uid], documents=[doc], metadatas=[meta])
                legacy_success = True
            else:
                legacy_success = True  # Already exists, count as success
        
        # 2. Write to portfolio_master (unified collection)
        if not USE_LEGACY_COLLECTIONS or True:  # Always write to master during dual-write phase
            master_col = client.get_or_create_collection('portfolio_master', embedding_function=embed_function)
            
            # Add category tags to metadata
            master_meta = meta.copy()
            master_meta['category'] = category
            if subcategory:
                master_meta['subcategory'] = subcategory
            
            existing = master_col.get(ids=[uid])
            if not existing or not existing['ids']:
                master_col.add(ids=[uid], documents=[doc], metadatas=[master_meta])
                master_success = True
            else:
                master_success = True  # Already exists, count as success
        
        return (legacy_success, master_success)
        
    except Exception as e:
        print(f"[ERROR] Dual-write failed for {uid}: {e}")
        return (legacy_success, master_success)

def sync_blogs_from_s3(chroma_client, embed_function):
    """
    Sync all blogs from S3 bucket (source of truth) to ChromaDB Blogs_data collection.
    Downloads index.json from S3 and embeds each blog.
    """
    print("\n📚 [BLOGS] Syncing blogs from S3...")
    
    try:
        s3 = boto3.client('s3')
        bucket = os.getenv('S3_BLOG_BUCKET', 'althaf-blogs-storage')
        
        # Download index.json from S3
        try:
            response = s3.get_object(Bucket=bucket, Key='blogs/index.json')
            index_data = json.loads(response['Body'].read().decode('utf-8'))
            
            # Handle nested structure: {"blogs": [...]}
            if isinstance(index_data, dict):
                if 'blogs' in index_data:
                    # Extract blogs array from wrapper
                    index_data = index_data['blogs']
                else:
                    # Single blog object - wrap in list
                    index_data = [index_data]
            
            print(f"✅ Found {len(index_data)} blogs in S3 index.json")
        except Exception as e:
            print(f"❌ Could not fetch S3 index.json: {e}")
            return
        
        # Dual-write mode: Track both legacy and master collections
        synced_count = 0
        skipped_count = 0
        legacy_success_count = 0
        master_success_count = 0
        
        for blog in index_data:
            blog_id = blog.get('id')
            if not blog_id:
                continue
            
            # Prepare content for embedding
            content = blog.get('content', '')
            if not content:
                # Fallback to description if content missing
                content = blog.get('description', blog.get('title', ''))
            
            if not content or len(content) < 50:
                print(f"⚠️ Skipping {blog_id}: Content too short")
                continue
            
            # Dual-write with category tagging (Task 13)
            title = safe_meta(blog.get('title', 'Untitled'))
            blog_category = safe_meta(blog.get('category', 'General'))
            url = f"https://althafportfolio.site/blogs/{blog_id}"
            timestamp = safe_meta(blog.get('createdAt', ''))
            published_date = timestamp[:10] if len(timestamp) >= 10 else ''
            
            metadata = {
                "title": title,
                "category": blog_category,
                "url": url,
                "timestamp": timestamp,
                "published_date": published_date
            }
            
            # Use dual_write_with_category helper
            legacy_ok, master_ok = dual_write_with_category(
                chroma_client,
                embed_function,
                blog_id,
                clean_text(content),
                metadata,
                category='blog',
                subcategory=blog_category
            )
            
            if legacy_ok:
                legacy_success_count += 1
            if master_ok:
                master_success_count += 1
            if legacy_ok or master_ok:
                synced_count += 1
                print(f"  ✅ Synced: {title[:50]}...")
            else:
                skipped_count += 1
                print(f"  ❌ Failed to sync {blog_id}")
        
        print(f"\n📊 S3 Sync Summary: {synced_count} synced, {skipped_count} skipped")
        print(f"   └─ Legacy (Blogs_data): {legacy_success_count} | Master (portfolio_master): {master_success_count}")
        
    except Exception as e:
        print(f"❌ S3 sync failed: {e}")
        import traceback
        traceback.print_exc()

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
    # We use get_or_create to preserve existing data (Smart Sync)
    portfolio_col = client.get_or_create_collection("portfolio", embedding_function=GeminiEmbeddingFunction())
    projects_col = client.get_or_create_collection("Projects_data", embedding_function=GeminiEmbeddingFunction())
    blogs_col = client.get_or_create_collection("Blogs_data", embedding_function=GeminiEmbeddingFunction())
    
    print("✅ Collections Ready (Persistent Mode).")

    def upsert_if_new(collection, uid, doc, meta):
        """Upserts data only if it doesn't exist yet (avoid duplicates)."""
        try:
            # Check if ID exists (lightweight)
            existing = collection.get(ids=[uid])
            if existing and existing['ids']:
                # print(f"[SKIP] {uid} already exists.") # Verbose off
                return False  # Already exists, skip
            
            # Add if missing
            collection.add(ids=[uid], documents=[doc], metadatas=[meta])
            print(f"[ADD] + Inserted new item: {uid}")
            return True
        except Exception as e:
            print(f"[ERR] Failed to insert {uid}: {e}")
            return False

    # ==========================================
    # 1. SYNC BLOGS FROM S3 -> 'Blogs_data'
    # ==========================================
    sync_blogs_from_s3(client, GeminiEmbeddingFunction())

    # ==========================================
    # 2. SYNC LOCAL BLOGS (LEGACY FALLBACK)
    # ==========================================
    blog_dir = "generated_blogs"
    if not os.path.exists(blog_dir):
        blog_dir = "backend/generated_blogs" # Fallback if running from root

    if os.path.exists(blog_dir):
        files = glob.glob(f"{blog_dir}/*.json")
        print(f"[SYNC] Scanning {len(files)} local blogs...")
        
        new_blogs = 0
        for i, filepath in enumerate(files):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    blog = json.load(f)
                    
                    # Use stable ID from filename or content
                    b_id = blog.get('id') or os.path.basename(filepath).replace('.json', '')
                    title = safe_meta(blog.get('title'))
                    content = safe_meta(blog.get('content'))
                    
                    # Store structured blog data
                    text = f"Blog Title: {title}. Content: {content[:4000]}..." # Limit chunk size (Safe < 16KB)
                    blog_cat = safe_meta(blog.get('tags', ['General'])[0])
                    metadata = {"title": title, "type": "blog", "category": blog_cat}
                    
                    # Dual-write for local blogs
                    legacy_ok, master_ok = dual_write_with_category(
                        client,
                        GeminiEmbeddingFunction(),
                        b_id,
                        clean_text(text),
                        metadata,
                        category='blog',
                        subcategory=blog_cat
                    )
                    if legacy_ok or master_ok:
                        new_blogs += 1
                        
            except Exception as e:
                print(f"[WARN] Skipped blog {filepath}: {e}")
        
        if new_blogs > 0:
            print(f"✅ Added {new_blogs} new blogs.")
        else:
            print("✅ All blogs up to date.")
    else:
        print("[WARN] No generated_blogs directory found.")

    # ==========================================
    # 2. SYNC PROJECTS -> 'Projects_data' (FROM MONGODB)
    # ==========================================
    if MONGO_URL:
        try:
            print("[SYNC] Checking MongoDB Projects...")
            mongo_client = MongoClient(MONGO_URL)
            db = mongo_client[os.getenv('DB_NAME', 'portfolioDB')]
            projects_cursor = db.projects.find({})
            
            new_projs = 0
            for p in projects_cursor:
                p_id = str(p.get('id', p.get('_id')))
                p_name = safe_meta(p.get('name') or p.get('title'))
                p_summary = safe_meta(p.get('summary'))
                p_details = safe_meta(p.get('details'))
                p_tech = ", ".join(p.get('technologies', []))
                
                # Create rich context for the project
                text = f"Project: {p_name}. Tech Stack: {p_tech}. Summary: {p_summary}. Implementation Details: {p_details}"
                metadata = {"name": p_name, "category": "Project", "source": "MongoDB"}
                
                # Dual-write for projects
                legacy_ok, master_ok = dual_write_with_category(
                    client,
                    GeminiEmbeddingFunction(),
                    p_id,
                    clean_text(text),
                    metadata,
                    category='project'
                )
                if legacy_ok or master_ok:
                    new_projs += 1
                    
            if new_projs > 0:
                print(f"✅ Added {new_projs} new projects.")
            else:
                print("✅ All projects up to date.")
                
        except Exception as e:
            print(f"[ERROR] Failed to sync projects from MongoDB: {e}")
    else:
        print("[WARN] MONGO_URL not set. Skipping Project Sync.")

    # ==========================================
    # 3. SYNC PORTFOLIO -> 'portfolio' (Resume, Skills, Experience, etc.)
    # ==========================================
    print("[SYNC] Verifying Portfolio Static Data...")

    # A. Robust Resume Path Detection
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
                        metadata = {"type": "resume", "title": "Full Resume"}
                        legacy_ok, master_ok = dual_write_with_category(
                            client,
                            GeminiEmbeddingFunction(),
                            "resume_full",
                            clean_text(resume_content),
                            metadata,
                            category='profile'
                        )
                        if legacy_ok or master_ok:
                            resume_found = True
                            break
            except Exception as e:
                print(f"[WARN] Error reading resume at {path}: {e}")
                
    if not resume_found:
        print("[WARN] ❌ Resume Details.txt NOT found.")

    # B. Sync ALL Sections from JSON
    json_path = 'portfolio_data.json'
    if not os.path.exists(json_path): json_path = 'backend/portfolio_data.json'
    
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # 1. Experience
            if "experience" in data:
                for i, exp in enumerate(data["experience"]):
                    text = f"Role: {exp.get('role')} at {exp.get('company')}. " \
                           f"Duration: {exp.get('duration')}. " \
                           f"Description: {exp.get('description')} " \
                           f"Key Achievements: {', '.join(exp.get('achievements', []))}"
                    metadata = {"type": "experience", "company": safe_meta(exp.get('company'))}
                    
                    dual_write_with_category(
                        client,
                        GeminiEmbeddingFunction(),
                        f"exp_{i}",
                        clean_text(text),
                        metadata,
                        category='profile'
                    )

            # 2. Skills
            if "skills" in data:
                for cat, skills in data["skills"].items():
                    skill_str = ", ".join([s['name'] if isinstance(s, dict) else s for s in skills])
                    text = f"Skill Category: {cat}. Skills: {skill_str}."
                    metadata = {"type": "skill", "category": cat}
                    
                    dual_write_with_category(
                        client,
                        GeminiEmbeddingFunction(),
                        f"skill_{cat}",
                        clean_text(text),
                        metadata,
                        category='profile'
                    )

            # 3. Education
            if "education" in data:
                for i, edu in enumerate(data["education"]):
                    text = f"Education: {edu.get('degree')} at {edu.get('institution')}. Year: {edu.get('year')}."
                    metadata = {"type": "education"}
                    dual_write_with_category(
                        client,
                        GeminiEmbeddingFunction(),
                        f"edu_{i}",
                        clean_text(text),
                        metadata,
                        category='profile'
                    )

            # 4. Certifications
            if "certifications" in data:
                for i, cert in enumerate(data["certifications"]):
                    text = f"Certification: {cert.get('name')} from {cert.get('issuer')}."
                    metadata = {"type": "certification"}
                    dual_write_with_category(
                        client,
                        GeminiEmbeddingFunction(),
                        f"cert_{i}",
                        clean_text(text),
                        metadata,
                        category='profile'
                    )

            # 5. Achievements
            if "achievements" in data:
                for i, ach in enumerate(data["achievements"]):
                    text = f"Achievement: {ach.get('title')}. Details: {ach.get('description')}"
                    metadata = {"type": "achievement"}
                    dual_write_with_category(
                        client,
                        GeminiEmbeddingFunction(),
                        f"ach_{i}",
                        clean_text(text),
                        metadata,
                        category='profile'
                    )

            # 6. Personal Info
            if "personal_info" in data:
                info = data["personal_info"]
                text = f"Personal Profile: {info.get('name')}. Title: {info.get('title')}. " \
                       f"Summary: {info.get('summary')}. Location: {info.get('location')}."
                metadata = {"type": "personal_info"}
                
                dual_write_with_category(
                    client,
                    GeminiEmbeddingFunction(),
                    "personal_info",
                    clean_text(text),
                    metadata,
                    category='profile'
                )

                # 7. Contacts
                contact_text = f"Email: {info.get('email')}. Phone: {info.get('phone')}. " \
                               f"LinkedIn: {info.get('linkedin')}. Location: {info.get('location')}."
                contact_metadata = {"type": "contacts", "email": safe_meta(info.get('email'))}
                
                dual_write_with_category(
                    client,
                    GeminiEmbeddingFunction(),
                    "contacts_info",
                    clean_text(contact_text),
                    contact_metadata,
                    category='profile'
                )
                    
        print("✅ Static Portfolio Data checked.")
    else:
        print("[ERROR] ❌ portfolio_data.json not found.")

    print("🎉 [SUCCESS] Smart Sync Complete. No duplicates added.")

if __name__ == "__main__":
    main()