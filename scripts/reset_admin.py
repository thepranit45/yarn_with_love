import os
import django
import sys

sys.path.append('D:/YWL')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yarned_with_love.settings')
django.setup()

from users.models import CustomUser

def run():
    username = 'admin'
    password = 'admin'
    email = 'admin@example.com'
    
    try:
        user, created = CustomUser.objects.get_or_create(username=username, defaults={'email': email})
        user.set_password(password)
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.save()
        
        if created:
            print(f"Created superuser '{username}' with password '{password}'")
        else:
            print(f"Updated password for superuser '{username}' to '{password}'")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run()
