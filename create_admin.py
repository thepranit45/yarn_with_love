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

    # Create 'yarn' superuser
    username_yarn = 'yarn'
    password_yarn = 'yarnwlove'
    email_yarn = 'yarn@example.com'

    try:
        if User.objects.filter(username=username_yarn).exists():
            print(f"User '{username_yarn}' already exists. Updating password...")
            user = User.objects.get(username=username_yarn)
            user.set_password(password_yarn)
            user.is_superuser = True
            user.is_staff = True
            user.save()
            print(f"SUCCESS: Password for '{username_yarn}' reset to '{password_yarn}'")
        else:
            print(f"Creating new superuser '{username_yarn}'...")
            User.objects.create_superuser(username=username_yarn, email=email_yarn, password=password_yarn)
            print(f"SUCCESS: Superuser '{username_yarn}' created with password '{password_yarn}'")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_admin()
