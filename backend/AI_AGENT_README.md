# AI Agent Service for Portfolio

This document explains how to configure and use the AI agent service for your portfolio.

## Overview

The AI agent service powers two main features:
1. **Automatic blog generation** - Creates daily blog posts on technology topics
2. **Interactive chat agent** - Answers questions about your portfolio and related topics

## Configuration

### Required Environment Variables

Add these to your `.env` file:

```bash
# Primary AI Service - Required
GEMINI_API_KEY="your_gemini_api_key"  # Get from https://makersuite.google.com/app/apikey

# Web Search - Highly Recommended
SERPER_API_KEY="your_serper_dev_api_key"  # Get from https://serper.dev

# Optional Fallbacks
NEWS_API_KEY="your_news_api_key"  # For enhanced news content
```

### Priority of Services

The system uses services in this order:

1. **AI Services**: 
   - Gemini API (primary)

2. **Search Services**:
   - Serper.dev API (primary)
   - DuckDuckGo scraping (fallback)

## Features

### Blog Generation

The agent automatically generates blog posts on technology topics:

- **Scheduled**: Daily at 1 AM
- **On-demand**: Via API endpoint `/api/blogs/generate`
- **Topics**: Randomly selected or user-specified

### Chat Agent

The chat agent answers questions using:

1. Web search to find relevant information
2. AI processing to generate a helpful response
3. Source attribution for transparency

## API Endpoints

- `POST /api/chat`: Send a message to the chat agent
  ```json
  {
    "message": "Tell me about your portfolio projects",
    "session_id": "user_session_123"
  }
  ```

- `POST /api/blogs/generate`: Generate a blog post
  ```json
  {
    "topic": "Modern JavaScript Frameworks"
  }
  ```

- `GET /api/blogs`: Get all published blogs

## Testing

You can test the AI agent service using these scripts:

- `test_blog_generator.py`: Tests blog generation functionality
- `test_serper.py`: Tests the Serper.dev API integration
- `test_api.py`: Tests the API endpoints

## Troubleshooting

If you encounter issues:

1. **Check API Keys**: Ensure your Gemini API key and Serper.dev API key are correct
2. **Check Logs**: Look in the `agent.log` file for error messages
3. **Test Components**: Run the test scripts to identify specific issues