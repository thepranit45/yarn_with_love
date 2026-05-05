from django.contrib.auth.signals import user_logged_out
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)

User = get_user_model()

import threading
@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    if created:
        def start_email():
            logger.info(f"New user created: {instance.email}. Attempting to send welcome email in background.")
            
            subject = 'Welcome to Yarned with Love! 🧶'
            message = f"""
            Hi {instance.get_display_name()},

            Welcome to the Yarned with Love family! We are so happy to have you here.

            Discover our handcrafted crochet collection made just for you.
            
            Happy Shopping!
            
            Warm regards,
            The Yarned with Love Team
            """
            
            if settings.EMAIL_HOST_PASSWORD:
                try:
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [instance.email],
                        fail_silently=True,
                    )
                    logger.info(f"Welcome email sent successfully to {instance.email}")
                except Exception as e:
                    logger.error(f"Error sending welcome email to {instance.email}: {e}")
            else:
                 logger.warning("EMAIL_HOST_PASSWORD is missing. Skipping welcome email.")

        # Start email sending in a separate thread to prevent 502 timeouts
        threading.Thread(target=start_email).start()
