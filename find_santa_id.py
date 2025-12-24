import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yarned_with_love.settings')
django.setup()

from store.models import Product

products = Product.objects.filter(name__icontains='Santa')
for p in products:
    print(f"ID: {p.id}, Name: {p.name}, Category: {p.category.name if p.category else 'None'}")
