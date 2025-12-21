#!/usr/bin/env python3
"""
Verify ChromaDB Projects_data contains FULL implementation details
Run this script to check what data is actually stored in ChromaDB
"""

import os
import chromadb
from dotenv import load_dotenv

# Load .env file
load_dotenv()

def verify_chromadb():
    print("=" * 80)
    print("CHROMADB PROJECTS_DATA VERIFICATION")
    print("=" * 80)
    
    # Corrected Credential Loading
    api_key = os.getenv('CHROMA_API_KEY')
    tenant_id = os.getenv('CHROMA_TENANT_ID')
    db_name = os.getenv('CHROMA_DB_NAME', 'Development')

    if not api_key:
        print("[ERROR] CHROMA_API_KEY not found in .env file.")
        return

    # Connect
    try:
        client = chromadb.CloudClient(
            api_key=api_key,
            tenant=tenant_id,
            database=db_name
        )
    except Exception as e:
        print(f"[ERROR] Connection Failed: {e}")
        return
    
    # Get collection
    try:
        collection = client.get_collection('Projects_data')
    except:
        print("[ERROR] Collection 'Projects_data' not found.")
        return
    
    # Get all data
    results = collection.get(include=['metadatas', 'documents'])
    
    print(f"\nTotal Projects: {len(results['ids'])}")
    print("=" * 80)
    
    for i, proj_id in enumerate(results['ids']):
        metadata = results['metadatas'][i]
        document = results['documents'][i]
        
        print(f"\n{i+1}. {metadata.get('name', 'Unknown Project')}")
        print(f"   ID: {proj_id}")
        print(f"   Document Length: {len(document):,} characters")
        
        # Check for key implementation details
        has_jenkins = 'pipeline {' in document or 'Jenkinsfile' in document
        has_arch = 'Architecture' in document or 'architecture' in document.lower()
        has_impl = 'Implementation' in document or 'implementation' in document.lower()
        has_terraform = 'Terraform' in document or 'terraform' in document.lower()
        
        print(f"   Content Check:")
        print(f"     - Has Architecture details: {'YES' if has_arch else 'NO'}")
        print(f"     - Has Implementation details: {'YES' if has_impl else 'NO'}")
        print(f"     - Has Jenkins Code: {'YES' if has_jenkins else 'NO'}")
        print(f"     - Has Terraform mentions: {'YES' if has_terraform else 'NO'}")
        
        if len(document) > 1000:
            print(f"   [VERDICT] Contains detailed content.")
        else:
            print(f"   [VERDICT] Summary only.")
        print("-" * 80)

if __name__ == "__main__":
    verify_chromadb()
