import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yarned_with_love.settings')
django.setup()

from store.models import Order, OrderItem, OrderUpdate

# Delete all orders (Cascades to Items and Updates)
print("Deleting all orders...")
Order.objects.all().delete()
print("All orders deleted.")

# Reset Sequence (SQLite specific, common for dev)
# For Postgres (Render), this might not work via Django ORM directly without raw SQL, 
# but deleting is the main request.
with connection.cursor() as cursor:
    if 'sqlite' in connection.vendor:
        try:
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='store_order';")
            print("SQLite sequence reset.")
        except Exception as e:
            print(f"Skipping SQLite sequence reset (might not be sqlite): {e}")
    elif 'postgresql' in connection.vendor:
        try:
            cursor.execute("ALTER SEQUENCE store_order_id_seq RESTART WITH 1;")
            print("Postgres sequence reset.")
        except Exception as e:
            print(f"Skipping Postgres sequence reset: {e}")

print("Order history cleared!")
