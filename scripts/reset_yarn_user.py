import os
import django
import sys

sys.path.append('D:/YWL')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yarned_with_love.settings')
django.setup()

from users.models import CustomUser

def run():
    username = 'yarn'  # The user trying to login
    password = 'admin'
    
    try:
        user = CustomUser.objects.get(username=username)
        user.set_password(password)
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.save()
        
        print(f"Updated '{username}' to be superuser with password '{password}'")
            
    except CustomUser.DoesNotExist:
        print(f"User '{username}' not found. Please use 'admin' / 'admin'")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run()
