import os
import chromadb
import google.generativeai as genai
from chromadb import EmbeddingFunction, Documents, Embeddings
from dotenv import load_dotenv

import traceback

# Load env vars
load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')
print(f"[DEBUG] GEMINI_API_KEY Loaded: {bool(api_key)}, Length: {len(api_key) if api_key else 0}", flush=True)

# Configure Gemini
genai.configure(api_key=api_key)

# Debug: List models
try:
    print("[DEBUG] Listing available models:", flush=True)
    for m in genai.list_models():
        if 'embed' in m.name or 'gemini' in m.name:
            print(f" - {m.name}", flush=True)
except Exception as e:
    print(f"[ERROR] Failed to list models: {e}", flush=True)

# --- EMBEDDING FUNCTION (Copied from server.py) ---
class GeminiEmbeddingFunction(EmbeddingFunction):
    def __init__(self):
        pass

    def __call__(self, input: Documents) -> Embeddings:
        try:
            return [
                genai.embed_content(
                    model='models/text-embedding-004',
                    content=text,
                    task_type="retrieval_query" 
                )['embedding']
                for text in input
            ]
        except Exception as e:
            print(f"Embedding failed: {e}", flush=True)
            return [[0.0] * 768 for _ in input]

def get_portfolio_context(query: str) -> str:
    all_context = []
    try:
        chroma_api_key = os.getenv('CHROMA_API_KEY')
        chroma_tenant = os.getenv('CHROMA_TENANT_ID') # User env might use ID
        chroma_database = os.getenv('CHROMA_DATABASE', 'Development') # Default to Development
        
        print(f"[INFO] Connecting to Chroma: DB={chroma_database}", flush=True)
        
        chroma_client = chromadb.CloudClient(
            api_key=chroma_api_key,
            tenant=chroma_tenant,
            database=chroma_database
        )
        
        collection_names = ['portfolio', 'Blogs_data', 'Projects_data']
        
        for collection_name in collection_names:
            try:
                print(f"[DEBUG] Getting collection object: {collection_name}...", flush=True)
                collection = chroma_client.get_collection(
                    name=collection_name,
                    embedding_function=GeminiEmbeddingFunction()
                )
                # Prioritization Rules (User Request):
                # 1. Portfolio: Fetch ALL relevant items (Limit 20 covering skills, exp, basic info)
                # 2. Projects: Fetch top 3
                # 3. Blogs: Fetch top 5 for tech context
                if collection_name == 'portfolio':
                    limit = 20 
                elif collection_name == 'Projects_data':
                    limit = 3
                else: 
                    limit = 5
                
                print(f"[INFO] Querying collection: {collection_name} (Limit: {limit})", flush=True)
                results = collection.query(query_texts=[query], n_results=limit)
                print(f"[DEBUG] Query returned.", flush=True)
                
                docs = results.get('documents', [[]])[0]
                if docs:
                    print(f"   -> Found {len(docs)} docs in {collection_name}", flush=True)
                    # Label the context with source for better LLM understanding
                    labeled_docs = [f"[Source: {collection_name}]\n{d}" for d in docs]
                    all_context.extend(labeled_docs)
                else:
                    print(f"   -> No relevant docs in {collection_name}", flush=True)
                    
            except Exception as e:
                print(f"[WARN] Skipping collection {collection_name}: {e}", flush=True)
                continue
        
        return '\n\n'.join(all_context)
    except Exception as e:
        print(f"[ERROR] ChromaDB Error: {e}", flush=True)
        return ""

def test_bot(query: str):
    print(f"\n--- Testing Allu Bot with Query: '{query}' ---", flush=True)
    
    # 1. Retrieve Context
    context = get_portfolio_context(query)
    
    if not context:
        print("[FAIL] No context retrieved from Vector DB.", flush=True)
        return

    print(f"\n[INFO] Context Retrieved ({len(context)} chars). generating answer...", flush=True)
    
    # 2. Generate Answer
    try:
        # Use 'models/gemma-3-12b-it' as per server.py
        
        system_instruction = f"""You are 'Allu Bot', the AI portfolio assistant for Althaf Hussain Syed.
        Your Persona:
        - You are an assistant, NOT Althaf. Refer to him as "Althaf" or "He".
        - You are professional, concise, and helpful.
        
        Strict Rules:
        1. **Intent Classification**: First, determine the user's intent.
           - **Social/Conversational**: functionality (Greetings, Compliments, Small Talk, Frustration). -> **Action**: Respond naturally, intelligently, and empathetically. Do NOT use the refusal message. Be human-like.
           - **Self-Query**: "Who are you?", "How do you work?" -> **Action**: Say "I am an AI assistant. My name is Allu bot. I am powered by Google Gemini and use RAG to search Althaf's portfolio to provide accurate answers."
           - **Portfolio Information**: Questions about Skills, Projects, Experience, Contact. -> **Action**: Answer ONLY using the Context below.
        
        2. **Refusal Logic (Only for Irrelevant Information)**:
           - IF the user asks for factual information NOT in the Context (e.g., "Capital of Mars", "Recipe for pizza"), AND it is NOT a social query:
           - THEN say: "Sorry, the question asked is not related to the portfolio. I can't answer you that question. Try something else related to the portfolio."
        
        3. **Zero Hallucination**: Never invent skills or projects.
        
        Context: {context}"""
        
        # Primary Model: Gemini Flash Latest (Best for Context)
        try:
            # Switch to Gemini Flash (Standard Alias)
            model = genai.GenerativeModel('models/gemini-flash-latest')
            print(f"[INFO] Using Primary Model: models/gemini-flash-latest", flush=True)
            response = model.generate_content(f"{system_instruction}\nUser: {query}")
        except Exception as e:
            print(f"[WARN] Primary model failed ({e}). Switching to Fallback: Gemma 12b", flush=True)
            # Fallback Model: Gemma 3 12b IT (User requested "Gamma")
            model = genai.GenerativeModel('models/gemma-3-12b-it')
            print(f"[INFO] Using Fallback Model: models/gemma-3-12b-it", flush=True)
            response = model.generate_content(f"{system_instruction}\nUser: {query}")
        
        print("\n--- BOT RESPONSE ---", flush=True)
        print(response.text, flush=True)
        print("--------------------", flush=True)
        
    except Exception as e:
        print(f"[ERROR] Generation failed: {e}", flush=True)

if __name__ == "__main__":
    # Test Technical Blog RAG
    queries = [
        "What are the six categories of technologies mentioned in the blogs?", 
        "Tell me about the DevOps and AWS concepts discussed in the blogs.",
    ]
    
    for q in queries:
        test_bot(q)
        print("\n" + "="*50 + "\n")
