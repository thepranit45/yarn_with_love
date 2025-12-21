import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yarned_with_love.settings")
django.setup()

from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

def fix_crash():
    print("Checking for Google App to fix crash...")
    
    # Check if Site ID 1 exists
    try:
        site = Site.objects.get(id=1)
    except Site.DoesNotExist:
        print("Site ID 1 missing. Creating it...")
        site = Site.objects.create(domain="yarnwithlove.store", name="Yarned With Love")

    # Check/Create Google App
    app, created = SocialApp.objects.get_or_create(
        provider='google',
        defaults={
            'name': 'Google (Placeholder)',
            'client_id': 'ENTER_YOUR_CLIENT_ID_HERE',
            'secret': 'ENTER_YOUR_SECRET_HERE',
        }
    )
    
    # Ensure it's linked to the site
    if site not in app.sites.all():
        app.sites.add(site)
        print(f"Linked Google App to Site {site.domain}")
    
    if created:
        print("SUCCESS: Created placeholder Google App. The 500 error should be gone.")
    else:
        print("Google App already exists. Checked site linkage.")

if __name__ == "__main__":
    fix_crash()
