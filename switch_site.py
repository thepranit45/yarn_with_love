import os
import django
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yarned_with_love.settings")
django.setup()

from django.contrib.sites.models import Site

def toggle_site(mode):
    try:
        site = Site.objects.get(id=1)
        if mode == 'local':
            site.domain = '127.0.0.1:8000'
            site.name = 'Yarned With Love (Local)'
            print(f"SWITCHED TO LOCAL: {site.domain}")
        else:
            site.domain = 'yarnwithlove.store'
            site.name = 'Yarned With Love'
            print(f"SWITCHED TO PROD: {site.domain}")
        site.save()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Default to local for this fix
    toggle_site('local')
