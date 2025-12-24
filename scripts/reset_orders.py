import os
import sys
import django
from django.db import connection
from pathlib import Path

# Setup Django
sys.path.append(str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yarned_with_love.settings")
django.setup()

from store.models import Order

def reset_orders():
    print("Deleting all orders...")
    count, _ = Order.objects.all().delete()
    print(f"Deleted {count} orders.")

    # Reset ID sequence (SQLite specific, but common in dev)
    print("Attempting to reset Order ID sequence...")
    try:
        with connection.cursor() as cursor:
            # Check if using SQLite
            if connection.vendor == 'sqlite':
                cursor.execute("DELETE FROM sqlite_sequence WHERE name='store_order'")
                print("Order ID sequence reset to 1.")
            else:
                print("Database is not SQLite. Skipping sequence reset (IDs will continue incrementing).")
                print("To reset IDs in PostgreSQL: TRUNCATE TABLE store_order RESTART IDENTITY CASCADE;")
    except Exception as e:
        print(f"Error resetting sequence: {e}")

if __name__ == "__main__":
    reset_orders()
