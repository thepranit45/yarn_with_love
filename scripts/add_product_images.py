import os
import sys
import django
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from django.core.files.base import ContentFile

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yarned_with_love.settings')
django.setup()

from store.models import Product

# Define product colors and descriptions
product_images = {
    1: {  # Pink Amigurumi Ball
        'colors': [(230, 190, 200), (200, 150, 180)],  # Pink gradients
        'text': 'Pink Ball',
        'emoji': '🎀'
    },
    2: {  # Bunny Ice Cream
        'colors': [(240, 240, 240), (210, 180, 140)],  # White and tan
        'text': 'Bunny Ice Cream',
        'emoji': '🐰'
    },
    3: {  # Sunflower
        'colors': [(255, 255, 0), (139, 69, 19)],  # Yellow and brown
        'text': 'Sunflower',
        'emoji': '🌻'
    }
}

def create_placeholder_image(width=300, height=300, colors=None, text='Product', emoji='🧶'):
    """Create a simple placeholder image"""
    if colors is None:
        colors = [(240, 220, 230), (200, 180, 200)]
    
    # Create image with gradient-like effect
    img = Image.new('RGB', (width, height), colors[0])
    
    # Add a simple pattern
    draw = ImageDraw.Draw(img)
    
    # Draw some rectangles for visual interest
    for i in range(0, width, 50):
        draw.rectangle([i, 0, i+25, height], fill=colors[1])
    
    # Add text and emoji
    try:
        # Try to use a larger font
        font_size = 40
        font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
    
    # Draw emoji
    text_bbox = draw.textbbox((0, 0), emoji, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    x = (width - text_width) // 2
    y = (height - text_height) // 2 - 30
    draw.text((x, y), emoji, fill=(50, 50, 50), font=font)
    
    # Draw product name
    draw.text((width//2 - 50, height - 50), text[:15], fill=(80, 80, 80), font=font)
    
    return img

# Add images to products
products = [
    (1, 'Pink Crocheted Amigurumi Ball'),
    (2, 'Crocheted Bunny Ice Cream Cone'),
    (3, 'Yellow Crocheted Sunflower in Pot'),
]

for product_id, product_name in products:
    try:
        product = Product.objects.get(pk=product_id)
        
        if not product.image:  # Only add if image doesn't exist
            img_data = product_images.get(product_id, product_images[1])
            
            # Create image
            img = create_placeholder_image(
                colors=img_data['colors'],
                text=img_data['text'],
                emoji=img_data['emoji']
            )
            
            # Save to BytesIO
            img_io = BytesIO()
            img.save(img_io, format='PNG')
            img_io.seek(0)
            
            # Save to product
            product.image.save(f'product_{product_id}.png', ContentFile(img_io.read()), save=True)
            print(f"✓ Image added to: {product.name}")
        else:
            print(f"✓ {product.name} already has an image")
            
    except Product.DoesNotExist:
        print(f"✗ Product with ID {product_id} not found")
    except Exception as e:
        print(f"✗ Error adding image to product {product_id}: {str(e)}")

print("\nDone! Images have been added to products.")
