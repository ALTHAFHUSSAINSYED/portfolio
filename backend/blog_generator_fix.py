"""
Fix for BlogGenerator.generate_blog method to focus on IT software topics
and properly categorize blog posts
"""

import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_agent_service():
    """
    This function provides a fixed version of BlogGenerator.generate_blog method
    that focuses on IT software topics and properly categorizes blog posts.
    
    Copy this implementation into your agent_service.py file to replace the
    existing BlogGenerator.generate_blog method.
    """
    
    print("=" * 80)
    print("COPY THE FOLLOWING CODE INTO YOUR agent_service.py FILE")
    print("Replace the existing BlogGenerator.generate_blog method with this implementation")
    print("=" * 80)
    
    print("""
    def generate_blog(self, topic=None):
        \"\"\"Generate a blog using AI and web search data\"\"\"
        try:
            # Pick a topic if none provided
            if not topic:
                # Organized IT software topics by categories
                it_software_topics = {
                    "Cloud Computing": [
                        "AWS Lambda vs Azure Functions: Serverless Comparison",
                        "Multi-Cloud Deployment Strategies for Enterprise Applications",
                        "Cloud Cost Optimization Best Practices",
                        "Kubernetes vs Docker Swarm for Container Orchestration",
                        "Serverless Architecture Patterns and Use Cases"
                    ],
                    "AI and ML": [
                        "MLOps Best Practices for Production AI Systems",
                        "NLP Techniques for Software Documentation",
                        "Computer Vision Applications in Software Testing",
                        "Machine Learning Model Monitoring in Production",
                        "Ethical Considerations in Enterprise AI Development"
                    ],
                    "DevOps": [
                        "CI/CD Pipeline Optimization for Microservices",
                        "Infrastructure as Code with Terraform and Ansible",
                        "GitOps Workflow for Kubernetes Applications",
                        "Observability Platforms: Prometheus vs Grafana vs Datadog",
                        "DevSecOps: Integrating Security into DevOps Workflows"
                    ],
                    "Software Development": [
                        "Microservices vs Monoliths: Architecture Tradeoffs",
                        "API Gateway Patterns and Implementation",
                        "Domain-Driven Design in Modern Software Development",
                        "Event-Driven Architecture with Kafka and RabbitMQ",
                        "Clean Code Principles for Enterprise Applications"
                    ],
                    "Databases": [
                        "NoSQL Database Selection: MongoDB vs Cassandra vs DynamoDB",
                        "Database Sharding Strategies for High-Scale Applications",
                        "Graph Databases: Neo4j vs Amazon Neptune",
                        "Data Warehousing with Snowflake and BigQuery",
                        "Time-Series Database Solutions for Monitoring Applications"
                    ],
                    "Cybersecurity": [
                        "Zero Trust Architecture Implementation",
                        "Container Security Best Practices",
                        "API Security Testing Strategies",
                        "SAST vs DAST in DevSecOps Pipelines",
                        "Cloud Security Posture Management"
                    ]
                }
                
                # Select a random category and then a topic from that category
                category = random.choice(list(it_software_topics.keys()))
                topic_from_category = random.choice(it_software_topics[category])
                
                # Store both the category and the topic
                self.current_category = category
                topic = topic_from_category
                
            logger.info(f"Generating blog on topic: {topic}")
            
            # Search for information on the topic
            search_results = self.search_engine.search_web(topic, max_results=5)
            
            # Retrieve recent news about the topic
            news_results = self.search_engine.search_web(f"{topic} latest news", max_results=3)
            
            # Use Gemini service if available (preferred)
            if gemini_client:
                try:
                    logger.info("Generating blog with Gemini AI")
                    blog_data = gemini_client.generate_blog_post(
                        topic=topic,
                        research_info=search_results,
                        news_info=news_results
                    )
                    
                    # Format the blog with category
                    blog = {
                        "title": blog_data.get("title") or f"Latest Insights on {topic}",
                        "content": blog_data.get("content") or f"Blog content about {topic} will be available soon.",
                        "topic": topic,
                        "created_at": datetime.now(),
                        "tags": blog_data.get("tags", [topic.lower(), "technology", "development"]),
                        "summary": blog_data.get("summary", "Insights on technology trends."),
                        "published": True,
                        "sources": [result.get("link") for result in search_results if result.get("link")],
                        # Use category from AI response if available, otherwise use the one from topic selection
                        "category": blog_data.get("category") or getattr(self, "current_category", "Technology")
                    }
                    return blog
                except Exception as e:
                    logger.error(f"Error with Gemini blog generation: {e}")
            
            # Create fallback blog if Gemini is not available or failed
            logger.warning("Gemini AI failed or not available, using fallback blog generator")
            
            # Process news results for fallback blog
            news_context = ""
            for i, news in enumerate(news_results):
                news_context += f"News {i+1}: {news.get('title', '')}\n"
                if news.get('snippet'):
                    news_context += f"{news.get('snippet')}\n\n"
            
            # Create simple fallback blog with available information
            fallback_blog = {
                "title": f"Latest Insights on {topic}",
                "content": f\"\"\"# {topic}: Essential Guide for IT Professionals
                
                ## Introduction
                
                {topic} is a critical area in modern software development. This article provides a technical overview for IT professionals.
                
                ## Key Concepts
                
                Understanding the fundamentals of {topic} requires knowledge of current best practices and implementation strategies.
                
                ## Implementation Strategies
                
                Professionals implementing {topic} should focus on scalability, security, and maintainability.
                
                ## Future Trends
                
                The field of {topic} continues to evolve rapidly with new techniques and technologies emerging.
                
                ## Conclusion
                
                As we explore {topic} further, IT professionals should stay updated with the latest developments and best practices.
                \"\"\",
                "topic": topic,
                "created_at": datetime.now(),
                "tags": [topic.lower().replace(" ", "-"), "software-development", "technology", "it-professional", "technical-guide"],
                "summary": f"A technical guide to {topic} for IT professionals focusing on implementation strategies and best practices.",
                "published": True,
                "sources": [result.get("link") for result in search_results if result.get("link")],
                "category": getattr(self, "current_category", "Technology")
            }
            return fallback_blog
            
        except Exception as e:
            logger.error(f"Error generating blog: {e}")
            # Ultimate fallback if everything else fails
            return {
                "title": "Latest IT Software Insights",
                "content": "# IT Software Trends\\n\\nStay tuned for our latest blog post on software development trends and innovations.",
                "topic": topic or "Software Development Trends",
                "created_at": datetime.now(),
                "tags": ["technology", "software-development", "it-trends", "programming", "devops"],
                "summary": "Upcoming blog on IT software trends and innovations.",
                "published": True,
                "sources": [],
                "category": "Software Development"
            }
    """)
    print("=" * 80)
    print("END OF CODE")
    print("=" * 80)

if __name__ == "__main__":
    update_agent_service()