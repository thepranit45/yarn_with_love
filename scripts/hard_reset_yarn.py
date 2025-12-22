import os
import django
import sys

sys.path.append('D:/YWL')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yarned_with_love.settings')
django.setup()

from users.models import CustomUser

def run():
    username = 'yarn'
    password = 'admin'
    email = 'yarn@example.com'
    
    # DELETE existing to ensure clean slate
    try:
        old_user = CustomUser.objects.get(username=username)
        old_user.delete()
        print(f"Deleted existing user '{username}'")
    except CustomUser.DoesNotExist:
        print(f"User '{username}' did not exist previously.")
        
    # CREATE fresh superuser
    try:
        user = CustomUser.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        print(f"Created NEW superuser '{username}' with password '{password}'")
        
        # Verify
        u = CustomUser.objects.get(username=username)
        print(f"VERIFICATION: Is credentials check valid? {u.check_password(password)}")
        print(f"VERIFICATION: Is active? {u.is_active}")
        print(f"VERIFICATION: Is staff? {u.is_staff}")
        print(f"VERIFICATION: Is superuser? {u.is_superuser}")
        
    except Exception as e:
        print(f"Error creating user: {e}")

if __name__ == "__main__":
    run()
