import chromadb
import os
from dotenv import load_dotenv

load_dotenv()

CHROMA_API_KEY = os.getenv('CHROMA_API_KEY')
CHROMA_TENANT_ID = os.getenv('CHROMA_TENANT_ID')
CHROMA_DB_NAME = os.getenv('CHROMA_DB_NAME', 'Development')

def check_size():
    print(f"Connecting to DB: {CHROMA_DB_NAME}")
    try:
        if CHROMA_API_KEY:
            client = chromadb.CloudClient(
                api_key=CHROMA_API_KEY,
                tenant=CHROMA_TENANT_ID,
                database=CHROMA_DB_NAME
            )
        else:
            client = chromadb.PersistentClient(path="chroma_db")
            
        collections = client.list_collections()
        total_chars = 0
        total_docs = 0
        
        print(f"\n{'Collection':<20} | {'Docs':<5} | {'Chars':<10} | {'Est. Tokens':<10}")
        print("-" * 60)
        
        for col in collections:
            data = col.get() # Gets all
            docs = data.get('documents', [])
            
            if not docs: 
                docs = []
            
            c_len = sum(len(d) for d in docs if d)
            c_count = len(docs)
            
            total_chars += c_len
            total_docs += c_count
            
            print(f"{col.name:<20} | {c_count:<5} | {c_len:<10} | {int(c_len/4):<10}")
            
        print("-" * 60)
        print(f"{'TOTAL':<20} | {total_docs:<5} | {total_chars:<10} | {int(total_chars/4):<10}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_size()
