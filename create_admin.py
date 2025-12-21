import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yarned_with_love.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def create_admin():
    username = 'thepranit'
    email = 'pranit@example.com'
    password = 'ythepranit'

    try:
        if User.objects.filter(username=username).exists():
            print(f"User '{username}' already exists. Updating password...")
            user = User.objects.get(username=username)
            user.set_password(password)
            user.is_superuser = True
            user.is_staff = True
            user.save()
            print(f"SUCCESS: Password for '{username}' reset to '{password}'")
        else:
            print(f"Creating new superuser '{username}'...")
            User.objects.create_superuser(username=username, email=email, password=password)
            print(f"SUCCESS: Superuser '{username}' created with password '{password}'")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_admin()
