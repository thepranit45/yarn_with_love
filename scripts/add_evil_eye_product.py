import os
import django
import sys
from pathlib import Path

# Setup Django
sys.path.append(str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yarned_with_love.settings")
django.setup()

from store.models import Product, Category, ProductImage
from django.contrib.auth import get_user_model
from django.core.files import File

User = get_user_model()

def add_product():
    # 1. Get Artisan
    try:
        artisan = User.objects.get(username='mansi')
    except User.DoesNotExist:
        print("Error: Artisan 'mansi' not found.")
        return

    # 2. Get Category
    category, _ = Category.objects.get_or_create(name='Key Chain')
    
    # 3. Product Details
    name = "Evil Eye Apple Airpod Case"
    description = "Handcrafted crochet Apple Airpod case with Evil Eye design. Protect your pods with good vibes! 🧿✨"
    price = 249.00
    
    # 4. Images (Relative to MEDIA_ROOT)
    # The files are already in d:\YWL\media\products\keychain\...
    # We can just set the path string if the file is already in the right place
    main_image_path = 'products/keychain/evil eye Apple Airpod Case 1.jpeg'
    extra_image_path = 'products/keychain/evil eye Apple Airpod Case 1 (2).jpeg'
    
    # Check if files exist to be safe
    media_root = Path('media')
    if not (media_root / main_image_path).exists():
        print(f"Warning: {main_image_path} not found in media directory.")
    
    # Create Product
    product, created = Product.objects.get_or_create(
        name=name,
        artisan=artisan,
        defaults={
            'category': category,
            'description': description,
            'price': price,
            'image': main_image_path,
            'is_active': True
        }
    )
    
    if created:
        print(f"SUCCESS: Created product: {product.name}")
    else:
        print(f"INFO: Product already exists. Updating details...")
        product.category = category
        product.description = description
        product.price = price
        product.image = main_image_path # Update main image
        product.save()
        print(f"SUCCESS: Updated product: {product.name}")

    # Add Extra Image (ProductImage)
    # Check if this specific extra image already exists for this product to avoid duplicates
    existing_images = ProductImage.objects.filter(product=product, image=extra_image_path).exists()
    
    if not existing_images:
        ProductImage.objects.create(product=product, image=extra_image_path)
        print(f"SUCCESS: Added extra image: {extra_image_path}")
    else:
        print(f"INFO: Extra image already linked.")

if __name__ == "__main__":
    add_product()
