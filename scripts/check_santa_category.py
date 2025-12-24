import os
import sys
import django
from pathlib import Path

# Setup Django
sys.path.append(str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yarned_with_love.settings")
django.setup()

from store.models import Product, Category

def check_santa():
    try:
        santa = Product.objects.filter(name="Santa Claus Keychain").first()
        if santa:
            print(f"Product: {santa.name}")
            print(f"Category: {santa.category.name if santa.category else 'None'}")
        else:
            print("Santa Product NOT FOUND.")

        print("\n--- Products in Keychains Category ---")
        keychains = Category.objects.filter(name='Keychains').first()
        if keychains:
            products = Product.objects.filter(category=keychains)
            for p in products:
                print(f"- {p.name}")
        else:
            print("Keychains Category NOT FOUND.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_santa()
