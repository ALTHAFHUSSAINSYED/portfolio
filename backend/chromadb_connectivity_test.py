
import os
import chromadb
from dotenv import load_dotenv

# Explicitly load .env file

# Load .env from backend directory
from pathlib import Path
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

api_key = os.getenv('api_key')
database = os.getenv('database')
tenant = os.getenv('tenant')


print(f"api_key: {api_key}")
print(f"tenant: {tenant}")
print(f"database: {database}")

try:
    chroma_client = chromadb.CloudClient(
        api_key=api_key,
        tenant=tenant,
        database=database
    )
    print("ChromaDB connection successful.")
    collections = chroma_client.list_collections()
    print("Collections:", collections)
except Exception as e:
    print(f"ChromaDB connection failed: {e}")
