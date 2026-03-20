"""
Generate placeholder cake images for the Beige.AI menu.
This creates simple colored placeholder images for each cake type.
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import os

def create_cake_placeholder(filename, cake_name, color_rgb, assets_dir):
    """Create a placeholder image for a cake."""
    width, height = 500, 400
    
    # Create image with base color
    img = Image.new('RGB', (width, height), color_rgb)
    draw = ImageDraw.Draw(img)
    
    # Add a subtle pattern
    for i in range(0, width, 40):
        for j in range(0, height, 40):
            if (i + j) % 80 == 0:
                overlay = Image.new('RGBA', (40, 40), (255, 255, 255, 10))
                img.paste(overlay, (i, j), overlay)
    
    # Add cake name text
    try:
        # Try to use a nice font, fallback to default if not available
        font_size = 32
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
    except:
        font = ImageFont.load_default()
    
    # Draw text with white color and center it
    text = cake_name
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    text_x = (width - text_width) // 2
    text_y = (height - text_height) // 2
    
    # Draw text with shadow for better visibility
    draw.text((text_x + 2, text_y + 2), text, font=font, fill=(100, 100, 100))
    draw.text((text_x, text_y), text, font=font, fill=(255, 255, 255))
    
    # Save image
    output_path = assets_dir / filename
    img.save(output_path, 'PNG')
    print(f"✓ Created: {output_path}")
    return output_path

def main():
    """Generate all cake placeholder images."""
    
    # Define assets directory
    assets_dir = Path(__file__).parent / "assets" / "images" / "cakes"
    assets_dir.mkdir(parents=True, exist_ok=True)
    
    # Define cakes with their representative colors (RGB tuples)
    # Colors chosen to represent each cake type
    cakes = {
        "dark_chocolate_sea_salt.png": ("Dark Chocolate Sea Salt Cake", (101, 67, 33)),     # Brown
        "matcha_zen.png": ("Matcha Zen Cake", (108, 155, 90)),                               # Green
        "citrus_cloud.png": ("Citrus Cloud Cake", (255, 192, 89)),                           # Yellow/Orange
        "berry_garden.png": ("Berry Garden Cake", (198, 124, 165)),                          # Berry pink
        "silk_cheesecake.png": ("Silk Cheesecake", (238, 211, 169)),                         # Cream
        "earthy_wellness.png": ("Earthy Wellness Cake", (139, 125, 107)),                    # Earthy brown
        "cafe_tiramisu.png": ("Café Tiramisu", (147, 109, 75)),                              # Cocoa brown
        "korean_sesame_mini_bread.png": ("Korean Sesame Mini Bread", (222, 184, 135)),      # Tan
    }
    
    print("=" * 70)
    print("GENERATING CAKE PLACEHOLDER IMAGES")
    print("=" * 70)
    print(f"Output directory: {assets_dir}\n")
    
    for filename, (cake_name, color) in cakes.items():
        create_cake_placeholder(filename, cake_name, color, assets_dir)
    
    print("\n" + "=" * 70)
    print(f"✅ Successfully created {len(cakes)} cake images!")
    print("=" * 70)
    
    # Verify all files exist
    created_files = list(assets_dir.glob("*.png"))
    print(f"\nVerification: {len(created_files)}/{len(cakes)} images exist")
    
    return assets_dir

if __name__ == "__main__":
    main()
