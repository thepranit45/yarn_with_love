import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yarned_with_love.settings')
django.setup()

from django.conf import settings
from store.models import Product

changed = 0
for p in Product.objects.all():
    has_file = bool(p.image and os.path.exists(os.path.join(str(settings.MEDIA_ROOT), p.image.name)))
    if not has_file and p.is_active:
        p.is_active = False
        p.save(update_fields=['is_active'])
        changed += 1
        print(f"Deactivated (missing image): {p.name}")

print(f"\nDone. Deactivated {changed} products with missing images.")
