import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yarned_with_love.settings")
django.setup()

from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

def cleanup_social_apps():
    print("Checking for duplicate SocialApps...")
    
    apps = SocialApp.objects.all()
    for app in apps:
        print(f"Found App: Provider={app.provider}, Name={app.name}, ID={app.id}, Sites={[s.id for s in app.sites.all()]}")

    # specific check for google
    google_apps = SocialApp.objects.filter(provider='google')
    if google_apps.exists():
        print(f"Found {google_apps.count()} Google apps. Deleting ALL to rely on settings.py...")
        google_apps.delete()
        print("Deleted all Google DB entries.")
    else:
        print("No Google apps found in DB.")

if __name__ == "__main__":
    cleanup_social_apps()
