import os
import django
import sys

sys.path.append('D:/YWL')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yarned_with_love.settings')
django.setup()

from users.models import CustomUser

def run():
    username = 'artisan_demo'
    password = 'demopassword' # Setting a default, though access is usually via code or admin
    email = 'demo@example.com'
    
    try:
        user, created = CustomUser.objects.get_or_create(username=username, defaults={'email': email})
        if created:
            user.set_password(password)
            user.is_artisan = True
            user.first_name = "Demo"
            user.last_name = "Artisan"
            user.save()
            print(f"Created user '{username}'.")
        else:
            if not user.is_artisan:
                user.is_artisan = True
                user.save()
            print(f"User '{username}' already exists. Ensured is_artisan=True.")
            
    except Exception as e:
        print(f"Error configuring '{username}': {e}")

if __name__ == "__main__":
    run()
