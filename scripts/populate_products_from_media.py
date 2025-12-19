import os
import sys
import re
from decimal import Decimal

import django


# Ensure project is on path and Django is configured
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yarned_with_love.settings")
django.setup()

from django.conf import settings  # noqa: E402
from store.models import Product, Category  # noqa: E402
from users.models import CustomUser  # noqa: E402


PRODUCTS_DIR = os.path.join(settings.MEDIA_ROOT, "products")


def title_from_filename(name: str) -> str:
    base = os.path.splitext(name)[0]
    # Replace separators with spaces
    base = re.sub(r"[_\-]+", " ", base)
    # Remove common noise tokens
    tokens = [t for t in base.split() if t.lower() not in {"img", "image", "photo", "pic"}]
    # Remove trailing/standalone numeric tokens that look like versions or prices
    cleaned = []
    for t in tokens:
        if re.fullmatch(r"\d+(?:[._-]\d+)?", t):
            # likely a number/price/version token; skip from title
            continue
        cleaned.append(t)
    title = " ".join(cleaned) if cleaned else base
    return title.strip().title()


def price_from_filename(name: str, default: Decimal = Decimal("19.99")) -> Decimal:
    base = os.path.splitext(name)[0]
    # Find first price-like pattern: 12, 12-99, 12_99, 12.99
    m = re.search(r"(\d+)(?:[._-](\d{2}))?", base)
    if not m:
        return default
    whole = m.group(1)
    cents = m.group(2) or "00"
    try:
        return Decimal(f"{int(whole)}.{int(cents):02d}")
    except Exception:
        return default


def get_or_create_default_artisan() -> CustomUser:
    artisan, _ = CustomUser.objects.get_or_create(
        username="default_artisan",
        defaults={
            "email": "artisan@yarnedwithlove.com",
            "is_artisan": True,
            "bio": "Default artisan for imported products",
        },
    )
    return artisan


def get_default_category() -> Category:
    cat, _ = Category.objects.get_or_create(slug="handmade", defaults={"name": "Handmade"})
    return cat


def import_from_media():
    if not os.path.isdir(PRODUCTS_DIR):
        print(f"✗ Folder not found: {PRODUCTS_DIR}")
        return

    artisan = get_or_create_default_artisan()
    category = get_default_category()

    files = [f for f in os.listdir(PRODUCTS_DIR) if os.path.isfile(os.path.join(PRODUCTS_DIR, f))]
    if not files:
        print("No images found in media/products.")
        return

    created, updated, skipped = 0, 0, 0

    for filename in sorted(files):
        rel_path = os.path.join("products", filename).replace("\\", "/")
        # Derive fields
        name = title_from_filename(filename)
        price = price_from_filename(filename)

        # If a product already exists for this exact image, update its basic fields
        prod = Product.objects.filter(image=rel_path).first()
        if prod:
            changed = False
            if not prod.name:
                prod.name = name
                changed = True
            if prod.price != price and price is not None:
                prod.price = price
                changed = True
            if prod.category_id is None:
                prod.category = category
                changed = True
            if not prod.is_active:
                prod.is_active = True
                changed = True
            if changed:
                prod.save(update_fields=["name", "price", "category", "is_active", "updated_at"] if hasattr(prod, "updated_at") else ["name", "price", "category", "is_active"])
                updated += 1
                print(f"↻ Updated: {prod.name} ({rel_path})")
            else:
                skipped += 1
                print(f"• Skipped (no changes): {prod.name} ({rel_path})")
            continue

        # Otherwise, try to find by name and attach image if empty
        prod = Product.objects.filter(name=name, artisan=artisan).first()
        if prod and not prod.image:
            prod.image.name = rel_path
            if prod.category_id is None:
                prod.category = category
            if not prod.price:
                prod.price = price
            if not prod.is_active:
                prod.is_active = True
            prod.save()
            updated += 1
            print(f"↻ Attached image to existing: {prod.name} -> {rel_path}")
            continue

        # Create a new product
        prod = Product(
            artisan=artisan,
            category=category,
            name=name or os.path.splitext(filename)[0],
            description=f"Handmade item imported from {filename}",
            price=price,
            estimated_days_to_complete=3,
            is_active=True,
        )
        # Set image path directly; file already stored in MEDIA_ROOT
        prod.image.name = rel_path
        prod.save()
        created += 1
        print(f"✓ Created: {prod.name} ({rel_path}) - ${prod.price}")

    print("\nSummary:")
    print(f"  Created: {created}")
    print(f"  Updated: {updated}")
    print(f"  Skipped: {skipped}")


if __name__ == "__main__":
    import_from_media()
