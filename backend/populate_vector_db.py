import chromadb
import os
import json
import re
import glob
import boto3
from google import genai
from google.genai import types
from chromadb import Documents, EmbeddingFunction, Embeddings
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env.local'))

# --- 1. CONFIGURATION ---
GOOGLE_API_KEY = os.getenv('GEMINI_API_KEY')
MONGO_URL = os.getenv('MONGO_URL')
CHROMA_API_KEY = os.getenv('CHROMA_API_KEY')
CHROMA_TENANT_ID = os.getenv('CHROMA_TENANT_ID')
CHROMA_DB_NAME = os.getenv('CHROMA_DB_NAME', 'Development')

# ChromaDB Migration Complete (Task 21 - Jan 3, 2026)
# Now writes ONLY to portfolio_master collection
USE_LEGACY_COLLECTIONS = os.getenv('USE_LEGACY_COLLECTIONS', 'false').lower() == 'true'
print(f"ChromaDB Sync Mode: {'LEGACY (3 collections - DEPRECATED)' if USE_LEGACY_COLLECTIONS else 'UNIFIED (portfolio_master only)'}")

if not GOOGLE_API_KEY:
    print("[ERROR] GEMINI_API_KEY is missing.")
    exit(1)

# Configure Gemini Client
try:
    genai_client = genai.Client(api_key=GOOGLE_API_KEY)
except Exception as e:
    print(f"[ERROR] Failed to initialize Gemini Client: {e}")
    genai_client = None

