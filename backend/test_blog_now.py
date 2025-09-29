import asyncio
import os
from datetime import datetime, UTC
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import logging
from notification_service import NotificationService
import ai_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

async def test_blog_generation():
    # Initialize notification service at the start
    notification_service = NotificationService()
    
    try:
        # Generate blog content first
        topic = "Latest Trends in AI and Machine Learning"
        content = ai_service.gemini_service.generate_blog_post(topic)
        
        if not content:
            raise Exception("Failed to generate blog content")
            
        # Try to save to MongoDB if available
        try:
            mongo_url = os.getenv("MONGO_URL")
            if mongo_url:
                client = AsyncIOMotorClient(mongo_url)
                db = client[os.getenv("DB_NAME", "portfolioDB")]
                
                # Add metadata and store in MongoDB
                blog_data = {
                    "title": content["title"],
                    "content": content["content"],
                    "author": "Allu Bot",
                    "createdAt": datetime.now(UTC),
                    "tags": ["AI", "Machine Learning", "Technology"]
                }
                
                # Insert into MongoDB
                result = await db.blogs.insert_one(blog_data)
                blog_data['_id'] = str(result.inserted_id)
            else:
                # If no MongoDB, still create blog data without saving
                blog_data = content
                blog_data.update({
                    "author": "Allu Bot",
                    "createdAt": datetime.now(UTC),
                    "_id": "local-" + str(int(datetime.now(UTC).timestamp()))
                })
        except Exception as db_error:
            logger.error(f"MongoDB error: {db_error}")
            # Continue with local blog data
            blog_data = content
            blog_data.update({
                "author": "Allu Bot",
                "createdAt": datetime.now(UTC),
                "_id": "local-" + str(int(datetime.now(UTC).timestamp()))
            })
        
        client = AsyncIOMotorClient(mongo_url)
        db_name = os.getenv("DB_NAME")
        if not db_name:
            raise ValueError("DB_NAME environment variable is not set")
            
        db = client[db_name]
        
        # Initialize notification service
        notification_service = NotificationService()
        
        # Generate blog content
        topic = "Latest Trends in AI and Machine Learning"
        content = ai_service.gemini_service.generate_blog_post(topic)
        
        if content:
            # Add metadata and store in MongoDB
            blog_data = {
                "title": content["title"],
                "content": content["content"],
                "author": "Allu Bot",
                "createdAt": datetime.now(UTC),
                "tags": ["AI", "Machine Learning", "Technology"]
            }
            
            # Insert into MongoDB and get the ID
            result = await db.blogs.insert_one(blog_data)
            blog_data['_id'] = str(result.inserted_id)
            
            # Send notification
            await notification_service.send_blog_notification(True, blog_data)
            logger.info(f"Blog generated and stored with ID: {blog_data['_id']}")
            return blog_data
    except Exception as e:
        error_msg = f"Error in blog generation: {str(e)}"
        logger.error(error_msg)
        await notification_service.send_blog_notification(False, None, error_msg)
    return None

async def main():
    logger.info("Starting test blog generation at: %s", datetime.now(UTC))
    result = await test_blog_generation()
    if result:
        logger.info("Blog generation successful!")
        logger.info(f"Blog title: {result['title']}")
        logger.info(f"Blog ID: {result['_id']}")
    else:
        logger.error("Blog generation failed!")

if __name__ == "__main__":
    asyncio.run(main())