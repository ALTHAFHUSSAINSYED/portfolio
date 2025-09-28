import chromadb
from chromadb.config import Settings
import json
import os

# Initialize ChromaDB client
client = chromadb.HttpClient(
    host='3.7.170.14',
    port=8000,
    settings=Settings(allow_reset=True)
)

# Get the collection
collection = client.get_collection("portfolio_data")

print("\nTesting blog-specific queries:\n")

test_queries = [
    "Explain to me about the blog on Docker containers",
    "What is the main topic of the blog about cloud computing?",
    "Give me a summary of the blog about DevOps",
    "What are the key points discussed in the blog about Kubernetes?",
]

for query in test_queries:
    print(f"Query: {query}")
    results = collection.query(
        query_texts=[query],
        n_results=2,
        where={"category": "blogs"}  # Filter to only get blog content
    )
    
    print("---")
    for doc in results['documents'][0]:
        print(doc)
        print("---")
    print()