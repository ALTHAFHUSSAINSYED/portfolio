import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import logging
from backend.notification_service import notification_service
from backend.ai_service import gemini_service
import asyncio
import time

async def generate_test_blog():
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        import os
        
        # Connect to MongoDB
        mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
        client = AsyncIOMotorClient(mongo_url)
        db = client[os.getenv("DB_NAME", "portfolioDB")]
        
        # Generate blog
        topic = "Latest Trends in AI and Machine Learning"
        content = gemini_service.generate_blog_post(topic)
        if content:
            # Add metadata and store in MongoDB
            blog_data = {
                "title": content["title"],
                "content": content["content"],
                "author": "Allu Bot",
                "createdAt": datetime.utcnow(),
                "tags": ["AI", "Machine Learning", "Technology"]
            }
            
            # Insert into MongoDB and get the ID
            result = await db.blogs.insert_one(blog_data)
            blog_data['_id'] = str(result.inserted_id)
            
            return blog_data
    except Exception as e:
        logging.error(f"Error generating blog: {e}")
    return None

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_blog_generation():
    try:
        logger.info("Starting test blog generation...")
        
        # Try to generate a blog
        blog = generate_test_blog()
        
        if blog and blog.get('title') and blog.get('content'):
            logger.info(f"Blog generated successfully: {blog['title']}")
            await notification_service.send_blog_notification(True, blog_title=blog['title'])
        else:
            error_msg = "Failed to generate blog content"
            logger.error(error_msg)
            await notification_service.send_blog_notification(False, error_message=error_msg)
            
    except Exception as e:
        error_msg = f"Error during blog generation: {str(e)}"
        logger.error(error_msg)
        await notification_service.send_blog_notification(False, error_message=error_msg)

if __name__ == "__main__":
    # Set target time to 10:40 PM UTC
    target_time = datetime.utcnow().replace(hour=22, minute=40, second=0, microsecond=0)
    current_time = datetime.utcnow()
    
    if current_time < target_time:
        wait_seconds = (target_time - current_time).total_seconds()
        print(f"Waiting for {wait_seconds:.0f} seconds until 10:36 PM UTC...")
        time.sleep(wait_seconds)
    
    asyncio.run(test_blog_generation())