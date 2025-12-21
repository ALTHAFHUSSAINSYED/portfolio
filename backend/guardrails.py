"""Guardrails for chatbot responses and query handling."""

GREETING_PATTERNS = {
    "hello": ["Hello! How can I assist you with technology today?", "Hi there! Ready to discuss tech with you!"],
    "hi": ["Hi! What tech topic would you like to explore?", "Hello! Let's talk about technology!"],
    "hey": ["Hey! Ready to help with your tech questions!", "Hi there! What would you like to know about technology?"],
    "good morning": ["Good morning! Ready to explore tech topics with you!", "Morning! How can I help with technology today?"],
    "good afternoon": ["Good afternoon! Let's discuss technology!", "Hi there! Ready to help with your tech queries!"],
    "good evening": ["Good evening! Ready to assist with tech topics!", "Evening! What technology would you like to discuss?"],
    "thank you": ["You're welcome! Feel free to ask more tech questions!", "Glad I could help! Let me know if you need anything else!"],
    "thanks": ["You're welcome! Always here to help with tech!", "Happy to help! Feel free to ask more questions!"],
    "bye": ["Goodbye! Feel free to return for more tech discussions!", "Take care! Come back if you have more tech questions!"]
}

BLOCKED_TOPICS = [
    "personal information",
    "political",
    "religious",
    "medical advice",
    "financial advice",
    "legal advice",
    "inappropriate content",
    "offensive content",
    "chatbot creation",
    "system details",
    "training data",
    "data sources",
    "internal operations"
]

TECH_CATEGORIES = {
    "programming": ["python", "java", "javascript", "coding", "programming", "software development"],
    "web_dev": ["frontend", "backend", "web", "html", "css", "react", "angular", "node"],
    "devops": ["docker", "kubernetes", "ci/cd", "jenkins", "git", "devops"],
    "cloud": ["aws", "azure", "gcp", "cloud computing", "serverless"],
    "data": ["database", "sql", "nosql", "mongodb", "postgresql"],
    "ai_ml": ["artificial intelligence", "machine learning", "deep learning", "neural networks"],
    "security": ["cybersecurity", "encryption", "security", "authentication"],
    "architecture": ["system design", "microservices", "api design", "scalability"],
    "mobile": ["android", "ios", "mobile development", "react native", "flutter"],
    "networking": ["tcp/ip", "http", "api", "rest", "graphql"]
}

def is_greeting(query: str) -> str:
    """Check if query is a greeting and return appropriate response."""
    query = query.lower().strip()
    for pattern, responses in GREETING_PATTERNS.items():
        if pattern in query:
            from random import choice
            return choice(responses)
    return ""

def is_blocked_topic(query: str) -> bool:
    """Check if query contains blocked topics."""
    query = query.lower()
    return any(topic in query for topic in BLOCKED_TOPICS)

def get_tech_category(query: str) -> str:
    """Identify the technical category of the query."""
    query = query.lower()
    for category, keywords in TECH_CATEGORIES.items():
        if any(keyword in query for keyword in keywords):
            return category
    return ""

def sanitize_response(response: str) -> str:
    """Sanitize response to remove any sensitive information."""
    # Remove any mentions of data sources, model names, or internal operations
    sensitive_patterns = [
        r"using (ChromaDB|Gemini|Google|API)",
        r"(fetching|retrieving) (from|data)",
        r"(trained|created|generated|powered) by",
        r"(internet|web) (access|connection)",
        r"(searching|querying) (online|internet)",
        r"(database|storage|vector store)"
    ]
    
    import re
    cleaned_response = response
    for pattern in sensitive_patterns:
        cleaned_response = re.sub(pattern, "", cleaned_response, flags=re.IGNORECASE)
    
    return cleaned_response.strip()

def is_tech_query(query: str) -> bool:
    """Determine if the query is technology-related."""
    # Check if query matches any tech category
    if get_tech_category(query):
        return True
        
    # Additional tech-related keywords
    tech_indicators = [
        r"\b(code|program|develop|build|implement|deploy|configure|setup|install)\b",
        r"\b(error|bug|issue|problem|fix|debug|troubleshoot)\b",
        r"\b(framework|library|package|module|component)\b",
        r"\b(server|client|database|api|endpoint)\b",
        r"\b(best practice|pattern|architecture|design)\b"
    ]
    
    import re
    return any(re.search(pattern, query, re.IGNORECASE) for pattern in tech_indicators)

def format_tech_response(response: str) -> str:
    """Format and structure technical responses."""
    # Ensure code blocks are properly formatted
    import re
    
    # Format inline code
    response = re.sub(r'`([^`]+)`', r'`\1`', response)
    
    # Ensure code blocks have language specification
    def format_code_block(match):
        code = match.group(1)
        if not code.startswith(('python', 'javascript', 'java', 'html', 'css')):
            return f"```python\n{code}\n```"
        return f"```{code}\n```"
    
    response = re.sub(r'```(.*?)```', format_code_block, response, flags=re.DOTALL)
    
    return response