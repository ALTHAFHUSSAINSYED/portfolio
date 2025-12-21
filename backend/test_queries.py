import chromadb

# Initialize ChromaDB cloud client
client = chromadb.CloudClient(
    api_key='ck-EWpGxabEbpBzHDHjj9YrSFoyRyiAtgwooUbtmJXxziXH',
    tenant='7c2da124-ba75-4ae6-85b5-ff22589f0d08',
    database='Development'
)

def test_queries():
    """Test various specific queries to verify data population"""
    collection = client.get_collection("portfolio")
    
    test_queries = [
        "What cloud platforms is Althaf experienced with?",
        "What DevOps tools does Althaf use?",
        "Tell me about Althaf's storage expertise",
        "List all of Althaf's programming skills",
        "What certifications does Althaf have from Oracle?",
        "Describe Althaf's most recent project",
        "What are Althaf's achievements and outcomes in previous roles?"
    ]
    
    print("Testing Specific Queries:\n")
    for query in test_queries:
        print(f"\nQuery: {query}")
        results = collection.query(
            query_texts=[query],
            n_results=2
        )
        
        print("\nResults:")
        for doc in results['documents'][0]:
            print(f"\n---\n{doc}")
        print("\n" + "="*50)

if __name__ == "__main__":
    test_queries()