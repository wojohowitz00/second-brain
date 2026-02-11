
import os
import sys
from PIL import Image, ImageDraw, ImageFont

def create_icon(size=1024):
    # Create image
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Draw rounded rectangle background (purple to blue gradient simulation)
    # Since prompt was "gradients of purple and blue", we'll do a simple fill
    # Pillow doesn't do gradients easily, so just a solid purple-blue color
    bg_color = (100, 50, 200, 255) # Deep purple
    
    # Draw circle/rounded rect
    margin = size // 10
    draw.ellipse([margin, margin, size-margin, size-margin], fill=bg_color)
    
    # Draw "SB" text
    try:
        # Try to load a font, otherwise default
        # macOS system font
        font_path = "/System/Library/Fonts/Helvetica.ttc"
        font = ImageFont.truetype(font_path, size=int(size/2.5))
    except Exception:
        font = ImageFont.load_default()

    text = "SB"
    
    # Calculate text position (centering)
    # bbox = draw.textbbox((0, 0), text, font=font)
    # text_w = bbox[2] - bbox[0]
    # text_h = bbox[3] - bbox[1]
    # x = (size - text_w) / 2
    # y = (size - text_h) / 2
    
    # Simple centering for default font or if bbox fails (older Pillow)
    # Draw text in white
    draw.text((size/2, size/2), text, font=font, fill=(255, 255, 255, 255), anchor="mm")

    return img

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_icon.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    img = create_icon()
    img.save(output_path)
    print(f"Icon saved to {output_path}")
