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

def get_project_details(project):
    """Extract detailed information from a project"""
    details = []
    details.append(f"Project: {project.get('title', '')}")
    details.append(f"Description: {project.get('description', '')}")
    details.append(f"Technologies: {', '.join(project.get('technologies', []))}")
    details.append(f"Category: {project.get('category', '')}")
    details.append(f"Duration: {project.get('duration', '')}")
    
    if 'challenges' in project:
        details.append("Challenges:")
        for challenge in project['challenges']:
            details.append(f"- {challenge}")
    
    if 'solutions' in project:
        details.append("Solutions:")
        for solution in project['solutions']:
            details.append(f"- {solution}")
    
    if 'outcomes' in project:
        details.append("Outcomes:")
        for outcome in project['outcomes']:
            details.append(f"- {outcome}")
    
    return "\n".join(details)

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
        Name: {info.get('name')}
        Title: {info.get('title')}
        Summary: {info.get('summary')}
        Location: {info.get('location')}
        Email: {info.get('email')}
        LinkedIn: {info.get('linkedin')}
        """))
        metadatas.append({"category": "personal_info", "section": "about"})
        ids.append(f"doc_{doc_id}")

    # Skills
    if 'skills' in data:
        for category, skills_list in data['skills'].items():
            doc_id += 1
            # Handle the new skills format where each skill is an object
            skill_texts = []
            for skill in skills_list:
                if isinstance(skill, dict):
                    skill_text = skill.get('name', '')
                    level = skill.get('level', '')
                    certs = skill.get('certifications', '')
                    if level or certs:
                        skill_text += f" (Level: {level}"
                        if certs:
                            skill_text += f", Certifications: {certs}"
                        skill_text += ")"
                    skill_texts.append(skill_text)
                else:
                    skill_texts.append(skill)
            
            documents.append(clean_text(f"Category: {category}\nSkills: {', '.join(skill_texts)}"))
            metadatas.append({"category": "skills", "section": category.lower()})
            ids.append(f"doc_{doc_id}")

    # Experience
    if 'experience' in data:
        for exp in data['experience']:
            doc_id += 1
            exp_text = f"""
            Position: {exp.get('title')}
            Company: {exp.get('company')}
            Duration: {exp.get('duration')}
            Description: {exp.get('description')}
            Responsibilities: {' '.join(exp.get('responsibilities', []))}
            """
            documents.append(clean_text(exp_text))
            metadatas.append({"category": "experience", "section": "work_history"})
            ids.append(f"doc_{doc_id}")

    # Projects
    if 'projects' in data:
        for project in data['projects']:
            doc_id += 1
            project_text = get_project_details(project)
            documents.append(clean_text(project_text))
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
            cert_text = f"""
            Certification: {cert.get('name')}
            Issuer: {cert.get('issuer')}
            Date: {cert.get('date')}
            Description: {cert.get('description')}
            """
            documents.append(clean_text(cert_text))
            metadatas.append({"category": "certifications", "section": "credentials"})
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
            "What are Althaf's technical skills?",
            "What projects has Althaf worked on?",
            "Tell me about Althaf's work experience",
            "What certifications does Althaf have?"
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