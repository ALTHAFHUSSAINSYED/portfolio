#!/usr/bin/env python3
"""
Master Project Sync Script
Syncs projects from portfolio_data_complete.json to both MongoDB and ChromaDB
"""

import os
import sys
import json
from datetime import datetime
from pymongo import MongoClient
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from dotenv import load_dotenv
import uuid

load_dotenv()

def get_html_list(items):
    """Convert list to HTML unordered list"""
    if not items:
        return ""
    html = "<ul>\n"
    for item in items:
        html += f"  <li>{item}</li>\n"
    html += "</ul>"
    return html

def sync_to_mongodb(projects):
    """Sync projects to MongoDB"""
    try:
        mongo_url = os.getenv('MONGO_URL')
        client = MongoClient(mongo_url)
        db = client['portfolioDB']
        collection = db['projects']
        
        # Clear existing projects
        deleted = collection.delete_many({})
        print(f"✓ Wiped old MongoDB projects ({deleted.deleted_count} documents)")
        
        # Insert new projects
        for project in projects:
            # Convert project data to MongoDB format
            mongo_doc = {
                'id': project.get('id', str(uuid.uuid4())),
                'name': project['title'],  # MongoDB uses 'name' not 'title'
                'summary': project['description'],
                'details': f"""
<h2>Overview</h2>
<p>{project['description']}</p>

<h3>Role & Team</h3>
<p><strong>Role:</strong> {project.get('role', 'DevOps Engineer')}</p>
<p><strong>Duration:</strong> {project.get('duration', 'N/A')}</p>
<p><strong>Team Size:</strong> {project.get('teamSize', 'N/A')}</p>

<h3>Challenges</h3>
{get_html_list(project.get('challenges', []))}

<h3>Solutions Implemented</h3>
{get_html_list(project.get('solutions', []))}

<h3>Key Achievements</h3>
{get_html_list(project.get('achievements', []))}

<h3>Technologies Used</h3>
{get_html_list(project.get('technologies', []))}
""",
                'image_url': project.get('image_url', ''),
                'technologies': project.get('technologies', []),
                'category': project.get('category', 'DevOps'),
                'timestamp': datetime.now()
            }
            
            collection.insert_one(mongo_doc)
        
        count = collection.count_documents({})
        print(f"✅ MongoDB: Refreshed {count} projects")
        return True
        
    except Exception as e:
        print(f"❌ MongoDB sync failed: {e}")
        return False

def sync_to_chromadb(projects):
    """Sync projects to ChromaDB"""
    try:
        # Initialize ChromaDB client
        chroma_client = chromadb.CloudClient(
            tenant=os.getenv('CHROMA_TENANT'),
            database=os.getenv('CHROMA_DATABASE'),
            api_key=os.getenv('CHROMA_API_KEY')
        )
        
        # Create embedding function
        embedding_fn = SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Get or create collection
        try:
            chroma_client.delete_collection(name="Projects_data")
            print("✓ Wiped old ChromaDB projects")
        except:
            pass
        
        collection = chroma_client.create_collection(
            name="Projects_data",
            embedding_function=embedding_fn
        )
        
        # Prepare data for ChromaDB
        documents = []
        metadatas = []
        ids = []
        
        for project in projects:
            # Create rich text representation with FULL implementation details for embedding
            challenges_text = '\n'.join(f"- {c}" for c in project.get('challenges', []))
            solutions_text = '\n'.join(f"- {s}" for s in project.get('solutions', []))
            achievements_text = '\n'.join(f"- {a}" for a in project.get('achievements', []))
            
            doc_text = f"""
Project Title: {project['title']}

Description: {project['description']}

Category: {project.get('category', 'DevOps')}

Role: {project.get('role', 'DevOps Engineer')}
Duration: {project.get('duration', 'N/A')}
Team Size: {project.get('teamSize', 'N/A')}

Technologies Used:
{', '.join(project.get('technologies', []))}

Challenges:
{challenges_text}

Solutions Implemented:
{solutions_text}

Key Achievements:
{achievements_text}

Full Implementation Details:
This project involved {project['description']} The team of {project.get('teamSize', 'N/A')} worked for {project.get('duration', 'N/A')} to deliver a comprehensive solution using {', '.join(project.get('technologies', [])[:5])}. The implementation addressed critical challenges including {' and '.join(project.get('challenges', [])[:2])}. The solutions delivered measurable results with achievements such as {' and '.join(project.get('achievements', [])[:2])}.
"""
            
            metadata = {
                'title': project['title'],
                'description': project['description'][:500],  # Truncate for metadata
                'category': project.get('category', 'DevOps'),
                'technologies': json.dumps(project.get('technologies', [])),
                'duration': project.get('duration', 'N/A'),
                'role': project.get('role', 'DevOps Engineer')
            }
            
            project_id = project.get('id', str(uuid.uuid4()))
            
            documents.append(doc_text)
            metadatas.append(metadata)
            ids.append(project_id)
        
        # Add to collection
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"✅ ChromaDB: Refreshed {len(projects)} projects")
        return True
        
    except Exception as e:
        print(f"❌ ChromaDB sync failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🚀 Master Project Sync (MongoDB + ChromaDB)")
    print("=" * 60)
    
    # Load projects from portfolio_data_complete.json
    json_file = os.path.join(os.path.dirname(__file__), 'portfolio_data_complete.json')
    
    if not os.path.exists(json_file):
        print(f"❌ Error: {json_file} not found")
        sys.exit(1)
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            projects = data.get('projects', [])
    except Exception as e:
        print(f"❌ Error loading JSON: {e}")
        sys.exit(1)
    
    if not projects:
        print("❌ No projects found in JSON")
        sys.exit(1)
    
    print(f"📄 Loaded {len(projects)} projects from JSON")
    
    # Sync to MongoDB
    mongo_success = sync_to_mongodb(projects)
    
    # Sync to ChromaDB
    chroma_success = sync_to_chromadb(projects)
    
    print("\n" + "=" * 60)
    if mongo_success and chroma_success:
        print("✅ ALL SYNCS COMPLETED SUCCESSFULLY")
    else:
        print("⚠️  PARTIAL SUCCESS - Some syncs failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
