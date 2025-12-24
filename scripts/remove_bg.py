
from PIL import Image
import os

ICON_DIR = "d:/YWL/static/icons"
ICONS = ["home.png", "love.png", "cart.png"]

def make_transparent(image_path):
    try:
        img = Image.open(image_path)
        img = img.convert("RGBA")
        datas = img.getdata()

        newData = []
        for item in datas:
            # Change all white (also shades of whites) to transparent
            # Threshold: > 240 for R, G, B
            if item[0] > 240 and item[1] > 240 and item[2] > 240:
                newData.append((255, 255, 255, 0))
            else:
                newData.append(item)

        img.putdata(newData)
        img.save(image_path, "PNG")
        print(f"Successfully processed {image_path}")
    except Exception as e:
        print(f"Error processing {image_path}: {e}")

for icon in ICONS:
    path = os.path.join(ICON_DIR, icon)
    if os.path.exists(path):
        make_transparent(path)
    else:
        print(f"File not found: {path}")