# --- 2. GEMINI EMBEDDING CLASS ---
class GeminiEmbeddingFunction(EmbeddingFunction):
    def __init__(self):
        pass

    def __call__(self, input: Documents) -> Embeddings:
        model = 'text-embedding-004'
        try:
            if not genai_client:
                return [[0.0] * 768 for _ in input]
            return [
                genai_client.models.embed_content(
                    model=model,
                    contents=text,
                    config=types.EmbedContentConfig(
                        task_type="RETRIEVAL_DOCUMENT"
                    )
                ).embeddings[0].values
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

def write_to_portfolio_master(client, embed_function, uid, doc, meta, category, subcategory=None):
    """Write data to portfolio_master collection with category tagging (Task 21 - Migration Complete)
    
    Args:
        client: ChromaDB client
        embed_function: GeminiEmbeddingFunction instance
        uid: Unique ID for the document
        doc: Document text content
        meta: Original metadata dict
        category: Main category ('profile', 'project', 'blog')
        subcategory: Optional subcategory (e.g., blog's Cloud Computing/DevOps)
    
    Returns:
        bool: Success status
    """
    try:
        # Write ONLY to portfolio_master (unified collection)
        master_col = client.get_or_create_collection('portfolio_master', embedding_function=embed_function)
        
        # Add category tags to metadata
        master_meta = meta.copy()
        master_meta['category'] = category
        if subcategory:
            master_meta['subcategory'] = subcategory
        
        existing = master_col.get(ids=[uid])
        if not existing or not existing['ids']:
            master_col.add(ids=[uid], documents=[doc], metadatas=[master_meta])
            print(f"[OK] Added to portfolio_master: {uid} (category={category})")
        else:
            existing_doc = existing['documents'][0] if existing['documents'] else None
            if existing_doc != doc:
                master_col.upsert(ids=[uid], documents=[doc], metadatas=[master_meta])
                print(f"[UPDATE] Content changed for {uid}. Updated in portfolio_master.")
            else:
                print(f"[SKIP] Matches existing data in portfolio_master: {uid}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to write {uid} to portfolio_master: {e}")
        return False

def sync_blogs_from_s3(chroma_client, embed_function):
    """
    Sync all blogs from S3 bucket (source of truth) to ChromaDB portfolio_master collection.
    Downloads index.json from S3 and embeds each blog with category='blog'.
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
            timestamp = safe_meta(blog.get('created_at', ''))  # Fixed: Use snake_case
            published_date = timestamp[:10] if len(timestamp) >= 10 else ''
            
            metadata = {
                "title": title,
                "category": blog_category,
                "url": url,
                "timestamp": timestamp,
                "published_date": published_date,
                "metadata_category": "blogs"  # Enhanced RAG tag
            }
            
            # Use dual_write_with_category helper
            success = write_to_portfolio_master(
                chroma_client,
                embed_function,
                blog_id,
                clean_text(content),
                metadata,
                category='blog',
                subcategory=blog_category
            )
            
            if success:
                synced_count += 1
                master_success_count += 1
                print(f"  ✅ Synced: {title[:50]}...")
            else:
                skipped_count += 1
                print(f"  ❌ Failed to sync {blog_id}")
        
        print(f"\n📊 S3 Sync Summary: {synced_count} synced, {skipped_count} skipped")
        print(f"   └─ Master (portfolio_master): {master_success_count}")
        
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
    # We use get_or_create to preserve existing data (Smart Sync), falling back to get_collection on conflict
    try:
        portfolio_col = client.get_or_create_collection("portfolio", embedding_function=GeminiEmbeddingFunction())
    except Exception:
        portfolio_col = client.get_collection("portfolio")
        
    try:
        projects_col = client.get_or_create_collection("Projects_data", embedding_function=GeminiEmbeddingFunction())
    except Exception:
        projects_col = client.get_collection("Projects_data")
        
    try:
        blogs_col = client.get_or_create_collection("Blogs_data", embedding_function=GeminiEmbeddingFunction())
    except Exception:
        blogs_col = client.get_collection("Blogs_data")
    
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
                    success = write_to_portfolio_master(
                        client,
                        GeminiEmbeddingFunction(),
                        b_id,
                        clean_text(text),
                        metadata,
                        category='blog',
                        subcategory=blog_cat
                    )
                    if success:
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
                metadata = {
                    "name": p_name,
                    "category": "Project",
                    "source": "MongoDB",
                    "metadata_category": "projects"  # Enhanced RAG tag
                }
                
                # Dual-write for projects
                success = write_to_portfolio_master(
                    client,
                    GeminiEmbeddingFunction(),
                    p_id,
                    clean_text(text),
                    metadata,
                    category='project'
                )
                if success:
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
                        success = write_to_portfolio_master(
                            client,
                            GeminiEmbeddingFunction(),
                            "resume_full",
                            clean_text(resume_content),
                            metadata,
                            category='profile'
                        )
                        if success:
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
                    
                    write_to_portfolio_master(
                        client,
                        GeminiEmbeddingFunction(),
                        f"exp_{i}",
                        clean_text(text),
                        metadata,
                        category='profile'
                    )

            # 2. Skills with Enhanced Metadata
            if "skills" in data:
                for cat, skills in data["skills"].items():
                    skill_str = ", ".join([s['name'] if isinstance(s, dict) else s for s in skills])
                    text = f"Skill Category: {cat}. Skills: {skill_str}."
                    metadata = {
                        "type": "skill",
                        "category": cat,
                        "metadata_category": "personal"  # Enhanced RAG tag
                    }
                    
                    write_to_portfolio_master(
                        client,
                        GeminiEmbeddingFunction(),
                        f"skill_{cat}",
                        clean_text(text),
                        metadata,
                        category='profile'
                    )

            # 3. Education with Enhanced Metadata
            if "education" in data:
                for i, edu in enumerate(data["education"]):
                    degree = edu.get('degree', 'Unknown')
                    institution = edu.get('institution', 'Unknown')
                    year = edu.get('year', 'Unknown')
                    
                    text = f"Education: {degree} at {institution}. Year: {year}."
                    metadata = {
                        "type": "education",
                        "degree": degree,
                        "institution": institution,
                        "metadata_category": "education"  # Enhanced RAG tag
                    }
                    write_to_portfolio_master(
                        client,
                        GeminiEmbeddingFunction(),
                        f"edu_{i}",
                        clean_text(text),
                        metadata,
                        category='profile'
                    )

            # 4. Certifications with Enhanced Metadata
            if "certifications" in data:
                for i, cert in enumerate(data["certifications"]):
                    cert_name = cert.get('name', 'Unknown')
                    issuer = cert.get('issuer', 'Unknown')
                    
                    text = f"Certification: {cert_name} from {issuer}."
                    metadata = {
                        "type": "certification",
                        "name": cert_name,
                        "issuer": issuer,
                        "metadata_category": "certifications"  # Enhanced RAG tag
                    }
                    write_to_portfolio_master(
                        client,
                        GeminiEmbeddingFunction(),
                        f"cert_{i}",
                        clean_text(text),
                        metadata,
                        category='profile'
                    )

            # 5. Achievements with Enhanced Metadata
            if "achievements" in data:
                for i, ach in enumerate(data["achievements"]):
                    achievement_title = ach.get('title', 'Unknown')
                    description = ach.get('description', '')
                    
                    text = f"Achievement: {achievement_title}. Details: {description}"
                    metadata = {
                        "type": "achievement",
                        "title": achievement_title,
                        "metadata_category": "achievements"  # Enhanced RAG tag
                    }
                    write_to_portfolio_master(
                        client,
                        GeminiEmbeddingFunction(),
                        f"ach_{i}",
                        clean_text(text),
                        metadata,
                        category='profile'
                    )

            # 6. Personal Info (About Me) with Enhanced Metadata
            if "personal_info" in data:
                info = data["personal_info"]
                name = info.get('name', 'Unknown')
                title = info.get('title', 'Unknown')
                summary = info.get('summary', '')
                location = info.get('location', '')
                
                text = f"Personal Profile: {name}. Title: {title}. " \
                       f"Summary: {summary}. Location: {location}."
                metadata = {
                    "type": "personal_info",
                    "name": name,
                    "title": title,
                    "metadata_category": "personal"  # Enhanced RAG tag (about me)
                }
                
                write_to_portfolio_master(
                    client,
                    GeminiEmbeddingFunction(),
                    "personal_info",
                    clean_text(text),
                    metadata,
                    category='profile'
                )

                # 7. Contacts with Enhanced Metadata (including website/portfolio)
                email = info.get('email', '')
                phone = info.get('phone', '')
                linkedin = info.get('linkedin', '')
                github = info.get('github', '')
                website = info.get('website', 'https://www.althafportfolio.site')
                portfolio_url = info.get('portfolio', 'https://www.althafportfolio.site')
                
                contact_text = f"Email: {email}. Phone: {phone}. " \
                               f"LinkedIn: {linkedin}. GitHub: {github}. " \
                               f"Website: {website}. Portfolio: {portfolio_url}. Location: {location}."
                contact_metadata = {
                    "type": "contacts",
                    "email": safe_meta(email),
                    "phone": safe_meta(phone),
                    "website": safe_meta(website),
                    "portfolio": safe_meta(portfolio_url),
                    "metadata_category": "contact"  # Enhanced RAG tag
                }
                
                write_to_portfolio_master(
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