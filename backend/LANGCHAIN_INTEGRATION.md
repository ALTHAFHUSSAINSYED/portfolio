# LangChain Integration for Gemini API

## Overview

This implementation creates a unified AI service that integrates both direct Gemini API access and LangChain with Gemini. The integration allows the portfolio application to use advanced LangChain features while maintaining direct Gemini API access as a fallback.

## Files Modified/Created

1. **ai_service.py**:
   - Created a new service that provides both direct Gemini API access and optional LangChain integration
   - Implements methods for content generation, chat functionality, blog post generation, and query answering
   - Uses lazy loading for LangChain components to avoid unnecessary imports

2. **agent_service.py**:
   - Updated to use the new unified AI service
   - Fixed indentation issues
   - Implemented BlogGenerator class that uses the AI service
   - Enhanced WebSearchEngine class with better fallback mechanisms
   - Updated handle_agent_query to use the new AI service

3. **Test Files**:
   - **test_blog_generator.py**: Tests the BlogGenerator class and query handling
   - **test_api.py**: Tests the API integration

## Features

### Direct Gemini API Integration

- Content generation with prompt engineering
- Chat functionality with conversation history
- Structured outputs (JSON) for blog posts and other content

### LangChain Integration

- Prompt templates
- LLM chains
- Lazy loading to avoid unnecessary dependencies

### Robustness Features

- Graceful fallbacks if either Gemini API or LangChain components fail
- Comprehensive error handling
- Default responses when AI services are unavailable

## Usage Examples

### Generate Content

```python
from ai_service import gemini_service

# Generate simple content
response = gemini_service.generate_content("Explain Python decorators")
print(response)
```

### Chat

```python
from ai_service import gemini_service

# Start a chat session
gemini_service.start_chat()

# Chat with history
response1 = gemini_service.chat("What are the best JavaScript frameworks?")
print(response1)

# Follow-up question (maintains context)
response2 = gemini_service.chat("Which one is best for beginners?")
print(response2)
```

### Generate Blog Posts

```python
from ai_service import gemini_service

# Generate a blog post with research
blog = gemini_service.generate_blog_post(
    topic="Modern JavaScript Frameworks",
    research_info=[
        {"title": "Source 1", "content": "..."},
        {"title": "Source 2", "content": "..."}
    ]
)
print(f"Blog Title: {blog['title']}")
print(f"Blog Content: {blog['content']}")
```

### Use with LangChain

```python
from ai_service import gemini_service

# Generate with LangChain
response = gemini_service.generate_with_langchain(
    template="Explain {topic} in {style} style",
    inputs={"topic": "Python generators", "style": "simple"}
)
print(response)
```

## API Endpoints

The existing API endpoints continue to work with the new implementation:

- `POST /api/chat`: Chat with the agent
- `POST /api/blogs/generate`: Generate a blog post

## Environment Variables

Required environment variables:
- `GOOGLE_API_KEY` or `GEMINI_API_KEY`: For Gemini API access
- `OPENAI_API_KEY`: (Optional) For fallback to OpenAI

## Next Steps

1. Further enhance LangChain integration with more advanced features
2. Implement memory and retrieval systems for improved context awareness
3. Add structured output parsing for more complex tasks
4. Expand test coverage to ensure robustness