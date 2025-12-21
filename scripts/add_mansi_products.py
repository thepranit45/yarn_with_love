import os
import django
import sys
from decimal import Decimal

# Add project root to path
sys.path.append('D:/YWL')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yarned_with_love.settings')
django.setup()

from users.models import CustomUser
from store.models import Product, Category

def run():
    print("Adding products for artist Mansi...")

    # 1. Get or Create Artist 'mansi'
    mansi, created = CustomUser.objects.get_or_create(
        username='mansi',
        defaults={
            'email': 'mansi@yarned.com',
            'is_artisan': True,
            'bio': 'Passionate about creating cute and functional crochet items! ✨'
        }
    )
    if created:
        mansi.set_password('mansi123')
        mansi.save()
        print(f"Created artist: {mansi.username}")
    else:
        print(f"Found artist: {mansi.username}")

    # 2. Define Products Data
    products_data = [
        # HAIR TIE
        {
            'category': 'Hair Tie', 'name': 'Daisy Hair Tie', 'price': 40, 'mrp': None,
            'desc': 'Cute daisy flower hair tie to brighten your hairstyle. handmade with soft yarn.'
        },
        {
            'category': 'Hair Tie', 'name': 'Bow Hair Tie', 'price': 50, 'mrp': None,
            'desc': 'Classic bow design hair tie. Adds a sweet touch to any ponytail.'
        },
        {
            'category': 'Hair Tie', 'name': 'Sunflower Hair Tie', 'price': 50, 'mrp': None,
            'desc': 'Vibrant sunflower hair tie. Perfect for summer vibes! 🌻'
        },
        {
            'category': 'Hair Tie', 'name': 'Love Hair Tie', 'price': 60, 'mrp': None,
            'desc': 'Heart-themed "Love" hair tie. A perfect gift for someone special.'
        },
        {
            'category': 'Hair Tie', 'name': 'Rose Hair Tie', 'price': 50, 'mrp': None,
            'desc': 'Elegant rose flower hair tie. Adds a romantic flair to your look.'
        },

        # FLOWER POT
        {
            'category': 'Flower Pot', 'name': 'Pink Gerbera Flower Pot', 'price': 210, 'mrp': 250,
            'desc': 'Beautiful pink Gerbera flower in a crochet pot. Maintenance-free blooming beauty for your desk!'
        },
        {
            'category': 'Flower Pot', 'name': 'Sunflower Flower Pot', 'price': 210, 'mrp': 250,
            'desc': 'Cheerful sunflower in a crochet pot. Brings sunshine indoors anywhere you place it.'
        },

        # KEY CHAIN
        {
            'category': 'Key Chain', 'name': 'Evil Eye Key Chain', 'price': 60, 'mrp': 75,
            'desc': 'Protective Evil Eye keychain. Stylish and symbolic, perfect for keys or bags.'
        },
        {
            'category': 'Key Chain', 'name': 'Ear Pod Case (Big Size)', 'price': 150, 'mrp': 190,
            'desc': 'Cozy and protective case for your Ear Pods (Big Size). Keeps them scratch-free and cute!'
        }
    ]

    # 3. Create Categories and Products
    for item in products_data:
        # Create/Get Category
        cat_slug = item['category'].lower().replace(' ', '-')
        category, _ = Category.objects.get_or_create(
            name=item['category'],
            defaults={'slug': cat_slug}
        )

        # Create Product (Idempotent)
        product, created = Product.objects.get_or_create(
            name=item['name'],
            artisan=mansi,
            defaults={
                'category': category,
                'price': Decimal(item['price']),
                'mrp': Decimal(item['mrp']) if item['mrp'] else None,
                'description': item['desc'],
                'short_description': item['desc'][:100],
                'key_features': "Handmade\nWashable\nDurable Yarn",
                'is_active': True,
                'estimated_days_to_complete': 3
            }
        )
        if created:
            print(f"Added: {item['name']} - Rs. {item['price']}")
        else:
            print(f"Skipped (Exists): {item['name']}")

    print("All products added successfully! 🧶")

if __name__ == "__main__":
    run()
