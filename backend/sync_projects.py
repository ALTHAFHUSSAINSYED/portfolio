import os
import json
import uuid
import chromadb
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer

load_dotenv()

# Config
MONGO_URI = os.getenv("MONGO_URL") or os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME", "portfolioDB")

# AI Setup
model = SentenceTransformer('all-MiniLM-L6-v2')
class LocalEmbeddingFunction:
    def __call__(self, input):
        return model.encode(input).tolist()

chroma = chromadb.CloudClient(
    api_key=os.getenv('CHROMA_API_KEY'),
    tenant=os.getenv('CHROMA_TENANT'),
    database=os.getenv('CHROMA_DATABASE')
)

def get_html_list(items, title):
    if not items: return ""
    html = f"<h3>{title}</h3><ul>"
    for item in items: html += f"<li>{item}</li>"
    html += "</ul>"
    return html

def main():
    print("🚀 Master Project Sync (Mongo + Chroma)...")
    
    # 1. LOAD JSON
    path = 'portfolio_data.json' if os.path.exists('portfolio_data.json') else 'backend/portfolio_data.json'
    with open(path, 'r') as f: data = json.load(f)
    projects = data.get('projects', [])

    # ---------------- MONGODB ----------------
    if MONGO_URI:
        try:
            client = MongoClient(MONGO_URI)
            db = client[DB_NAME]
            
            # Wipe & Replace
            db["projects"].delete_many({})
            print("✓ Wiped old MongoDB projects")
            
            new_docs = []
            for p in projects:
                details = ""
                if 'challenges' in p: details += get_html_list(p['challenges'], "Challenges")
                if 'solutions' in p: details += get_html_list(p['solutions'], "Solutions")
                
                new_docs.append({
                    "id": str(uuid.uuid4()),
                    "name": p.get('title'),
                    "summary": p.get('description'),
                    "details": details,
                    "image_url": p.get('image', ''),
                    "technologies": p.get('technologies', []),
                    "timestamp": datetime.utcnow()
                })
            
            if new_docs: 
                db["projects"].insert_many(new_docs)
                print(f"✅ MongoDB: Refreshed {len(new_docs)} projects.")
            client.close()
        except Exception as e:
            print(f"❌ MongoDB Error: {e}")

    # ---------------- CHROMA DB ----------------
    try:
        try: 
            chroma.delete_collection("Projects_data")
            print("✓ Wiped old ChromaDB projects")
        except: 
            print("✓ No existing ChromaDB projects collection")
        
        coll = chroma.create_collection(
            name="Projects_data",
            embedding_function=LocalEmbeddingFunction()
        )
        
        c_docs, c_metas, c_ids = [], [], []
        for i, p in enumerate(projects):
            text = f"Project: {p.get('title')}. Desc: {p.get('description')}. "
            if 'challenges' in p: text += f"Challenges: {', '.join(p['challenges'])}. "
            if 'solutions' in p: text += f"Solutions: {', '.join(p['solutions'])}. "
            if 'technologies' in p: text += f"Stack: {', '.join(p['technologies'])}."
            
            c_docs.append(text)
            c_metas.append({"title": p.get('title'), "type": "project"})
            c_ids.append(f"proj_{i}")

        if c_docs:
            coll.add(documents=c_docs, metadatas=c_metas, ids=c_ids)
            print(f"✅ ChromaDB: Refreshed {len(c_docs)} projects.")
            
    except Exception as e:
        print(f"❌ ChromaDB Error: {e}")

if __name__ == "__main__":
    main()
