import chromadb
import os
import json
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

client = chromadb.CloudClient(
    api_key=os.getenv('CHROMA_API_KEY'),
    tenant=os.getenv('CHROMA_TENANT'),
    database=os.getenv('CHROMA_DATABASE')
)

model = SentenceTransformer('all-MiniLM-L6-v2')
class LocalEmbeddingFunction:
    def __call__(self, input):
        return model.encode(input).tolist()

BLOG_DIR = 'generated_blogs' if os.path.exists('generated_blogs') else 'backend/generated_blogs'

def main():
    print("🚀 Syncing Blogs...")
    if not os.path.exists(BLOG_DIR): 
        print(f"⚠️ Blog directory not found: {BLOG_DIR}")
        return

    # 1. WIPE
    try: 
        client.delete_collection("Blogs_data")
        print("✓ Wiped old blog data")
    except: 
        print("✓ No existing blog collection")
    
    # 2. CREATE
    coll = client.create_collection(
        name="Blogs_data",
        embedding_function=LocalEmbeddingFunction()
    )
    
    # 3. PROCESS FILES
    docs, metas, ids = [], [], []
    files = [f for f in os.listdir(BLOG_DIR) if f.endswith('.json')]
    
    for fname in files:
        with open(os.path.join(BLOG_DIR, fname), 'r') as f:
            b = json.load(f)
        
        content = b.get('content') or b.get('summary')
        docs.append(content)
        metas.append({"title": b.get('title'), "category": b.get('category')})
        ids.append(fname.replace('.json', ''))

    if docs:
        coll.add(documents=docs, metadatas=metas, ids=ids)
        print(f"✅ Blogs Synced ({len(docs)} items).")
    else:
        print("⚠️ No blog files found")

if __name__ == "__main__":
    main()
