import os
import chromadb
from dotenv import load_dotenv
from datetime import datetime, timedelta
import json
from sentence_transformers import SentenceTransformer

load_dotenv()
model = SentenceTransformer('all-MiniLM-L6-v2')

chroma_client = chromadb.CloudClient(
    api_key=os.getenv('CHROMA_API_KEY'),
    tenant=os.getenv('CHROMA_TENANT_ID'),
    database=os.getenv('CHROMA_DATABASE')
)

TRACKING_FILE = 'query_tracking_log.json'
QUERY_LIMIT_PER_DAY = 50
STORAGE_LIMIT_MB = 900
BLOG_COLLECTION = 'Blogs_data'

# Initialize tracking log if not exists
if not os.path.exists(TRACKING_FILE):
    with open(TRACKING_FILE, 'w') as f:
        json.dump([], f)

def log_query(source, query_text, result_count):
    entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'source': source,
        'query': query_text,
        'result_count': result_count
    }
    with open(TRACKING_FILE, 'r+') as f:
        data = json.load(f)
        data.append(entry)
        f.seek(0)
        json.dump(data, f, indent=2)
        f.truncate()

def get_collection_stats(collection_name):
    collection = chroma_client.get_collection(name=collection_name)
    ids = collection.get(ids=None)['ids']
    doc_count = len(ids)
    avg_doc_size_kb = 8
    total_size_mb = (doc_count * avg_doc_size_kb) / 1024
    return doc_count, total_size_mb, ids

def enforce_storage_limit():
    doc_count, total_size_mb, ids = get_collection_stats(BLOG_COLLECTION)
    if total_size_mb < STORAGE_LIMIT_MB:
        print(f"Storage is within limit: {total_size_mb:.2f} MB")
        return
    print(f"Storage ({total_size_mb:.2f} MB) exceeds limit. Deleting old blogs...")
    collection = chroma_client.get_collection(name=BLOG_COLLECTION)
    # Fetch metadata for all blogs
    blogs = collection.get(ids=ids)
    # Find blogs older than 3 months
    three_months_ago = datetime.utcnow() - timedelta(days=90)
    to_delete = []
    for i, meta in enumerate(blogs['metadatas']):
        created_at = meta.get('created_at')
        if created_at:
            try:
                created_dt = datetime.fromisoformat(created_at)
            except Exception:
                continue
            if created_dt < three_months_ago:
                to_delete.append(blogs['ids'][i])
    if to_delete:
        print(f"Deleting {len(to_delete)} old blogs...")
        collection.delete(ids=to_delete)
    else:
        print("No blogs older than 3 months to delete.")

def get_today_query_count():
    today = datetime.utcnow().date()
    with open(TRACKING_FILE, 'r') as f:
        data = json.load(f)
    count = sum(1 for q in data if q['source'] == 'chromadb' and datetime.fromisoformat(q['timestamp']).date() == today)
    return count

def track_chromadb_query(collection_name, query_text):
    if get_today_query_count() >= QUERY_LIMIT_PER_DAY:
        print(f"Daily query limit ({QUERY_LIMIT_PER_DAY}) reached. Query not executed.")
        return
    collection = chroma_client.get_collection(name=collection_name)
    embedding = model.encode([query_text]).tolist()
    results = collection.query(query_embeddings=embedding)
    result_count = len(results['ids'])
    print(f"ChromaDB Query '{query_text}' returned {result_count} results.")
    log_query('chromadb', query_text, result_count)

def show_tracking_summary():
    with open(TRACKING_FILE, 'r') as f:
        data = json.load(f)
    chromadb_count = sum(1 for q in data if q['source'] == 'chromadb')
    print(f"Total ChromaDB queries: {chromadb_count}")
    print(f"Full log: {json.dumps(data, indent=2)}")

if __name__ == "__main__":
    enforce_storage_limit()
    # Example query
    track_chromadb_query(BLOG_COLLECTION, "AI")
    show_tracking_summary()
