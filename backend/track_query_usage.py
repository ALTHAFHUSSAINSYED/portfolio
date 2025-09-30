import os
import chromadb
from dotenv import load_dotenv
from datetime import datetime
import json
from sentence_transformers import SentenceTransformer


load_dotenv()
model = SentenceTransformer('all-MiniLM-L6-v2')

# Connect to ChromaDB Cloud
chroma_client = chromadb.CloudClient(
    api_key=os.getenv('CHROMA_API_KEY'),
    tenant=os.getenv('CHROMA_TENANT_ID'),
    database=os.getenv('CHROMA_DATABASE')
)

TRACKING_FILE = 'query_tracking_log.json'

# Initialize tracking log if not exists
if not os.path.exists(TRACKING_FILE):
    with open(TRACKING_FILE, 'w') as f:
        json.dump([], f)

def log_query(source, query_text, result_count):
    entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'source': source,  # chromadb, dynamodb, internet
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
    print(f"Collection '{collection_name}' has {doc_count} documents.")
    avg_doc_size_kb = 8
    total_size_mb = (doc_count * avg_doc_size_kb) / 1024
    print(f"Estimated total size: {total_size_mb:.2f} MB")
    return doc_count, total_size_mb

def track_chromadb_query(collection_name, query_text):
    collection = chroma_client.get_collection(name=collection_name)
    embedding = model.encode([query_text]).tolist()
    results = collection.query(query_embeddings=embedding)
    result_count = len(results['ids'])
    print(f"ChromaDB Query '{query_text}' returned {result_count} results.")
    log_query('chromadb', query_text, result_count)

def track_dynamodb_query(query_text, result_count):
    print(f"DynamoDB Query '{query_text}' returned {result_count} results.")
    log_query('dynamodb', query_text, result_count)

def track_internet_query(query_text, result_count):
    print(f"Internet Query '{query_text}' returned {result_count} results.")
    log_query('internet', query_text, result_count)

def show_tracking_summary():
    with open(TRACKING_FILE, 'r') as f:
        data = json.load(f)
    chromadb_count = sum(1 for q in data if q['source'] == 'chromadb')
    dynamodb_count = sum(1 for q in data if q['source'] == 'dynamodb')
    internet_count = sum(1 for q in data if q['source'] == 'internet')
    print(f"Total ChromaDB queries: {chromadb_count}")
    print(f"Total DynamoDB queries: {dynamodb_count}")
    print(f"Total Internet queries: {internet_count}")
    print(f"Full log: {json.dumps(data, indent=2)}")

if __name__ == "__main__":
    get_collection_stats('Blogs_data')
    get_collection_stats('Projects_data')
    # Example queries
    track_chromadb_query('Blogs_data', "AI")
    track_dynamodb_query("project search", 2)
    track_internet_query("latest AI news", 5)
    show_tracking_summary()
