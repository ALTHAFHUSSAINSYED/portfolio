import chromadb
import os
import json
import re

# Initialize ChromaDB cloud client
client = chromadb.CloudClient(
    api_key='ck-EWpGxabEbpBzHDHjj9YrSFoyRyiAtgwooUbtmJXxziXH',
    tenant='7c2da124-ba75-4ae6-85b5-ff22589f0d08',
    database='Development'
)

def clean_text(text):
    """Clean and format text for better embedding"""
    # Remove extra whitespace and newlines
    text = re.sub(r'\s+', ' ', text).strip()
    # Remove special characters but keep punctuation
    text = re.sub(r'[^\w\s.,!?-]', '', text)
    return text

def load_portfolio_data():
    """Load portfolio data from the formatted JSON file"""
    try:
        with open('portfolio_data.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading portfolio data: {e}")
        return None

def format_skill_category(category, skills):
    """Format a category of skills"""
    lines = []
    lines.append(f"Skill Category: {category}")
    for skill in skills:
        if isinstance(skill, dict):
            skill_info = []
            name = skill.get('name', '')
            level = skill.get('level', '')
            certs = skill.get('certifications', '')
            
            skill_info.append(f"Technology: {name}")
            if level:
                skill_info.append(f"Proficiency: {level}")
            if certs:
                skill_info.append(f"Certifications: {certs}")
            
            lines.append(" | ".join(skill_info))
    return "\n".join(lines)

def format_experience(exp):
    """Format work experience details"""
    lines = []
    lines.append(f"Position: {exp.get('title', '')}")
    lines.append(f"Company: {exp.get('company', '')}")
    lines.append(f"Duration: {exp.get('duration', '')}")
    
    if 'description' in exp:
        lines.append(f"Overview: {exp['description']}")
    
    if 'responsibilities' in exp:
        lines.append("\nKey Responsibilities:")
        for resp in exp['responsibilities']:
            lines.append(f"- {resp}")
    
    return "\n".join(lines)

def format_project(project):
    """Format project details"""
    lines = []
    lines.append(f"Project Title: {project.get('title', '')}")
    
    if 'description' in project:
        lines.append(f"Project Overview: {project['description']}")
    
    if 'duration' in project:
        lines.append(f"Timeline: {project['duration']}")
    
    if project.get('technologies'):
        lines.append("Technologies and Tools:")
        for tech in project['technologies']:
            lines.append(f"- {tech}")
    
    if project.get('challenges'):
        lines.append("\nKey Challenges Addressed:")
        for challenge in project['challenges']:
            lines.append(f"- {challenge}")
    
    if project.get('solutions'):
        lines.append("\nSolutions and Implementations:")
        for solution in project['solutions']:
            lines.append(f"- {solution}")
    
    if project.get('outcomes'):
        lines.append("\nProject Outcomes and Impact:")
        for outcome in project['outcomes']:
            lines.append(f"- {outcome}")
            
    return "\n".join(lines)

def format_certification(cert):
    """Format certification details"""
    lines = []
    lines.append(f"Certification: {cert.get('name', '')}")
    lines.append(f"Issuing Organization: {cert.get('issuer', '')}")
    
    if cert.get('date'):
        lines.append(f"Date Achieved: {cert['date']}")
    
    if cert.get('description'):
        lines.append(f"\nDetails: {cert['description']}")
        
    if cert.get('credential'):
        lines.append(f"Credential ID: {cert['credential']}")
        
    return "\n".join(lines)

def process_portfolio_data(data):
    """Process and structure all portfolio data for embedding"""
    documents = []
    metadatas = []
    ids = []
    doc_id = 0

    # Personal Information
    if 'personalInfo' in data:
        info = data['personalInfo']
        doc_id += 1
        documents.append(clean_text(f"""
        Professional Profile:
        Name: {info.get('name')}
        Role: {info.get('title')}
        
        Professional Summary:
        {info.get('summary')}
        
        Contact Information:
        Location: {info.get('location')}
        Email: {info.get('email')}
        LinkedIn: {info.get('linkedin')}
        """))
        metadatas.append({"category": "personal_info", "section": "about"})
        ids.append(f"doc_{doc_id}")

    # Skills by Category
    if 'skills' in data:
        for category, skills in data['skills'].items():
            doc_id += 1
            documents.append(clean_text(format_skill_category(category, skills)))
            metadatas.append({"category": "skills", "section": category.lower()})
            ids.append(f"doc_{doc_id}")

    # Experience
    if 'experience' in data:
        for exp in data['experience']:
            doc_id += 1
            documents.append(clean_text(format_experience(exp)))
            metadatas.append({
                "category": "experience", 
                "section": "work_history",
                "company": exp.get('company', '')
            })
            ids.append(f"doc_{doc_id}")

    # Projects
    if 'projects' in data:
        for project in data['projects']:
            doc_id += 1
            documents.append(clean_text(format_project(project)))
            metadatas.append({
                "category": "projects",
                "section": "portfolio_project",
                "project_title": project.get('title', '')
            })
            ids.append(f"doc_{doc_id}")

    # Certifications
    if 'certifications' in data:
        for cert in data['certifications']:
            doc_id += 1
            documents.append(clean_text(format_certification(cert)))
            metadatas.append({
                "category": "certifications",
                "section": "credentials",
                "issuer": cert.get('issuer', '')
            })
            ids.append(f"doc_{doc_id}")

    return documents, metadatas, ids

def main():
    try:
        # Get or create collection
        collection = client.get_or_create_collection(
            name="portfolio",
            metadata={"description": "Portfolio content embeddings"}
        )
        print("Connected to ChromaDB cloud collection!")

        # Load portfolio data
        portfolio_data = load_portfolio_data()
        if not portfolio_data:
            print("Failed to load portfolio data")
            return

        # Process portfolio data
        documents, metadatas, ids = process_portfolio_data(portfolio_data)
        
        # Add documents to collection
        print(f"\nAdding {len(documents)} documents to collection...")
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print("Successfully added documents!")
        
        # Test queries
        test_queries = [
            "What cloud platforms is Althaf experienced with?",
            "What DevOps tools does Althaf use?",
            "Describe Althaf's storage expertise",
            "List Althaf's programming languages",
            "What certifications does Althaf have?",
            "Tell me about Althaf's most recent project",
            "What are Althaf's key achievements?"
        ]
        
        print("\nTesting queries:")
        for query in test_queries:
            print(f"\nQuery: {query}")
            results = collection.query(
                query_texts=[query],
                n_results=2
            )
            
            for doc in results['documents'][0]:
                print(f"\n---\n{doc}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()