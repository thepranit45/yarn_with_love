import os
import django
import sys

# Add project root to path
sys.path.append('D:/YWL')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yarned_with_love.settings')
django.setup()

from users.models import CustomUser
from store.models import Category, Product, Order, OrderItem, OrderUpdate

def run():
    print("Creating test data...")

    # Create users
    artisan, created = CustomUser.objects.get_or_create(username='artisan_anna', email='anna@yarned.com', is_artisan=True)
    if created:
        artisan.set_password('password123')
        artisan.bio = "I love making sunflowers!"
        artisan.save()
        print(f"Created Artisan: {artisan.username}")

    customer, created = CustomUser.objects.get_or_create(username='customer_cathy', email='cathy@example.com')
    if created:
        customer.set_password('password123')
        customer.save()
        print(f"Created Customer: {customer.username}")
    
    # Create category
    category, _ = Category.objects.get_or_create(name='Flowers', slug='flowers')
    print(f"Created Category: {category.name}")

    # Create product
    product, created = Product.objects.get_or_create(
        name='Crochet Sunflower',
        artisan=artisan,
        category=category,
        defaults={
            'description': 'A bright and sunny handcrafted sunflower.',
            'price': 25.00,
            'estimated_days_to_complete': 5
        }
    )
    print(f"Created Product: {product.name}")

    # Create Order
    order, created = Order.objects.get_or_create(
        customer=customer,
        status='PENDING',
        defaults={
            'customization_notes': 'Extra leaves please!'
        }
    )
    if created:
        OrderItem.objects.create(order=order, product=product, price_at_purchase=product.price)
        print(f"Created Order: {order}")

    # Update Order Status
    order.status = 'IN_PROGRESS'
    order.save()
    print(f"Updated Order Status to: {order.status}")

    # Create Order Update
    update = OrderUpdate.objects.create(
        order=order,
        description="Started working on the petals today! Looking yellow and bright.",
    )
    print(f"Created Order Update: {update}")

    print("Test data population complete!")

if __name__ == '__main__':
    run()
