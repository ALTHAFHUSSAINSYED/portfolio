import chromadb
from chromadb.config import Settings
import json
import re

def clean_text(text):
    """Clean and format text for better embedding"""
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'[^\w\s.,!?-]', '', text)
    return text

# Initialize ChromaDB client
client = chromadb.CloudClient(
    api_key='ck-EWpGxabEbpBzHDHjj9YrSFoyRyiAtgwooUbtmJXxziXH',
    tenant='7c2da124-ba75-4ae6-85b5-ff22589f0d08',
    database='Development'
)

# Get or create collection
collection = client.get_or_create_collection("portfolio_data")

# Add blog data
blogs = [
    {
        "title": "Understanding Docker Containers",
        "content": """
        Docker containers are lightweight, standalone executable packages that include everything needed to run an application.
        Key benefits include:
        - Consistency across environments
        - Isolation from other applications
        - Easy scaling and deployment
        - Efficient resource utilization
        This technology is fundamental for modern DevOps practices and microservices architecture.
        """,
        "category": "DevOps"
    },
    {
        "title": "Cloud Computing Fundamentals",
        "content": """
        Cloud computing provides on-demand access to computing resources over the internet.
        Core concepts include:
        - Infrastructure as a Service (IaaS)
        - Platform as a Service (PaaS)
        - Software as a Service (SaaS)
        The major providers are AWS, Azure, and Google Cloud Platform.
        """,
        "category": "Cloud"
    },
    {
        "title": "DevOps Best Practices",
        "content": """
        DevOps combines development and operations to improve software delivery.
        Essential practices include:
        - Continuous Integration/Continuous Deployment
        - Infrastructure as Code
        - Automated Testing
        - Monitoring and Logging
        These practices help organizations deliver better software faster.
        """,
        "category": "DevOps"
    }
]

# Format and add blog documents
for blog in blogs:
    document = f"Title: {blog['title']}\n\n{clean_text(blog['content'])}"
    metadata = {
        "category": "blogs",
        "subcategory": blog["category"],
        "type": "article"
    }
    collection.add(
        documents=[document],
        metadatas=[metadata],
        ids=[f"blog_{blog['title'].lower().replace(' ', '_')}"]
    )

print("\nTesting blog queries:\n")

test_queries = [
    "Explain to me about the blog on Docker containers",
    "What is the main topic of the blog about cloud computing?",
    "Give me a summary of the blog about DevOps",
]

for query in test_queries:
    print(f"Query: {query}")
    results = collection.query(
        query_texts=[query],
        n_results=1,
        where={"category": "blogs"}
    )
    print("---")
    for doc in results['documents'][0]:
        print(doc)
        print("---")
    print()