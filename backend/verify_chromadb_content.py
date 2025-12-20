#!/usr/bin/env python3
"""
Verify ChromaDB Projects_data contains FULL implementation details
Run this script to check what data is actually stored in ChromaDB
"""
import os
from dotenv import load_dotenv
import chromadb

load_dotenv()

def verify_chromadb():
    print("=" * 80)
    print("CHROMADB PROJECTS_DATA VERIFICATION")
    print("=" * 80)
    
    # Connect
    client = chromadb.CloudClient(
        api_key=os.getenv('api_key'),
        tenant=os.getenv('tenant'),
        database=os.getenv('database')
    )
    
    # Get collection
    collection = client.get_collection('Projects_data')
    
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
        has_kubernetes = 'Kubernetes' in document or 'kubernetes' in document.lower()
        
        print(f"   Content Check:")
        print(f"     - Has Architecture details: {'✅ YES' if has_arch else '❌ NO'}")
        print(f"     - Has Implementation details: {'✅ YES' if has_impl else '❌ NO'}")
        print(f"     - Has Jenkins/Pipeline code: {'✅ YES' if has_jenkins else '❌ NO'}")
        print(f"     - Has Terraform mentions: {'✅ YES' if has_terraform else '❌ NO'}")
        print(f"     - Has Kubernetes details: {'✅ YES' if has_kubernetes else '❌ NO'}")
        
        # Sample content (first 300 chars)
        print(f"\n   Document Preview:")
        print(f"   {document[:300]}...")
        
        # Verdict
        if len(document) > 1000 and (has_arch or has_impl):
            print(f"   ✅ VERDICT: Contains FULL implementation details")
        else:
            print(f"   ⚠️  VERDICT: May contain only summary - needs update!")
        
        print("-" * 80)
    
    print("\n" + "=" * 80)
    print("SUMMARY:")
    
    # Overall analysis
    avg_length = sum(len(doc) for doc in results['documents']) / len(results['documents'])
    print(f"Average document length: {avg_length:,.0f} characters")
    
    if avg_length > 3000:
        print("✅ ChromaDB appears to have FULL implementation details!")
    elif avg_length > 1000:
        print("⚠️  ChromaDB has moderate content - verify completeness")
    else:
        print("❌ ChromaDB likely has only summaries - needs re-sync from MongoDB")
    
    print("=" * 80)

if __name__ == "__main__":
    try:
        verify_chromadb()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
