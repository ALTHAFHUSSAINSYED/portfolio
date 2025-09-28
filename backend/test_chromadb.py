import chromadb
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# Initialize Gemini for embeddings
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Initialize ChromaDB cloud client
client = chromadb.CloudClient(
    api_key='ck-EWpGxabEbpBzHDHjj9YrSFoyRyiAtgwooUbtmJXxziXH',
    tenant='7c2da124-ba75-4ae6-85b5-ff22589f0d08',
    database='Development'
)

# Check if collection exists
try:
    collection = client.get_collection(name="portfolio")
    print("ChromaDB collection found!")
    print(f"Collection size: {collection.count()}")
    
    # Test query
    test_query = "What are Althaf's skills?"
    results = collection.query(
        query_texts=[test_query],
        n_results=2
    )
    
    if results and results['documents']:
        print("\nTest query results:")
        for doc in results['documents'][0]:
            print(f"\n---\n{doc[:200]}...")
    else:
        print("\nNo results found for test query")
        
except Exception as e:
    print(f"Error accessing ChromaDB collection: {e}")
    print("Please run generate_vector_db.py first to create the collection")