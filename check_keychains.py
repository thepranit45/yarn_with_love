import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yarned_with_love.settings')
django.setup()

from store.models import Category, Product

cat1 = Category.objects.filter(name='Key Chain').first()
cat2 = Category.objects.filter(name='Keychains').first()

if cat1:
    count1 = Product.objects.filter(category=cat1).count()
    print(f"Category 'Key Chain' (slug: {cat1.slug}) has {count1} products.")
else:
    print("Category 'Key Chain' not found.")

if cat2:
    count2 = Product.objects.filter(category=cat2).count()
    print(f"Category 'Keychains' (slug: {cat2.slug}) has {count2} products.")
else:
    print("Category 'Keychains' not found.")
