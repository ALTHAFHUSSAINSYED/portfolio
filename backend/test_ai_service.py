"""
Test script for the Gemini AI service

This script demonstrates how to use the AI service in the portfolio application.
"""

from ai_service import gemini_service
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_direct_generation():
    """Test direct content generation"""
    prompt = "Write a short paragraph about AI in web development"
    
    print("\n===== Testing Direct Content Generation =====")
    result = gemini_service.generate_content(prompt)
    print(result)

def test_chat():
    """Test chat functionality"""
    print("\n===== Testing Chat Functionality =====")
    
    # Start a new chat
    gemini_service.start_chat()
    
    # Send a message
    response1 = gemini_service.chat("What are the best practices for portfolio websites?")
    print("Response 1:", response1)
    
    # Send a follow-up message
    response2 = gemini_service.chat("How can I showcase my projects effectively?")
    print("\nResponse 2:", response2)

def test_blog_generation():
    """Test blog post generation"""
    print("\n===== Testing Blog Post Generation =====")
    
    # Sample research information
    research_info = [
        {
            "title": "Modern Web Development Trends",
            "content": "Progressive Web Apps (PWAs) continue to gain traction as they offer app-like experiences on the web. They work offline, load quickly, and can send push notifications. Frameworks like React, Vue, and Angular dominate the frontend landscape, with each offering unique advantages for different use cases."
        },
        {
            "title": "JavaScript in 2023",
            "content": "JavaScript continues to evolve with new features in ES2023. The rise of TypeScript provides type safety for large codebases. Node.js and Deno offer robust backend capabilities for JavaScript developers."
        }
    ]
    
    # Sample news information
    news_info = [
        {
            "title": "New React Features Announced",
            "description": "React 19 is on the horizon with improved performance and new hooks."
        },
        {
            "title": "Browser Support for CSS Container Queries",
            "description": "Major browsers now support CSS Container Queries, enabling more responsive designs."
        }
    ]
    
    # Generate a blog post
    blog = gemini_service.generate_blog_post(
        topic="Modern Frontend Development Techniques",
        research_info=research_info,
        news_info=news_info
    )
    
    # Print the blog post
    print("Title:", blog.get("title"))
    print("Summary:", blog.get("summary"))
    print("Tags:", blog.get("tags"))
    print("\nExcerpt:", blog.get("content")[:300] + "...")

def test_query_answering():
    """Test query answering"""
    print("\n===== Testing Query Answering =====")
    
    # Sample context information
    context = [
        {
            "title": "About Althaf",
            "content": "Althaf is a full-stack developer with expertise in React, Node.js, and cloud technologies. He has worked on numerous projects including e-commerce platforms, social media applications, and data visualization tools."
        },
        {
            "title": "Portfolio Projects",
            "content": "Althaf's portfolio includes a real-time chat application built with Socket.io, a machine learning-powered recommendation system, and a responsive e-commerce platform with payment integration."
        }
    ]
    
    # Generate a response to a query
    query = "What kind of projects has Althaf worked on?"
    response = gemini_service.answer_query(query, context)
    
    print("Query:", query)
    print("Response:", response)

def test_langchain_integration():
    """Test LangChain integration"""
    print("\n===== Testing LangChain Integration =====")
    
    template = "Write a {length} biography for a developer named {name} who specializes in {specialties}."
    inputs = {
        "length": "short",
        "name": "Althaf",
        "specialties": "React, Node.js, and AI integration"
    }
    
    result = gemini_service.generate_with_langchain(template, inputs)
    print(result)

if __name__ == "__main__":
    print("Starting AI Service Tests...")
    
    try:
        # Test direct content generation
        test_direct_generation()
        
        # Test chat functionality
        test_chat()
        
        # Test blog post generation
        test_blog_generation()
        
        # Test query answering
        test_query_answering()
        
        # Test LangChain integration
        test_langchain_integration()
        
        print("\n===== All tests completed successfully! =====")
    except Exception as e:
        logger.error(f"Error during testing: {e}")
        print(f"\n❌ Test failed with error: {e}")