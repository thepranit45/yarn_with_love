
import os
import django
import sys
import random
from datetime import timedelta
from django.utils import timezone

# Add project root to path
# Assuming the script is run from the project root or scripts directory.
# Adjusting based on standard management command structure or standalone script
sys.path.append('D:/YWL')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yarned_with_love.settings')
django.setup()

from users.models import CustomUser
from store.models import Category, Product, Order, OrderItem, OrderUpdate

def run():
    print("Starting data population...")

    # 1. Create Default Artisan
    artisan_username = 'artisan_demo'
    artisan_email = 'demo@yarnedwithlove.com'
    artisan_password = 'password123'
    
    artisan, created = CustomUser.objects.get_or_create(
        username=artisan_username, 
        defaults={
            'email': artisan_email, 
            'is_artisan': True,
            'bio': 'Passionate creator of handmade woolens and accessories. I love bringing warmth to your life!'
        }
    )
    if not created:
        print(f"Artisan {artisan.username} already exists.")
    else:
        artisan.set_password(artisan_password)
        artisan.save()
        print(f"Created Artisan: {artisan.username}")

    # 2. Create Default Customer
    customer_username = 'customer_demo'
    customer_email = 'customer@example.com'
    customer_password = 'password123'

    customer, created = CustomUser.objects.get_or_create(
        username=customer_username,
        defaults={'email': customer_email}
    )
    if not created:
        print(f"Customer {customer.username} already exists.")
    else:
        customer.set_password(customer_password)
        customer.save()
        print(f"Created Customer: {customer.username}")

    # 3. Create Sample Products
    # Ensure categories exist
    cat_names = ['Woolens', 'Accessories', 'Home Decor']
    categories = []
    for name in cat_names:
        cat, _ = Category.objects.get_or_create(name=name, defaults={'slug': name.lower().replace(' ', '-')})
        categories.append(cat)

    product_data = [
        {'name': 'Cozy Scarf', 'price': 35.00, 'cat_idx': 1, 'desc': 'Soft and warm scarf for winter.'},
        {'name': 'Handmade Sweater', 'price': 85.00, 'cat_idx': 0, 'desc': 'Custom fit sweater made with love.'},
        {'name': 'Crochet Coasters', 'price': 15.00, 'cat_idx': 2, 'desc': 'Set of 4 colorful coasters.'},
        {'name': 'Baby Booties', 'price': 25.00, 'cat_idx': 1, 'desc': 'Adorable warm booties for infants.'},
    ]

    products = []
    for p_data in product_data:
        product, created = Product.objects.get_or_create(
            name=p_data['name'],
            artisan=artisan,
            defaults={
                'category': categories[p_data['cat_idx']],
                'description': p_data['desc'],
                'price': p_data['price'],
                'estimated_days_to_complete': random.randint(3, 14)
            }
        )
        products.append(product)
        if created:
            print(f"Created Product: {product.name}")

    # 4. Create Dummy Orders (Active & Past)
    # We want 3-4 active orders and some history.
    order_scenarios = [
        {'status': 'PENDING', 'notes': 'Can you add a gift note?', 'items': [0]},
        {'status': 'IN_PROGRESS', 'notes': 'Prefer blue color if possible.', 'items': [1], 'update': 'Choosing the yarn colors today!'},
        {'status': 'FINISHING', 'notes': '', 'items': [2, 3], 'update': 'Almost done, just weaving in the ends.'},
        {'status': 'READY', 'notes': 'Please ship ASAP.', 'items': [0], 'update': 'Packed and ready to go!'},
        # Past orders
        {'status': 'COMPLETED', 'notes': 'Thank you!', 'items': [2], 'update': 'Delivered!', 'months_ago': 1},
        {'status': 'COMPLETED', 'notes': 'Lovely item.', 'items': [1], 'update': 'Delivered!', 'months_ago': 2},
    ]

    for i, scenario in enumerate(order_scenarios):
        # Check if we should create this order (simple check to avoid infinite dupes on re-run, though random tracking ID makes distinct orders)
        # We'll just create them. In a real scenario we'd check existence, but for demo data "more is better" usually unless strict.
        
        created_time = timezone.now()
        if 'months_ago' in scenario:
             created_time = timezone.now() - timedelta(days=30 * scenario['months_ago'])

        order = Order.objects.create(
            customer=customer,
            status=scenario['status'],
            customization_notes=scenario['notes'],
            full_name=f"Customer {i+1}",
            shipping_address=f"123 Street {i+1}",
            city="Metropolis",
            state="NY",
            zip_code="10001",
            created_at=created_time # Note: automatic auto_now_add override might need special handling, but often works if set at creation or updated after.
        )
        # Force update date for past orders
        if 'months_ago' in scenario:
            Order.objects.filter(pk=order.pk).update(created_at=created_time)

        # Add items
        for item_idx in scenario['items']:
            prod = products[item_idx]
            OrderItem.objects.create(
                order=order,
                product=prod,
                quantity=1,
                price_at_purchase=prod.price
            )
        
        # Add update if exists
        if 'update' in scenario:
            OrderUpdate.objects.create(
                order=order,
                description=scenario['update']
            )

        print(f"Created Order #{order.id} with status {order.status}")

    print("Data population completed successfully!")

if __name__ == '__main__':
    run()
