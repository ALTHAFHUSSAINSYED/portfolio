from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

async def health_check():
    """
    Health check to ensure blog generation is working and handle Render free tier limitations.
    """
    try:
        from database import db
        from notification_service import notification_service
        
        # Check last blog generation time
        last_blog = await db.blogs.find_one(
            sort=[("created_at", -1)]
        )
        
        if last_blog:
            time_since_last = datetime.utcnow() - last_blog['created_at']
            
            # If more than 25 hours since last blog (buffer over 24h)
            if time_since_last > timedelta(hours=25):
                error_msg = f"Blog generation missed. Last blog was {time_since_last.total_seconds()/3600:.1f} hours ago"
                logger.warning(error_msg)
                await notification_service.send_blog_notification(False, error_message=error_msg)
                
                # Try to generate now
                from server import generate_daily_blog
                await generate_daily_blog()
                
            # Log status for monitoring
            logger.info(f"Health check passed. Last blog: {last_blog['title']} ({time_since_last.total_seconds()/3600:.1f}h ago)")
        else:
            error_msg = "No blogs found in database"
            logger.warning(error_msg)
            await notification_service.send_blog_notification(False, error_message=error_msg)
            
    except Exception as e:
        error_msg = f"Health check failed: {str(e)}"
        logger.error(error_msg)
        await notification_service.send_blog_notification(False, error_message=error_msg)