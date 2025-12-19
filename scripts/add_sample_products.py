import os
import sys
import django
from decimal import Decimal

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yarned_with_love.settings')
django.setup()

from store.models import Product, Category
from users.models import CustomUser

# Get or create categories
handmade_category, _ = Category.objects.get_or_create(
    slug='handmade-amigurumi',
    defaults={'name': 'Handmade Amigurumi'}
)

home_decor_category, _ = Category.objects.get_or_create(
    slug='home-decor',
    defaults={'name': 'Home Decor'}
)

# Get or create a default artisan user (or use existing)
artisan, _ = CustomUser.objects.get_or_create(
    username='default_artisan',
    defaults={
        'email': 'artisan@yarnedwithlove.com',
        'is_artisan': True,
        'bio': 'Skilled crochet artisan creating beautiful handmade items'
    }
)

# Product 1: Pink Amigurumi Ball
product1, created1 = Product.objects.get_or_create(
    name='Pink Crocheted Amigurumi Ball',
    artisan=artisan,
    defaults={
        'category': handmade_category,
        'description': 'Adorable handmade pink crocheted amigurumi ball with cute face. Perfect for decoration or as a toy. Each stitch crafted with care.',
        'price': Decimal('15.99'),
        'estimated_days_to_complete': 3,
        'is_active': True
    }
)

# Product 2: Bunny Ice Cream
product2, created2 = Product.objects.get_or_create(
    name='Crocheted Bunny Ice Cream Cone',
    artisan=artisan,
    defaults={
        'category': handmade_category,
        'description': 'Charming white crocheted bunny head sitting in a tan ice cream cone. A playful and whimsical handmade creation perfect for decoration.',
        'price': Decimal('22.99'),
        'estimated_days_to_complete': 4,
        'is_active': True
    }
)

# Product 3: Sunflower in Pot
product3, created3 = Product.objects.get_or_create(
    name='Yellow Crocheted Sunflower in Pot',
    artisan=artisan,
    defaults={
        'category': home_decor_category,
        'description': 'Beautiful handmade yellow sunflower with grey center and green leaves planted in a cozy beige pot. Brighten any space with this cheerful creation.',
        'price': Decimal('24.99'),
        'estimated_days_to_complete': 5,
        'is_active': True
    }
)

# Print results
print("✓ Products added successfully!")
print(f"  1. {product1.name} - ${product1.price} - {'Created' if created1 else 'Already exists'}")
print(f"  2. {product2.name} - ${product2.price} - {'Created' if created2 else 'Already exists'}")
print(f"  3. {product3.name} - ${product3.price} - {'Created' if created3 else 'Already exists'}")
print(f"\nArtisan: {artisan.username} (ID: {artisan.id})")
