import os
import django
import sys
import random

# Add project root to path
sys.path.append('D:/YWL')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yarned_with_love.settings')
django.setup()

from users.models import CustomUser
from store.models import Product, Review

def run():
    print("Adding dummy Indian reviews...")

    # Ensure we have a user to attach reviews to
    user, _ = CustomUser.objects.get_or_create(
        username='dummy_reviewer', 
        defaults={'email': 'dummy@example.com'}
    )
    if not user.check_password('pass'):
        user.set_password('pass')
        user.save()

    products = list(Product.objects.filter(is_active=True))
    if not products:
        print("No products found! Please add products first.")
        return

    reviews_data = [
        ("Priya Sharma", "Absolutely in love with this! The quality is unmatched. ❤️"),
        ("Aarav Patel", "A bit pricey but totally worth it for the handmade feel."),
        ("Diya Singh", "Bought this as a gift for my mom and she cried happy tears!"),
        ("Rohan Gupta", "Delivery was fast and the packaging was so cute."),
        ("Ananya Verma", "The colors are even more vibrant in person. Will buy again!"),
        ("Vihaan Kumar", "Perfect stitching. You can tell it was made with love."),
        ("Ishita Reddy", "So soft and cozy! Highly recommended."),
        ("Kabir  Malhotra", "Amazing work. Keep it up! 👍"),
        ("Sana Khan", "Just beautiful. Thank you so much!"),
        ("Arjun Nair", "Exceeded my expectations. 5 stars! ⭐⭐⭐⭐⭐")
    ]

    count = 0
    for name, comment in reviews_data:
        product = random.choice(products)
        
        # Check if this "dummy user" already reviewed this product to avoid unique constraint
        # But wait, unique_together might have been removed or we can just skip
        if Review.objects.filter(product=product, customer=user).exists():
            # Try to find another product
            found_new = False
            for p in products:
                if not Review.objects.filter(product=p, customer=user).exists():
                    product = p
                    found_new = True
                    break
            if not found_new:
                # If dummmy user reviewed ALL products, create a new dummy user
                import uuid
                user, _ = CustomUser.objects.get_or_create(username=f'dummy_{uuid.uuid4().hex[:6]}')
        
        Review.objects.create(
            product=product,
            customer=user,
            rating=5,
            comment=comment,
            customer_name=name
        )
        print(f"Added review by {name} for {product.name}")
        count += 1

    print(f"Successfully added {count} reviews!")

if __name__ == "__main__":
    run()
