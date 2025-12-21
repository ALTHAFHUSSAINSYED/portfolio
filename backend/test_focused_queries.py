import chromadb

def test_focused_queries():
    # Initialize ChromaDB cloud client
    client = chromadb.CloudClient(
        api_key='ck-EWpGxabEbpBzHDHjj9YrSFoyRyiAtgwooUbtmJXxziXH',
        tenant='7c2da124-ba75-4ae6-85b5-ff22589f0d08',
        database='Development'
    )
    
    # Get the collection
    collection = client.get_collection("portfolio")
    
    # Test category-specific queries with metadata filtering
    test_cases = [
        {
            "category": "skills",
            "queries": [
                "What cloud platforms does Althaf know?",
                "List DevOps tools experience",
                "Programming languages proficiency",
                "Storage technology expertise"
            ]
        },
        {
            "category": "experience",
            "queries": [
                "What are Althaf's work responsibilities?",
                "Recent work experience",
                "Job achievements"
            ]
        },
        {
            "category": "projects",
            "queries": [
                "Most recent project details",
                "Project challenges and solutions",
                "Technical implementations"
            ]
        },
        {
            "category": "certifications",
            "queries": [
                "Cloud certifications",
                "Oracle certifications",
                "Recent certifications"
            ]
        }
    ]
    
    print("Testing Category-Specific Queries:\n")
    for case in test_cases:
        print(f"\n=== {case['category'].upper()} QUERIES ===")
        
        for query in case['queries']:
            print(f"\nQuery: {query}")
            results = collection.query(
                query_texts=[query],
                n_results=2,
                where={"category": case['category']}
            )
            
            print("\nResults:")
            for doc in results['documents'][0]:
                print(f"\n---\n{doc}")
            print("-" * 50)

if __name__ == "__main__":
    test_focused_queries()