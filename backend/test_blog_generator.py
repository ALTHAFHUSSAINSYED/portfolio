import os
from dotenv import load_dotenv
from agent_service import BlogGenerator, handle_agent_query

# Load environment variables
load_dotenv()

def test_blog_generator():
    """Test the BlogGenerator class with the new AI service integration"""
    print("\n=== Testing BlogGenerator with AI service integration ===")
    
    # Create blog generator
    blog_generator = BlogGenerator()
    
    # Generate a blog post
    topic = "Python Web Development Trends"
    print(f"Generating blog on topic: {topic}")
    
    # Generate the blog
    blog = blog_generator.generate_blog(topic)
    
    if blog:
        print("\nBlog generation successful!")
        print(f"Title: {blog.get('title')}")
        print(f"Summary: {blog.get('summary')}")
        print(f"Tags: {', '.join(blog.get('tags', []))}")
        print("\nContent Preview:")
        
        # Print the first 200 characters of content
        content = blog.get('content', '')
        print(f"{content[:200]}...")
        
        print(f"\nTotal content length: {len(content)} characters")
    else:
        print("Blog generation failed.")

def test_agent_query():
    """Test the agent query handling with AI service integration"""
    print("\n=== Testing Agent Query with AI service integration ===")
    
    # Test queries
    queries = [
        "What are the latest trends in web development?",
        "Tell me about portfolio projects"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        
        # Process the query
        result = handle_agent_query(query)
        
        # Display the results
        print("\nAgent response:")
        print(f"{result.get('reply')[:200]}...")
        print(f"\nSource: {result.get('source')}")

if __name__ == "__main__":
    # Test blog generation
    test_blog_generator()
    
    # Test agent query handling
    test_agent_query()