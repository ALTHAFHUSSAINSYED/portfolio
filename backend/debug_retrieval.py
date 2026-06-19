import chromadb
import os
from dotenv import load_dotenv
import google.generativeai as genai
from chromadb import EmbeddingFunction, Documents, Embeddings

load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

class GeminiEmbeddingFunction(EmbeddingFunction):
    def __init__(self):
        pass
    def __call__(self, input: Documents) -> Embeddings:
        model = 'models/text-embedding-004'
        try:
            return [
                genai.embed_content(
                    model=model, content=text, task_type="retrieval_query"
                )['embedding'] for text in input
            ]
        except Exception as e:
            print(f"[ERROR] {e}")
            return [[0.0] * 768 for _ in input]

def check_retrieval():
    print("--- Debugging Retrieval for 'Skills' ---")
    client = chromadb.CloudClient(
        api_key=os.getenv('CHROMA_API_KEY'),
        tenant=os.getenv('CHROMA_TENANT_ID'),
        database=os.getenv('CHROMA_DB_NAME', 'Development')
    )
    col = client.get_collection("portfolio", embedding_function=GeminiEmbeddingFunction())
    
    query = "What are your technical skills?"
    print(f"Query: {query}")
    
    results = col.query(query_texts=[query], n_results=10)
    
    ids = results['ids'][0]
    docs = results['documents'][0]
    metas = results['metadatas'][0]
    
    print(f"\nFound {len(ids)} documents:")
    for i in range(len(ids)):
        print(f"\n{i+1}. ID: {ids[i]}")
        print(f"   Metadata: {metas[i]}")
        print(f"   Content snippet: {docs[i][:100]}...")
        if "Skill Category" in docs[i]:
            print("   ✅ CONTAINS SKILL DATA")
        else:
            print("   ❌ NO SKILL DATA")

if __name__ == "__main__":
    check_retrieval()
