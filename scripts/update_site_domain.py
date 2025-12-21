import os
import django
import sys

# Add project root to path
sys.path.append('D:/YWL')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yarned_with_love.settings')
django.setup()

from django.contrib.sites.models import Site

def run():
    print("Updating Site configuration for Production...")
    
    # Get the default site (ID=1)
    try:
        site = Site.objects.get(id=1)
        print(f"Current Domain: {site.domain}")
        print(f"Current Name: {site.name}")
        
        # Update to production domain
        # The user seems to use "yarnwithlove.store" based on settings.py
        site.domain = 'yarnwithlove.store'
        site.name = 'Yarned with Love'
        site.save()
        
        print(f"Updated Domain to: {site.domain}")
        print(f"Updated Name to: {site.name}")
        
    except Site.DoesNotExist:
        print("Site with ID 1 does not exist! Creating a new one...")
        Site.objects.create(id=1, domain='yarnwithlove.store', name='Yarned with Love')
        print("Created new Site object.")

if __name__ == "__main__":
    run()
