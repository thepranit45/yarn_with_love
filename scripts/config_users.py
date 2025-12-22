import os
import django
import sys

sys.path.append('D:/YWL')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yarned_with_love.settings')
django.setup()

from users.models import CustomUser

def run():
    # 1. Configure 'pranit' (Superuser)
    username = 'pranit'
    password = 'thepranit'
    email = 'pranit@example.com'
    
    try:
        user, created = CustomUser.objects.get_or_create(username=username, defaults={'email': email})
        user.set_password(password)
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.is_artisan = True # Assuming he wants to be an artisan too, or just admin
        user.save()
        
        if created:
            print(f"Created superuser '{username}' with password '{password}'")
        else:
            print(f"Updated password for superuser '{username}' to '{password}'")
            
    except Exception as e:
        print(f"Error configuring '{username}': {e}")

    # 2. Configure 'mansi' (Default Artist)
    # We essentially want to make sure she exists. The user said "passwords manage by artist pranit"
    # which might mean Pranit will log in to admin to manage her, OR that we should set a known password for her too.
    # I'll set a default one just in case, or leave it if it exists. 
    # To be safe, let's set it to 'mansi123' so she can login if needed, or 'thepranit' if that's what was meant.
    # Interpreting "all passwords manage by ... pranit" -> Pranit is the admin.
    
    mansi_username = 'mansi'
    try:
        mansi, created = CustomUser.objects.get_or_create(username=mansi_username)
        mansi.is_artisan = True
        mansi.first_name = "Mansi"
        # Ensure she has a bio/image from previous steps (they should persist unless we deleted DB)
        # If we need to re-link image:
        if not mansi.profile_image:
             mansi.profile_image.name = 'artistmansi.png'
        
        mansi.save()
        print(f"Ensured user '{mansi_username}' is an artisan.")
        
    except Exception as e:
        print(f"Error configuring '{mansi_username}': {e}")

if __name__ == "__main__":
    run()
