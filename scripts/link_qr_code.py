import os
import django
import sys
from pathlib import Path

# Setup Django
sys.path.append(str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yarned_with_love.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def link_qr():
    try:
        user = User.objects.get(username='mansi')
        # Path relative to MEDIA_ROOT
        qr_path = 'Payment qr photo/mansiqr.png'
        
        user.payment_qr_code = qr_path
        user.save()
        print(f"Successfully linked QR code '{qr_path}' to user '{user.username}'.")
        
        # Verify
        if user.payment_qr_code:
            print(f"Verification: URL is {user.payment_qr_code.url}")
        
    except User.DoesNotExist:
        print("User 'mansi' not found.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    link_qr()
