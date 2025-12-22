import os
import django
import sys

sys.path.append('D:/YWL')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yarned_with_love.settings')
django.setup()

from users.models import CustomUser

def run():
    try:
        user = CustomUser.objects.get(username='mansi')
        
        # Update Name
        user.first_name = "Mansi"
        # user.last_name = "" # Optional
        
        # Update Bio if empty
        if not user.bio:
            user.bio = "The creative soul behind Yarned with Love. Mansi brings warmth and artistry to every handmade piece, ensuring that each knot and stitch tells a story of care and dedication."
            print("Updated bio.")
            
        # Update Image (Simulating the path as if uploaded)
        # We know 'artistmansi.png' is in media/
        if not user.profile_image:
            user.profile_image.name = 'artistmansi.png'
            print("Linked profile image.")
            
        user.is_artisan = True
        user.save()
        print(f"Successfully updated profile for {user.username}")
        
    except CustomUser.DoesNotExist:
        print("User 'mansi' not found!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run()
