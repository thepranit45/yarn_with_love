
import os

FILE_PATH = "d:/YWL/templates/store/product_list.html"

def fix_file():
    try:
        with open(FILE_PATH, 'r', encoding='utf-8') as f:
            content = f.read()

        # Define the specific broken strings and their replacements
        # We need to be careful with whitespace, so we might replace based on substrings
        
        # 1. Fix story-ring div
        old_div = '<div class="story-ring"\n            style="{% if not request.GET.category'
        new_div = '<div class="story-ring" style="{% if not request.GET.category'
        
        # 2. Fix story-label span
        old_span = '<span class="story-label"\n            style="{% if not request.GET.category'
        new_span = '<span class="story-label" style="{% if not request.GET.category'

        if old_div not in content and old_span not in content:
            print("Target strings not found directly. Checking variations...")
            # Try matching with different newline/space variations if strict match fails
            # But based on agent view_file, it looks like \n + 12 spaces
            pass

        new_content = content.replace(old_div, new_div)
        new_content = new_content.replace(old_span, new_span)
        
        if content == new_content:
            print("No changes made. Content might not match exactly.")
        else:
            with open(FILE_PATH, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print("Successfully updated product_list.html")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_file()
