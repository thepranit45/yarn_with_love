import os
import sys
import django

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yarned_with_love.settings')
django.setup()

from store.models import Coupon

def create_coupon():
    code = "SANTA5"
    discount = 5
    
    try:
        coupon, created = Coupon.objects.get_or_create(
            code=code,
            defaults={'discount_percentage': discount, 'active': True}
        )
        
        if created:
            print(f"✅ Success: Coupon '{code}' created with {discount}% discount.")
        else:
            coupon.discount_percentage = discount
            coupon.active = True
            coupon.save()
            print(f"ℹ️ Info: Coupon '{code}' updated to {discount}% discount.")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    create_coupon()
