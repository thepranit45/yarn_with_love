from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
import logging

logger = logging.getLogger(__name__)

User = get_user_model()

@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    if created:
        logger.info(f"New user created: {instance.email}. Attempting to send welcome email.")
        
        subject = 'Welcome to Yarned with Love! 🧶'
        message = f"""
        Hi {instance.get_display_name()},

        Welcome to the Yarned with Love family! We are so happy to have you here.

        Discover our handcrafted crochet collection made just for you.
        
        Happy Shopping!
        
        Warm regards,
        The Yarned with Love Team
        """
        
        # Only send if API key is set 
        if settings.EMAIL_HOST_PASSWORD:
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [instance.email],
                    fail_silently=False, # Changed to False to ensure we catch errors
                )
                logger.info(f"Welcome email sent successfully to {instance.email}")
            except Exception as e:
                logger.error(f"Error sending welcome email to {instance.email}: {e}")
        else:
             logger.warning("EMAIL_HOST_PASSWORD (SendGrid API Key) is missing. Skipping welcome email.")
