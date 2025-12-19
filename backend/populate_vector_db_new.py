import chromadb
import os
import json
import re
from dotenv import load_dotenv
# Explicitly import standard SentenceTransformer
from sentence_transformers import SentenceTransformer

load_dotenv()

# Initialize Client
client = chromadb.CloudClient(
    api_key=os.getenv('CHROMA_API_KEY'),
    tenant=os.getenv('CHROMA_TENANT'),
    database=os.getenv('CHROMA_DATABASE')
)

# Initialize Embedding Model (Local)
print("⏳ Loading AI Model (this takes 400MB RAM)...")
model = SentenceTransformer('all-MiniLM-L6-v2')

class LocalEmbeddingFunction:
    def __call__(self, input):
        return model.encode(input).tolist()

def clean(text): 
    return re.sub(r'\s+', ' ', str(text)).strip()

def main():
    print("🚀 Syncing Portfolio (Resume/Skills/Experience/Certifications)...")
    
    # 1. WIPE OLD DATA / GET EXISTING COLLECTION
    try: 
        client.delete_collection("portfolio")
        print("✓ Wiped old portfolio data")
    except: 
        print("✓ No existing portfolio collection")
    
    # 2. GET OR CREATE COLLECTION (With local embedding function)
    try:
        coll = client.get_collection(
            name="portfolio",
            embedding_function=LocalEmbeddingFunction()
        )
        print("✓ Using existing portfolio collection")
    except:
        coll = client.create_collection(
            name="portfolio",
            embedding_function=LocalEmbeddingFunction()
        )
        print("✓ Created new portfolio collection")
    
    # 3. LOAD JSON
    path = 'portfolio_data.json' if os.path.exists('portfolio_data.json') else 'backend/portfolio_data.json'
    with open(path, 'r') as f: 
        data = json.load(f)

    docs, metas, ids = [], [], []

    # 4. PROCESS PERSONAL INFO
    info = data.get('personalInfo', {})
    if info:
        text = f"Candidate: {info.get('name')}. Role: {info.get('title')}. Summary: {info.get('summary')}. Contact: {info.get('email')}, {info.get('location')}."
        docs.append(clean(text))
        metas.append({"type": "resume", "name": info.get('name'), "email": info.get('email')})
        ids.append("info")

    # 5. PROCESS SKILLS
    for cat, items in data.get('skills', {}).items():
        s_list = [i['name'] if isinstance(i, dict) else str(i) for i in items]
        docs.append(f"Category: {cat}. Skills: {', '.join(s_list)}.")
        metas.append({"type": "skill", "category": cat})
        ids.append(f"skill_{cat}")

    # 6. PROCESS EXPERIENCE
    for i, exp in enumerate(data.get('experience', [])):
        responsibilities = exp.get('responsibilities', []) if isinstance(exp.get('responsibilities'), list) else []
        achievements = exp.get('achievements', []) if isinstance(exp.get('achievements'), list) else []
        
        text = f"Role: {exp.get('position')} at {exp.get('company')}. Duration: {exp.get('duration')}. "
        if responsibilities:
            text += f"Responsibilities: {' '.join(responsibilities)}. "
        if achievements:
            text += f"Achievements: {' '.join(achievements)}."
        
        docs.append(clean(text))
        metas.append({"type": "experience", "company": exp.get('company')})
        ids.append(f"exp_{i}")

    # 7. PROCESS CERTIFICATIONS
    for i, cert in enumerate(data.get('certifications', [])):
        category = cert.get('category', '')
        # Convert list to string if needed
        if isinstance(category, list):
            category = ', '.join(str(c) for c in category)
        
        text = f"Certification: {cert.get('name')} from {cert.get('issuer')}. Year: {cert.get('year')}. Category: {category}."
        docs.append(clean(text))
        metas.append({"type": "certification", "category": str(category)})
        ids.append(f"cert_{i}")

    # 8. ADD TO CHROMADB
    if docs:
        coll.add(documents=docs, metadatas=metas, ids=ids)
        print(f"✅ Portfolio Synced to ChromaDB ({len(docs)} items).")
    else:
        print("⚠️ No portfolio data found to sync")

if __name__ == "__main__": 
    main()
