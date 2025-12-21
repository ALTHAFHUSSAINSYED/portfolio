#!/usr/bin/env python3
"""
Complete Portfolio Sync to ChromaDB
Syncs ALL portfolio sections including education, achievements, languages, 
professional interests, and resume PDF content
"""

import os
import sys
import json
from pymongo import MongoClient
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from dotenv import load_dotenv
import PyPDF2

load_dotenv()

class LocalEmbeddingFunction:
    """Local embedding function using sentence-transformers"""
    def __init__(self):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def __call__(self, input):
        if isinstance(input, str):
            input = [input]
        return self.model.encode(input).tolist()

def clean(text):
    """Clean text for embedding"""
    return ' '.join(text.split())

def extract_pdf_text(pdf_path):
    """Extract text from PDF resume"""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ''
            for page in pdf_reader.pages:
                text += page.extract_text() + '\n'
            return clean(text)
    except Exception as e:
        print(f"Warning: Could not extract PDF text: {e}")
        return None

def sync_complete_portfolio():
    """Sync all portfolio sections to ChromaDB"""
    
    print("🚀 Complete Portfolio Sync to ChromaDB")
    print("=" * 70)
    
    # Initialize ChromaDB
    client = chromadb.CloudClient(
        tenant=os.getenv('CHROMA_TENANT'),
        database=os.getenv('CHROMA_DATABASE'),
        api_key=os.getenv('CHROMA_API_KEY')
    )
    
    # Wipe and recreate collection
    try:
        client.delete_collection("portfolio")
        print("✓ Wiped old portfolio collection")
    except:
        print("✓ No existing portfolio collection")
    
    try:
        coll = client.get_collection(
            name="portfolio",
            embedding_function=LocalEmbeddingFunction()
        )
    except:
        coll = client.create_collection(
            name="portfolio",
            embedding_function=LocalEmbeddingFunction()
        )
    
    # Load portfolio data (JSON) and Resume Details.txt
    json_path = 'portfolio_data_complete.json' if os.path.exists('portfolio_data_complete.json') else 'backend/portfolio_data_complete.json'
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Parse Resume Details.txt
    resume_txt_path = 'Resume Details.txt' if os.path.exists('Resume Details.txt') else 'backend/Resume Details.txt'
    resume_txt = ''
    if os.path.exists(resume_txt_path):
        with open(resume_txt_path, 'r', encoding='utf-8') as f:
            resume_txt = f.read()

    docs, metas, ids = [], [], []

    # 1. PERSONAL INFO / RESUME (from JSON and Resume Details.txt)
    print("\n📝 Processing Personal Info...")
    info = data.get('personalInfo', {})
    if info:
        text = f"""
        Name: {info.get('name')}
        Title: {info.get('title')}
        Email: {info.get('email')}
        Phone: {info.get('phone')}
        Location: {info.get('location')}
        LinkedIn: {info.get('linkedin')}
        Professional Summary: {info.get('summary')}
        Hero Summary: {info.get('heroSummary')}
        """
        docs.append(clean(text))
        metas.append({
            "type": "resume",
            "section": "personal_info",
            "name": info.get('name', ''),
            "email": info.get('email', '')
        })
        ids.append("personal_info")
        print(f"  ✓ Personal Info (JSON)")

    # Add Resume Details.txt as a separate doc
    if resume_txt:
        docs.append(clean(resume_txt))
        metas.append({
            "type": "resume_txt",
            "section": "resume_txt",
            "source": "Resume Details.txt"
        })
        ids.append("resume_txt")
        print(f"  ✓ Resume Details.txt")

    # 1B. CONTACT INFORMATION (separate entry for chatbot)
    print("\n📞 Processing Contact Information...")
    if info:
        contact_text = f"""
        Contact Information for {info.get('name')}:
        Email: {info.get('email')}
        Phone: {info.get('phone')}
        Location: {info.get('location')}
        LinkedIn Profile: {info.get('linkedin')}
        Professional Title: {info.get('title')}
        You can reach out via email at {info.get('email')} or phone at {info.get('phone')}.
        Located in {info.get('location')}.
        Connect on LinkedIn: {info.get('linkedin')}
        """
        docs.append(clean(contact_text))
        metas.append({
            "type": "contact",
            "section": "contact",
            "email": info.get('email', ''),
            "phone": info.get('phone', '')
        })
        ids.append("contact_info")
        print(f"  ✓ Contact Information")
    
    # 2. SKILLS (all categories)
    print("\n🛠️  Processing Skills...")
    for cat, items in data.get('skills', {}).items():
        skills_list = []
        for item in items:
            if isinstance(item, dict):
                name = item.get('name', '')
                level = item.get('level', '')
                certs = item.get('certifications', '')
                if certs:
                    skills_list.append(f"{name} ({level}, {certs} certifications)")
                else:
                    skills_list.append(f"{name} ({level})")
            else:
                skills_list.append(str(item))
        
        text = f"Skill Category: {cat}. Skills: {', '.join(skills_list)}."
        docs.append(clean(text))
        metas.append({"type": "skill", "category": cat, "section": "skills"})
        ids.append(f"skill_{cat}")
        print(f"  ✓ {cat}: {len(skills_list)} skills")
    
    # 3. EXPERIENCE
    print("\n💼 Processing Experience...")
    for i, exp in enumerate(data.get('experience', [])):
        achievements = exp.get('achievements', [])
        achievements_text = ' | '.join(achievements) if isinstance(achievements, list) else str(achievements)
        
        technologies = exp.get('technologies', [])
        tech_text = ', '.join(technologies) if isinstance(technologies, list) else str(technologies)
        
        text = f"""
        Company: {exp.get('company')}
        Position: {exp.get('position')}
        Duration: {exp.get('duration')}
        Location: {exp.get('location')}
        Project: {exp.get('project')}
        Achievements: {achievements_text}
        Technologies: {tech_text}
        """
        
        docs.append(clean(text))
        metas.append({
            "type": "experience",
            "section": "experience",
            "company": exp.get('company', ''),
            "position": exp.get('position', '')[:100]
        })
        ids.append(f"exp_{i}")
        print(f"  ✓ {exp.get('company')}")
    
    # 4. EDUCATION
    print("\n🎓 Processing Education...")
    for i, edu in enumerate(data.get('education', [])):
        text = f"""
        Degree: {edu.get('degree')}
        Institution: {edu.get('institution')}
        Duration: {edu.get('duration')}
        Location: {edu.get('location')}
        """
        
        docs.append(clean(text))
        metas.append({
            "type": "education",
            "section": "education",
            "degree": edu.get('degree', '')[:100],
            "institution": edu.get('institution', '')[:100]
        })
        ids.append(f"edu_{i}")
        print(f"  ✓ {edu.get('degree')}")
    
    # 5. CERTIFICATIONS
    print("\n🏅 Processing Certifications...")
    for i, cert in enumerate(data.get('certifications', [])):
        category = cert.get('category', '')
        if isinstance(category, list):
            category = ', '.join(str(c) for c in category)
        
        text = f"""
        Certification: {cert.get('name')}
        Issuer: {cert.get('issuer')}
        Year: {cert.get('year')}
        Category: {category}
        """
        
        docs.append(clean(text))
        metas.append({
            "type": "certification",
            "section": "certifications",
            "category": str(category)[:100]
        })
        ids.append(f"cert_{i}")
        print(f"  ✓ {cert.get('name')}")
    
    # 6. ACHIEVEMENTS
    print("\n🏆 Processing Achievements...")
    for i, achievement in enumerate(data.get('achievements', [])):
        text = f"""
        Achievement: {achievement.get('title')}
        Description: {achievement.get('description')}
        """
        
        docs.append(clean(text))
        metas.append({
            "type": "achievement",
            "section": "achievements",
            "title": achievement.get('title', '')[:100]
        })
        ids.append(f"achievement_{i}")
        print(f"  ✓ {achievement.get('title')}")
    
    # 7. PROFESSIONAL INTERESTS
    print("\n🎯 Processing Professional Interests...")
    interests = data.get('professionalInterests', [])
    if interests:
        text = f"Professional Interests and Career Goals: {' | '.join(interests)}"
        docs.append(clean(text))
        metas.append({
            "type": "professional_interests",
            "section": "professional_interests"
        })
        ids.append("professional_interests")
        print(f"  ✓ {len(interests)} interests")
    
    # 8. LANGUAGES
    print("\n🌍 Processing Languages...")
    languages = data.get('languages', [])
    if languages:
        text = f"Languages: {', '.join(languages)}"
        docs.append(clean(text))
        metas.append({
            "type": "languages",
            "section": "languages"
        })
        ids.append("languages")
        print(f"  ✓ {len(languages)} languages")
    
    # 9. RESUME PDF (if exists)
    print("\n📄 Processing Resume PDF...")
    pdf_paths = [
        'frontend/public/AlthafResume.pdf',
        '../frontend/public/AlthafResume.pdf',
        '../../frontend/public/AlthafResume.pdf'
    ]
    
    pdf_text = None
    for pdf_path in pdf_paths:
        if os.path.exists(pdf_path):
            pdf_text = extract_pdf_text(pdf_path)
            if pdf_text:
                docs.append(pdf_text)
                metas.append({
                    "type": "resume_pdf",
                    "section": "resume_pdf",
                    "source": "AlthafResume.pdf"
                })
                ids.append("resume_pdf")
                print(f"  ✓ PDF Resume ({len(pdf_text)} chars)")
                break
    
    if not pdf_text:
        print("  ⚠️  Resume PDF not found or could not be extracted")
    
    # 10. ADD ALL TO CHROMADB (only if new data is present)
    print("\n💾 Adding to ChromaDB (portfolio collection)...")
    # Get current IDs in ChromaDB
    existing_ids = set()
    try:
        existing = coll.get(include=["ids"])
        existing_ids = set(existing["ids"])
    except Exception:
        pass

    # Only add new docs (by id)
    new_docs, new_metas, new_ids = [], [], []
    for d, m, i in zip(docs, metas, ids):
        if i not in existing_ids:
            new_docs.append(d)
            new_metas.append(m)
            new_ids.append(i)

    if new_docs:
        coll.add(documents=new_docs, metadatas=new_metas, ids=new_ids)
        print(f"✅ Added {len(new_docs)} new items to ChromaDB portfolio collection")
        # Send email notification (import notification_service dynamically)
        try:
            import importlib.util
            notif_spec = importlib.util.find_spec("backend.notification_service")
            if notif_spec:
                notification_service = importlib.util.module_from_spec(notif_spec)
                notif_spec.loader.exec_module(notification_service)
                to_email = os.getenv("TO_EMAIL") or getattr(notification_service, "to_email", None)
                if hasattr(notification_service, "send_blog_notification"):
                    notification_service.send_blog_notification(True, {"section": "portfolio", "count": len(new_docs)}, None)
                print(f"📧 Notification sent to {to_email}")
        except Exception as e:
            print(f"⚠️  Could not send notification: {e}")
        # Show summary
        print("\n📊 SUMMARY:")
        sections = {}
        for meta in new_metas:
            section = meta.get('section', 'unknown')
            sections[section] = sections.get(section, 0) + 1
        for section, count in sorted(sections.items()):
            print(f"  {section}: {count} items")
    else:
        print("❌ No new data to add")

    print("\n" + "=" * 70)
    print("✅ COMPLETE PORTFOLIO SYNC FINISHED")

if __name__ == "__main__":
    sync_complete_portfolio()
