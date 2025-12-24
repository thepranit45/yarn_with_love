import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yarned_with_love.settings')
django.setup()

from store.models import Category, Product

# Target to KEEP
keep_cat = Category.objects.filter(name='Key Chain').first()
# Target to REMOVE
remove_cat = Category.objects.filter(name='Keychains').first()

if keep_cat and remove_cat:
    # Move products
    products_to_move = Product.objects.filter(category=remove_cat)
    count = products_to_move.count()
    print(f"Moving {count} products from '{remove_cat.name}' to '{keep_cat.name}'...")
    
    for p in products_to_move:
        p.category = keep_cat
        p.save()
        print(f"Moved product: {p.name}")
    
    # Delete duplicate category
    remove_cat.delete()
    print(f"Deleted category '{remove_cat.name}'.")
    
    print(f"Final count for '{keep_cat.name}': {Product.objects.filter(category=keep_cat).count()}")

else:
    print("One or both categories not found. Aborting.")
