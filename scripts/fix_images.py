import os
import sys
import django
from shutil import copyfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yarned_with_love.settings')
django.setup()

from store.models import Product
from django.core.files.base import ContentFile

print("\n=== Fixing Product Images ===\n")

# Fix the sunflower without image
sunflower = Product.objects.filter(name='Yellow Crocheted Sunflower in Pot').first()
if sunflower and not sunflower.image:
    print(f"Adding image to: {sunflower.name}")
    product_file_path = os.path.join('media', 'products', 'product_1.png')
    if os.path.exists(product_file_path):
        with open(product_file_path, 'rb') as f:
            sunflower.image.save('sunflower.png', ContentFile(f.read()), save=True)
        print(f"✓ Image added successfully!")

print("\n=== Final Product Status ===\n")
for p in Product.objects.all():
    status = "✓" if p.image else "✗"
    print(f"{status} ID: {p.id} | {p.name} | Image: {p.image}")
