import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yarned_with_love.settings')
django.setup()

from store.models import Product

try:
    p = Product.objects.get(id=31)
    p.price = 70.00
    p.mrp = 130.00
    p.save()
    print(f"Updated {p.name}: Price=₹{p.price}, MRP=₹{p.mrp}")
except Product.DoesNotExist:
    print("Product ID 31 not found!")
