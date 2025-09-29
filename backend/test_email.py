import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from datetime import datetime, UTC
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_email_config():
    print("\n" + "="*50)
    print("📧 Testing Email Configuration")
    print("="*50)
    
    # Get SendGrid API key
    sendgrid_api_key = os.getenv('SENDGRID_API_KEY')
    if not sendgrid_api_key:
        print("❌ ERROR: SENDGRID_API_KEY not found in environment variables")
        try:
            # Use verified sender for both from_email and to_email
            verified_sender = 'allualthaf42@gmail.com'
            message = Mail(
                from_email=verified_sender,
                to_emails=verified_sender,
                subject='Test Email from Blog Generator',
                html_content=f'''
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2>\ud83d\ude80 Test Email</h2>
                    <p>This is a test email from your blog generation system.</p>
                    <p>Sent at: {datetime.now(UTC).strftime('%B %d, %Y at %H:%M UTC')}</p>
                    <p>If you received this email, your email configuration is working correctly!</p>
                </div>
                '''
            )
            # Send the email
            sg = SendGridAPIClient(sendgrid_api_key)
            response = sg.send(message)
            if response.status_code == 202:
                print("\u2705 Test email sent successfully!")
                return True
            else:
                print(f"\u274c Failed to send email. Status code: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error sending email: {str(e)}")
            return False

if __name__ == "__main__":
    test_email_config()