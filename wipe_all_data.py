
import os
import django
import shutil

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yarned_with_love.settings')
django.setup()

from store.models import Product, Category, OrderItem, Order

def aggressive_wipe():
    print("Starting AGGRESSIVE wipe...")
    
    # 1. Delete all OrderItems (This frees up the Products)
    deleted_items, _ = OrderItem.objects.all().delete()
    print(f"Deleted {deleted_items} OrderItems.")

    # 2. Delete all Products
    # Also clean up media files just in case
    for product in Product.objects.all():
        if product.image and os.path.exists(product.image.path):
            try:
                os.remove(product.image.path)
            except:
                pass
    
    deleted_products, _ = Product.objects.all().delete()
    print(f"Deleted {deleted_products} Products.")

    # 3. Delete all Categories
    deleted_cats, _ = Category.objects.all().delete()
    print(f"Deleted {deleted_cats} Categories.")
    
    # 4. Optional: Delete Orders if they are now empty and useless?
    # User asked to delete "collections" (products), didn't explicitly say orders, 
    # but empty orders are weird. I'll leave them for now to be safe, or just mention it.
    
    print("Wipe complete.")

if __name__ == '__main__':
    aggressive_wipe()
