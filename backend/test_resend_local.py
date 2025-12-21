import os
import resend

# Test Resend email locally
# Using the key from conversation: re_EyWvGNPM_Hz4ppqxzRKZ4U5Qgu8kph6nu
resend.api_key = "re_EyWvGNPM_Hz4ppqxzRKZ4U5Qgu8kph6nu"

try:
    params = {
        "from": "Portfolio Contact <contact@althafportfolio.site>",
        "to": ["allualthaf42@gmail.com"],
        "subject": "Test Email from Portfolio",
        "html": "<strong>This is a test email from your portfolio contact form!</strong><p>If you receive this, Resend is working correctly.</p>",
    }

    email = resend.Emails.send(params)
    print("✅ SUCCESS! Email sent:")
    print(email)
except Exception as e:
    print("❌ ERROR sending email:")
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {str(e)}")
