import os
import django
import sys

sys.path.append('D:/YWL')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yarned_with_love.settings')
django.setup()

from users.models import CustomUser
from store.models import Product

def run():
    print("Linking images for Mansi's products...")
    
    try:
        mansi = CustomUser.objects.get(username='mansi')
    except CustomUser.DoesNotExist:
        print("Error: User 'mansi' not found!")
        return

    # Product Name -> Image Path (relative to MEDIA_ROOT)
    image_map = {
        # Hair Ties
        'Daisy Hair Tie': 'products/hairtie/daisyhairtie.jpeg',
        'Bow Hair Tie': 'products/hairtie/bowtie.jpeg',
        'Sunflower Hair Tie': 'products/hairtie/sunflower hair tie.jpeg',
        'Love Hair Tie': 'products/hairtie/lovehairtie.jpeg',
        'Rose Hair Tie': 'products/hairtie/rose hair tie .jpeg',

        # Flower Pots
        'Pink Gerbera Flower Pot': 'products/flowerpot/pink gerbera flower pot.jpeg',
        'Sunflower Flower Pot': 'products/flowerpot/sunflower flower pot.jpeg',

        # Key Chains
        'Evil Eye Key Chain': 'products/keychain/evil eye keychain.jpeg',
        'Ear Pod Case (Big Size)': 'products/keychain/ear pod keychain.jpeg',
    }

    count = 0
    for prod_name, img_path in image_map.items():
        try:
            product = Product.objects.get(name=prod_name, artisan=mansi)
            # Assign the relative path to the ImageField
            product.image.name = img_path
            product.save()
            print(f"Updated image for: {prod_name}")
            count += 1
        except Product.DoesNotExist:
            print(f"WARNING: Product '{prod_name}' not found!")
        except Exception as e:
            print(f"Error updating '{prod_name}': {e}")

    print(f"Update complete. {count}/{len(image_map)} products updated.")

if __name__ == "__main__":
    run()
