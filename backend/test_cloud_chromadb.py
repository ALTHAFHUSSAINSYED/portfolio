from chromadb.config import Settings
import chromadb

# Initialize ChromaDB cloud client
client = chromadb.CloudClient(
    api_key='ck-EWpGxabEbpBzHDHjj9YrSFoyRyiAtgwooUbtmJXxziXH',
    tenant='7c2da124-ba75-4ae6-85b5-ff22589f0d08',
    database='Development'
)

try:
    # Try to get existing collection
    collection = client.get_or_create_collection(name="portfolio")
    print("Connected to ChromaDB cloud collection!")
    print(f"Collection name: {collection.name}")
    print(f"Collection metadata: {collection.metadata}")

    # Sample data
    documents = [
        "Althaf Hussain Syed is a highly skilled DevOps Engineer with expertise in cloud technologies and infrastructure automation.",
        "Key skills include AWS, GCP, Azure, Docker, Kubernetes, and Python.",
        "Currently working as Analyst III Infrastructure Services / DevOps Engineer at DXC Technology."
    ]
    
    # Add documents
    collection.add(
        documents=documents,
        metadatas=[{"source": "profile"}, {"source": "skills"}, {"source": "experience"}],
        ids=["doc1", "doc2", "doc3"]
    )
    
    # Test query
    results = collection.query(
        query_texts=["What are Althaf's technical skills?"],
        n_results=2
    )
    
    print("\nQuery results:")
    for doc in results['documents'][0]:
        print(f"\n---\n{doc}")

except Exception as e:
    print(f"Error: {e}")