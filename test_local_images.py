"""
Verification test for local cake images in product cards.
Ensures all images are properly generated and accessible.
"""

import sys
from pathlib import Path

def test_local_images():
    """Verify all cake images exist in the local assets directory."""
    print("\n" + "=" * 70)
    print("LOCAL IMAGE VERIFICATION TEST")
    print("=" * 70)
    
    # Define assets directory
    assets_dir = Path(__file__).parent / "assets" / "images" / "cakes"
    
    expected_images = {
        "dark_chocolate_sea_salt.png": "Dark Chocolate Sea Salt Cake",
        "matcha_zen.png": "Matcha Zen Cake",
        "citrus_cloud.png": "Citrus Cloud Cake",
        "berry_garden.png": "Berry Garden Cake",
        "silk_cheesecake.png": "Silk Cheesecake",
        "earthy_wellness.png": "Earthy Wellness Cake",
        "cafe_tiramisu.png": "Café Tiramisu",
        "korean_sesame_mini_bread.png": "Korean Sesame Mini Bread"
    }
    
    print(f"\nAssets directory: {assets_dir}")
    print(f"Expected images: {len(expected_images)}\n")
    
    # Check each image file
    missing_images = []
    found_images = []
    
    for filename, cake_name in expected_images.items():
        image_path = assets_dir / filename
        if image_path.exists():
            file_size = image_path.stat().st_size
            print(f"✅ {filename:.<40} {file_size:>8} bytes - {cake_name}")
            found_images.append(filename)
        else:
            print(f"❌ {filename:.<40} MISSING - {cake_name}")
            missing_images.append(filename)
    
    # Summary
    print("\n" + "=" * 70)
    print("IMAGE VERIFICATION SUMMARY")
    print("=" * 70)
    
    print(f"\nFound: {len(found_images)}/{len(expected_images)} images")
    print(f"Missing: {len(missing_images)}/{len(expected_images)} images")
    
    if missing_images:
        print(f"\n⚠️  Missing images:")
        for img in missing_images:
            print(f"   - {img}")
        return False
    
    # Test image accessibility
    print("\n" + "-" * 70)
    print("IMAGE ACCESSIBILITY TEST")
    print("-" * 70)
    
    try:
        from PIL import Image
        print("\nVerifying image files can be opened with PIL:")
        
        for filename in found_images:
            image_path = assets_dir / filename
            try:
                img = Image.open(image_path)
                print(f"✅ {filename:.<40} {img.size[0]}x{img.size[1]} - {img.format}")
            except Exception as e:
                print(f"❌ {filename:.<40} ERROR: {str(e)}")
                return False
        
    except ImportError:
        print("⚠️  PIL not available, skipping detailed image validation")
    
    # Test Streamlit image path resolution
    print("\n" + "-" * 70)
    print("STREAMLIT PATH RESOLUTION TEST")
    print("-" * 70)
    
    app_path = Path(__file__).parent / "frontend" / "beige_ai_app.py"
    print(f"\nApp file: {app_path}")
    
    # Simulate path resolution from app perspective
    if app_path.exists():
        app_dir = app_path.parent
        resolved_assets = app_dir.parent / "assets" / "images" / "cakes"
        print(f"Resolved assets: {resolved_assets}")
        
        if resolved_assets.exists():
            resolved_images = list(resolved_assets.glob("*.png"))
            print(f"Images found: {len(resolved_images)}")
            print("✅ Path resolution working correctly")
        else:
            print("❌ Resolved assets path not found")
            return False
    
    print("\n" + "=" * 70)
    print("✅ ALL LOCAL IMAGE TESTS PASSED!")
    print("=" * 70)
    return True

if __name__ == "__main__":
    success = test_local_images()
    sys.exit(0 if success else 1)
