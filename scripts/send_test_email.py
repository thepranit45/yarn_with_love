import os
import django
import sys
from pathlib import Path

# Setup Django
sys.path.append(str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yarned_with_love.settings")
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def send_test():
    print("Configuring Email Test...")
    print(f"From: {settings.DEFAULT_FROM_EMAIL}")
    print(f"Host: {settings.EMAIL_HOST}")
    
    recipient = input("Enter the email address to send the test to: ")
    
    if not recipient:
        print("No recipient entered.")
        return

    print(f"Sending test email to {recipient}...")
    
    try:
        send_mail(
            subject='Test Email from Yarned with Love',
            message='If you are reading this, your SendGrid SMTP setup is working perfectly! :D',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            fail_silently=False,
        )
        print("SUCCESS: Email sent successfully! Check your inbox (and spam folder).")
    except Exception as e:
        print(f"FAILED: Failed to send email: {e}")

if __name__ == "__main__":
    send_test()
