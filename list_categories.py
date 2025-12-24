import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yarned_with_love.settings')
django.setup()

from store.models import Category

print("Existing Categories:")
for cat in Category.objects.all():
    print(f"- '{cat.name}' (slug: {cat.slug})")
