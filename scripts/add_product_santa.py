import os
import sys
import django
from decimal import Decimal
from pathlib import Path

# Setup Django
sys.path.append(str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yarned_with_love.settings")
django.setup()

from store.models import Product, Category
from users.models import CustomUser

def add_product():
    try:
        # Get or Create Category
        category, _ = Category.objects.get_or_create(
            name='Keychains',
            defaults={'slug': 'keychains'}
        )

        # Get Artisan (assuming 'mansi' exists, or first artisan)
        artisan = CustomUser.objects.filter(is_artisan=True, username='mansi').first()
        if not artisan:
            print("Artisan 'mansi' not found, defaulting to first available artisan.")
            artisan = CustomUser.objects.filter(is_artisan=True).first()
        
        if not artisan:
            print("Error: No artisan found to assign product to.")
            return

        # Create Product
        product, created = Product.objects.get_or_create(
            name="Santa Claus Keychain",
            defaults={
                'description': "Adorable handmade crocheted Santa Claus keychain. Detailed with a tiny hat, beard, and cute expression. Perfect for Christmas gifts or adding a festive touch to your keys/bag!",
                'short_description': "Cute crocheted Santa keychain.",
                'price': Decimal("149.00"),  # Default price
                'category': category,
                'artisan': artisan,
                'is_active': True,
                'image': 'products/keychain/santa_keychain.jpg',
                'estimated_days_to_complete': 3
            }
        )

        if created:
            print(f"Successfully created product: {product.name}")
        else:
            print(f"Product already exists: {product.name}")
            # Optional: Update image if it exists but image changed
            product.image = 'products/keychain/santa_keychain.jpg'
            product.save()
            print("Updated product image.")

    except Exception as e:
        print(f"Error adding product: {e}")

if __name__ == "__main__":
    add_product()
