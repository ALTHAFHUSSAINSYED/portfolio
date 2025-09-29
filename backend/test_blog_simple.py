from datetime import datetime, UTC
import logging
from ai_service import gemini_service
import asyncio
from notification_service import NotificationService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_blog_generation():
    try:
        # Generate blog content
        topic = "Latest Trends in AI and Machine Learning"
        content = gemini_service.generate_blog_post(topic)
        
        if content and isinstance(content, dict):
            logger.info("Blog generated successfully!")
            logger.info(f"Title: {content['title']}")
            logger.info(f"Summary: {content.get('summary', 'No summary available')}")
            logger.info(f"Tags: {', '.join(content.get('tags', []))}")
            
            # Send success notification
            notification_service = NotificationService()
            blog_data = {
                **content,
                "author": "Allu Bot",
                "createdAt": datetime.now(UTC),
                "_id": "test-" + str(int(datetime.now(UTC).timestamp()))
            }
            await notification_service.send_blog_notification(True, blog_data)
            
            return blog_data
    except Exception as e:
        error_msg = f"Error in blog generation: {str(e)}"
        logger.error(error_msg)
        
        # Send failure notification
        notification_service = NotificationService()
        await notification_service.send_blog_notification(False, None, error_msg)
    return None

async def main():
    logger.info("Starting test blog generation at: %s", datetime.now(UTC))
    await test_blog_generation()

if __name__ == "__main__":
    asyncio.run(main())