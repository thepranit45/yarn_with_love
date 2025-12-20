
import random
from django.utils import timezone
from users.models import CustomUser
from store.models import Category, Product, Order, OrderItem, OrderUpdate

def reset_demo_data(artisan_user):
    """
    Resets orders for the demo artisan to ensure a fresh 'New Orders' queue.
    """
    # 1. Find the Demo Customer
    customer, _ = CustomUser.objects.get_or_create(username='customer_demo')

    # 2. Delete existing orders for this artisan's products (simplification: delete orders from demo customer)
    # real specific: delete orders where items belong to artisan_user
    # To be safe and clean, let's just delete all orders by 'customer_demo'
    Order.objects.filter(customer=customer).delete()
    
    # 3. Ensure Products Exist
    # (Assuming products are already there from previous script, but safe to get/create)
    products = Product.objects.filter(artisan=artisan_user)
    if not products.exists():
        # Fallback creation if products were deleted
        cat, _ = Category.objects.get_or_create(name='Demo Category', defaults={'slug': 'demo'})
        Product.objects.create(name='Demo Scarf', artisan=artisan_user, price=50, category=cat, description='Demo item')
        products = Product.objects.filter(artisan=artisan_user)
    
    prod_list = list(products)

    # 4. Create 3 Fresh 'Queue' Orders (PENDING)
    for i in range(1, 4):
        order = Order.objects.create(
            customer=customer,
            status='PENDING',
            full_name=f"Fresh Customer {i}",
            shipping_address=f"New Street {i}",
            city="Demo City",
            customization_notes=f"Fresh order note {i}"
        )
        # Add random product
        OrderItem.objects.create(
            order=order,
            product=random.choice(prod_list),
            quantity=random.randint(1, 2),
            price_at_purchase=50
        )

    # 5. Create 1 Active Order (IN_PROGRESS) for variety
    active_order = Order.objects.create(
        customer=customer,
        status='IN_PROGRESS',
        full_name="Active Customer",
        city="Work City"
    )
    OrderItem.objects.create(order=active_order, product=random.choice(prod_list), quantity=1, price_at_purchase=50)

    print("Demo data reset complete.")
