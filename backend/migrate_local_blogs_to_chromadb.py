import os
import json
import chromadb
from dotenv import load_dotenv
load_dotenv()

# Path to local blogs directory
BLOGS_DIR = os.path.join(os.path.dirname(__file__), 'generated_blogs')

# Connect to ChromaDB and get/create Blogs_data collection
chroma_client = chromadb.CloudClient(
    api_key=os.getenv('CHROMA_API_KEY'),
    tenant=os.getenv('CHROMA_TENANT_ID'),
    database=os.getenv('CHROMA_DATABASE')
)
blogs_collection = chroma_client.get_collection(
    name='Blogs_data'
)

def migrate_local_blogs():
    files = [f for f in os.listdir(BLOGS_DIR) if f.endswith('.json')]
    print(f"Found {len(files)} blog files to migrate.")
    for filename in files:
        filepath = os.path.join(BLOGS_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            blog = json.load(f)
        # Prepare document and metadata
        document = blog.get('content', '')
        metadata = {
            'title': blog.get('title'),
            'topic': blog.get('topic'),
            'created_at': blog.get('created_at'),
            'tags': ', '.join(blog.get('tags', [])),
            'summary': blog.get('summary'),
            'category': blog.get('category'),
            'sources': ', '.join(blog.get('sources', []))
        }
        blog_id = f"blog_{filename.replace('.json', '')}"
        blogs_collection.add(documents=[document], metadatas=[metadata], ids=[blog_id])
        print(f"Migrated: {metadata['title']} -> {blog_id}")
    print("Migration of local blogs to ChromaDB complete.")

if __name__ == "__main__":
    migrate_local_blogs()
