"""
Script to fix agent_service.py and add Gemini integration
"""
import re
import os

# Read the original file
with open('agent_service.py', 'r') as file:
    content = file.read()

# Fix the _generate_blog_with_ai method to use Gemini
pattern = re.compile(r'def _generate_blog_with_ai.*?return self._generate_fallback_blog\(topic, detailed_content, news_results\)', re.DOTALL)
replacement = '''def _generate_blog_with_ai(self, topic, detailed_content, news_results):
        """Generate blog content using Gemini or OpenAI's models or fallback to a template"""
        try:
            # First try Gemini if available
            if gemini_client and gemini_client.is_available:
                logger.info("Attempting to generate blog with Gemini API")
                try:
                    # Prepare context from research
                    research_context = ""
                    for i, content in enumerate(detailed_content):
                        research_context += f"Source {i+1}: {content.get('title', '')}"
                        if content.get('content'):
                            research_context += f"\\n{content.get('content', '')[:800]}\\n\\n"
                    
                    news_context = ""
                    for i, news in enumerate(news_results):
                        news_context += f"News {i+1}: {news.get('title', '')} - {news.get('description', '')}\\n"
                    
                    # Create prompt for Gemini
                    system_prompt = """You are an expert blog writer specializing in technology and development topics. 
                    Create a high-quality, informative blog post based on the research provided. 
                    The blog should be well-structured, insightful, and professionally written.
                    Include a catchy title, introduction, main sections, and conclusion.
                    Also provide 5 relevant tags and a brief summary."""
                    
                    user_prompt = f"""Topic: {topic}
                    
                    Research Information:
                    {research_context}
                    
                    Latest News:
                    {news_context}
                    
                    Write a comprehensive blog post (800-1200 words) that provides value to readers.
                    Format your response as a JSON object with the following structure:
                    {{
                        "title": "Your catchy blog title",
                        "content": "The full blog content with markdown formatting",
                        "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
                        "summary": "A brief 1-2 sentence summary of the blog"
                    }}
                    """
                    
                    # Call Gemini API
                    response = gemini_client.chat.create(
                        model="gemini-pro",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        temperature=0.7,
                        max_tokens=2500
                    )
                    
                    # Parse the response
                    content = response.choices[0].message.content
                    try:
                        # Extract JSON from response
                        import json
                        blog = json.loads(content)
                        return blog
                    except Exception as json_err:
                        logger.error(f"Error parsing Gemini JSON response: {json_err}")
                        logger.info("Falling back to OpenAI")
                except Exception as e:
                    logger.error(f"Error generating blog with Gemini: {e}")
                    logger.info("Falling back to OpenAI")
            
            # Fall back to OpenAI if Gemini is not available or failed
            if not openai_client:
                logger.error("OpenAI client not available for blog generation")
                return self._generate_fallback_blog(topic, detailed_content, news_results)
                
            # Check if we can actually call the OpenAI API (might have insufficient quota)
            try:
                # Try a small test request first to check quota
                response = openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": "Is this API key working?"}
                    ],
                    max_tokens=10
                )
            except Exception as e:
                logger.error(f"OpenAI API quota error: {e}")
                return self._generate_fallback_blog(topic, detailed_content, news_results)'''

updated_content = pattern.sub(replacement, content)

# Fix the indentation issues in the rest of the method
pattern2 = re.compile(r'                research_context \+= f"{content\.get.*?json_content = content', re.DOTALL)
replacement2 = '''            # Prepare context from research
            research_context = ""
            for i, content in enumerate(detailed_content):
                research_context += f"Source {i+1}: {content.get('title', '')}"
                if content.get('content'):
                    research_context += f"\\n{content.get('content', '')[:800]}\\n\\n"
            
            news_context = ""
            for i, news in enumerate(news_results):
                news_context += f"News {i+1}: {news.get('title', '')} - {news.get('description', '')}\\n"
            
            # Create prompt for OpenAI
            system_prompt = """You are an expert blog writer specializing in technology and development topics. 
            Create a high-quality, informative blog post based on the research provided. 
            The blog should be well-structured, insightful, and professionally written.
            Include a catchy title, introduction, main sections, and conclusion.
            Also provide 5 relevant tags and a brief summary."""
            
            user_prompt = f"""Topic: {topic}
            
            Research Information:
            {research_context}
            
            Latest News:
            {news_context}
            
            Write a comprehensive blog post (800-1200 words) that provides value to readers.
            Format your response as a JSON object with the following structure:
            {{
                "title": "Your catchy blog title",
                "content": "The full blog content with markdown formatting",
                "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
                "summary": "A brief 1-2 sentence summary of the blog"
            }}
            """
            
            try:
                response = openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.7,
                    max_tokens=2500
                )
            except Exception as e:
                logger.error(f"OpenAI API error during blog generation: {e}")
                # Return a fallback blog post if OpenAI call fails
                return {
                    "title": f"Latest Insights on {topic}",
                    "content": f"# {topic}\\n\\n## Introduction\\nThis blog post would normally contain AI-generated content about {topic}. However, there was an issue connecting to the OpenAI API.\\n\\n## What to Expect\\nWhen the API is working correctly, this blog would contain information gathered from various web sources and news articles, processed by AI to create informative content.\\n\\n## About the Technology\\nThis portfolio uses a combination of React, FastAPI, MongoDB, and OpenAI's GPT models to create an interactive and dynamic website with AI-powered features.",
                    "tags": [topic.lower(), "technology", "web development", "portfolio", "ai"],
                    "summary": f"An overview of {topic} and related technologies (generated as a fallback due to API issues)."
                }
            
            # Parse the response
            content = response.choices[0].message.content
            try:
                # Extract JSON from response
                json_content = content'''

updated_content = pattern2.sub(replacement2, updated_content)

# Fix the exception handling and closing of the method
pattern3 = re.compile(r'        except Exception as e:.*?def save_blog_to_database', re.DOTALL)
replacement3 = '''        except Exception as e:
            logger.error(f"Error generating blog with AI: {e}")
            return {
                "title": f"Latest Insights on {topic}",
                "content": "Our blog generation system is currently experiencing technical difficulties. Please check back later for new content.",
                "tags": [topic.lower(), "technology", "development"],
                "summary": "Upcoming blog post on technology trends."
            }
    
    def save_blog_to_database'''

updated_content = pattern3.sub(replacement3, updated_content)

# Write the updated content back to the file
with open('agent_service_fixed.py', 'w') as file:
    file.write(updated_content)

print("Created agent_service_fixed.py with Gemini integration")