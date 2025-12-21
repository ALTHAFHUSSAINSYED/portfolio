import chromadb
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

# MongoDB Atlas connection details from .env
import os
from dotenv import load_dotenv
load_dotenv()
MONGO_URI = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME", "portfolioDB")
COLLECTION_NAME = "projects"

# ChromaDB cloud credentials from .env
api_key = os.getenv("api_key")
tenant = os.getenv("tenant")
database = os.getenv("database")

# Connect to ChromaDB Cloud and get/create Projects_data collection

# Connect to ChromaDB Cloud
chroma_client = chromadb.CloudClient(
    api_key=api_key,
    tenant=tenant,
    database=database
)
projects_collection = chroma_client.get_collection(name='Projects_data')

async def migrate_projects():
    mongo_client = AsyncIOMotorClient(MONGO_URI)
    db = mongo_client[DB_NAME]
    cursor = db[COLLECTION_NAME].find({})
    count = 0
    async for project in cursor:
        document = project.get('details', '')
        metadata = {
            'name': project.get('name'),
            'summary': project.get('summary'),
            'technologies': ', '.join(project.get('technologies', [])),
            'image_url': project.get('image_url'),
            'key_outcomes': project.get('key_outcomes'),
            'timestamp': str(project.get('timestamp'))
        }
        project_id = f"project_{str(project.get('_id'))}"
        projects_collection.add(documents=[document], metadatas=[metadata], ids=[project_id])
        print(f"Migrated: {metadata['name']} -> {project_id}")
        count += 1
    print(f"Migration of {count} projects from MongoDB to ChromaDB complete.")

if __name__ == "__main__":
    asyncio.run(migrate_projects())
