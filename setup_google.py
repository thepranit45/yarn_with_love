import os
import django
import sys

# Setup Django Environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yarned_with_love.settings")
django.setup()

from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

def setup_google():
    print("="*50)
    print("   GOOGLE AUTHENTICATION SETUP WIZARD   ")
    print("="*50)
    
    # 1. Ensure Site is configured
    site = Site.objects.get(id=1)
    print(f"Current Site Domain: {site.domain}")
    print(f"Current Site Name:   {site.name}")
    print("-" * 50)

    # 2. Check for existing App
    existing = SocialApp.objects.filter(provider='google').first()
    if existing:
        print(f"Found EXISTING Google App configuration.")
        print(f"Client ID: {existing.client_id}")
        print("To overwrite this, continue. To cancel, press Ctrl+C.")
    else:
        print("No Google App configuration found.")

    print("\nPlease enter your Google OAuth credentials:")
    print("(You can find these in the Google Cloud Console -> APIs & Services -> Credentials)")
    
    # 3. Get Credentials
    client_id = input("Enter Client ID: ").strip()
    secret = input("Enter Client Secret: ").strip()

    if not client_id or not secret:
        print("\nError: Client ID and Secret are required!")
        return

    # 4. Save to Database
    if existing:
        app = existing
        app.client_id = client_id
        app.secret = secret
        app.name = "Google"
        app.save()
        print("\nUpdated existing Google App configuration.")
    else:
        app = SocialApp.objects.create(
            provider='google',
            name='Google',
            client_id=client_id,
            secret=secret
        )
        print("\nCreated NEW Google App configuration.")

    # 5. Link to Site
    app.sites.add(site)
    print(f"Linked App to Site: {site.domain}")
    
    print("="*50)
    print("SUCCESS! Google Auth is now configured.")
    print("You can now restart your server and log in.")
    print("="*50)

if __name__ == "__main__":
    try:
        setup_google()
    except KeyboardInterrupt:
        print("\nSetup cancelled.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
