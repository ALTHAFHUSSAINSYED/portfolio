import os
import json
from dotenv import load_dotenv
import chromadb
import google.generativeai as genai
import numpy as np

# Load environment variables
load_dotenv()

# Initialize Gemini
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Initialize ChromaDB cloud client
client = chromadb.CloudClient(
    api_key=os.getenv('CHROMA_API_KEY'),
    tenant='7c2da124-ba75-4ae6-85b5-ff22589f0d08',
    database='Development'
)

# Custom embedding function using Gemini
class GeminiEmbeddingFunction:
    def __call__(self, texts):
        # Initialize model
        model = genai.GenerativeModel('gemini-pro')
        
        # Generate embeddings for each text
        embeddings = []
        for text in texts:
            # Use Gemini to generate a numerical representation
            # We'll use a prompt that asks Gemini to understand the text deeply
            prompt = f"Analyze this text and represent its key concepts: {text}"
            response = model.generate_content(prompt)
            
            # Convert the response to a fixed-size embedding
            # We'll hash the response to create a consistent numerical representation
            embedding = self._text_to_vector(response.text)
            embeddings.append(embedding)
        
        return embeddings
    
    def _text_to_vector(self, text, vector_size=768):
        """Convert text to a fixed-size vector using a deterministic method."""
        # Create a fixed-size array initialized with zeros
        vector = np.zeros(vector_size)
        
        # Use character positions and values to fill the vector
        for i, char in enumerate(text):
            # Update vector elements based on character position and value
            pos = i % vector_size
            vector[pos] = (vector[pos] + ord(char)) % 1.0  # Normalize to [0,1]
        
        # Normalize the vector
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        
        return vector.tolist()

# Initialize embedding function
embedding_function = GeminiEmbeddingFunction()

def create_or_get_collection():
    """Create or get the ChromaDB collection for portfolio data."""
    try:
        collection = client.get_collection(
            name="portfolio",
            embedding_function=embedding_function
        )
        print("Retrieved existing collection")
    except:
        collection = client.create_collection(
            name="portfolio",
            embedding_function=embedding_function
        )
        print("Created new collection")
    return collection

def load_portfolio_data():
    """Load portfolio data from JSON file."""
    try:
        with open('../frontend/src/data/mock.js', 'r') as file:
            # Skip the export line and parse the JSON part
            content = file.read()
            json_str = content.split('export const portfolioData = ')[1].strip().rstrip(';')
            return json.loads(json_str)
    except Exception as e:
        print(f"Error loading portfolio data: {e}")
        return None

def create_text_chunks(data):
    """Process portfolio data into text chunks for embedding."""
    chunks = []
    ids = []
    metadata = []

    # Personal Info
    if 'personalInfo' in data:
        info = data['personalInfo']
        chunk = f"Personal Information:\n{info.get('name')} is a {info.get('title')}.\n{info.get('summary')}"
        chunks.append(chunk)
        ids.append("personal_info")
        metadata.append({"category": "personal_info"})

    # Skills
    if 'skills' in data:
        for i, skill_category in enumerate(data['skills']):
            chunk = f"Skills in {skill_category['category']}:\n"
            chunk += "\n".join([f"- {skill}" for skill in skill_category['skills']])
            chunks.append(chunk)
            ids.append(f"skills_{i}")
            metadata.append({"category": "skills", "subcategory": skill_category['category']})

    # Experience
    if 'experience' in data:
        for i, exp in enumerate(data['experience']):
            chunk = f"Work Experience at {exp['company']} as {exp['role']}\n"
            chunk += f"Duration: {exp['duration']}\n"
            chunk += "Responsibilities and achievements:\n"
            chunk += "\n".join([f"- {point}" for point in exp['points']])
            chunks.append(chunk)
            ids.append(f"experience_{i}")
            metadata.append({"category": "experience", "company": exp['company']})

    # Projects
    if 'projects' in data:
        for i, project in enumerate(data['projects']):
            chunk = f"Project: {project['title']}\n"
            chunk += f"Description: {project['description']}\n"
            if 'techStack' in project:
                chunk += f"Technologies used: {', '.join(project['techStack'])}\n"
            if 'points' in project:
                chunk += "Key features and achievements:\n"
                chunk += "\n".join([f"- {point}" for point in project['points']])
            chunks.append(chunk)
            ids.append(f"project_{i}")
            metadata.append({"category": "project", "title": project['title']})

    # Blogs (if available)
    if 'blogs' in data:
        for i, blog in enumerate(data['blogs']):
            chunk = f"Blog: {blog['title']}\n"
            chunk += f"Description: {blog['description']}\n"
            if 'content' in blog:
                chunk += f"Content: {blog['content'][:500]}..." # Truncate long content
            chunks.append(chunk)
            ids.append(f"blog_{i}")
            metadata.append({"category": "blog", "title": blog['title']})

    return chunks, ids, metadata

def main():
    # Get or create collection
    collection = create_or_get_collection()
    
    # Load portfolio data
    print("Loading portfolio data...")
    data = load_portfolio_data()
    if not data:
        print("Failed to load portfolio data")
        return
    
    # Create text chunks
    print("Processing portfolio data into chunks...")
    chunks, ids, metadata = create_text_chunks(data)
    
    # Add documents to collection
    print(f"Adding {len(chunks)} documents to ChromaDB...")
    collection.add(
        documents=chunks,
        ids=ids,
        metadatas=metadata
    )
    
    print("Successfully created vector database!")
    print(f"Total chunks added: {len(chunks)}")

if __name__ == "__main__":
    main()