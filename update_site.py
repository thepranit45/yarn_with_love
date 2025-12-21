import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yarned_with_love.settings")
django.setup()

from django.contrib.sites.models import Site

def update_site():
    print("Updating Site ID 1...")
    try:
        site = Site.objects.get(id=1)
        old_domain = site.domain
        site.domain = "yarnwithlove.store"
        site.name = "Yarned With Love"
        site.save()
        print(f"Success! Updated Site ID 1: {old_domain} -> {site.domain}")
    except Site.DoesNotExist:
        print("Error: Site ID 1 does not exist. Creating it...")
        Site.objects.create(domain="yarnwithlove.store", name="Yarned With Love")
        print("Created Site ID 1.")

if __name__ == "__main__":
    update_site()
