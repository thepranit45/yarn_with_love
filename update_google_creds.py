import os
import django
import sys

# Setup Django environment
sys.path.append('d:\\YWL')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yarned_with_love.settings')
django.setup()

from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

def update_google_app():
    try:
        # Client ID and Secret from user screenshot
        client_id = '23789169144-umvq6obgrf0rkb2bt90uq5roupsj0vqm.apps.googleusercontent.com'
        secret = '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'
        
        # Determine the site
        # Usually site with ID 1 is example.com, we might need to check active site or localhost
        # For local dev, typically ID 1 or a site named 'localhost' is used.
        # Let's get the current site or create one for localhost if strictly needed, 
        # but typically updating the existing SocialApp is enough.
        
        app, created = SocialApp.objects.get_or_create(
            provider='google',
            defaults={
                'name': 'Google Local',
                'client_id': client_id,
                'secret': secret,
            }
        )
        
        if not created:
            print(f"Updating existing app: {app.name}")
            app.client_id = client_id
            app.secret = secret
            app.name = 'Google Local'
            app.save()
        else:
            print(f"Created new app: {app.name}")
        
        # Ensure it's attached to the current site (usually ID 1)
        current_site = Site.objects.get(pk=1)
        app.sites.add(current_site)
        
        print("Successfully updated Google SocialApp credentials.")
        
    except Exception as e:
        print(f"Error updating SocialApp: {e}")

if __name__ == '__main__':
    update_google_app()
