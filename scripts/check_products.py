import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yarned_with_love.settings')
django.setup()

from store.models import Product

print("\n=== Current Products ===\n")
for p in Product.objects.all():
    print(f"ID: {p.id} | Name: {p.name} | Image: {p.image} | Price: ${p.price}")

# Delete duplicate sunflower if exists
duplicate = Product.objects.filter(name='Crochet Sunflower').first()
if duplicate:
    print(f"\n✓ Removing duplicate: {duplicate.name} (ID: {duplicate.id})")
    duplicate.delete()

# Make sure the right product has the right image
sunflower = Product.objects.filter(name='Yellow Crocheted Sunflower in Pot').first()
if sunflower and not sunflower.image:
    print(f"✓ Adding image to Sunflower product...")
    from django.core.files.storage import default_storage
    from django.core.files.base import ContentFile
    
    # Read the product_1.png file
    product_file_path = os.path.join('media', 'products', 'product_1.png')
    if os.path.exists(product_file_path):
        with open(product_file_path, 'rb') as f:
            sunflower.image.save('sunflower.png', ContentFile(f.read()), save=True)
        print(f"✓ Image added to {sunflower.name}")

print("\n=== Updated Products ===\n")
for p in Product.objects.all():
    print(f"ID: {p.id} | Name: {p.name} | Image: {p.image} | Price: ${p.price}")
