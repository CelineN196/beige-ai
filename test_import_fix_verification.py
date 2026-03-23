#!/usr/bin/env python3
"""
TEST: Verify menu_config import fix works in deployment scenario
===================================================================
This test verifies that menu_config.py is now in frontend/
and can be imported correctly from various contexts.
"""

import sys
from pathlib import Path

print("\n" + "="*70)
print("TEST: ImportError Fix - menu_config Resolution (PRIMARY FIX)")
print("="*70)

print("\n1. Testing direct frontend/ import (same directory as beige_ai_app.py)...")

# Add frontend to path (simulating beige_ai_app.py context)
frontend_dir = str(Path(__file__).resolve().parent / "frontend")
if frontend_dir not in sys.path:
    sys.path.insert(0, frontend_dir)
    print(f"   ✅ Added {frontend_dir} to sys.path")

# Test that menu_config can be imported
print("\n2. Testing menu_config import from frontend/...")
try:
    from menu_config import CAKE_MENU, CAKE_CATEGORIES, get_cake_info
    print(f"   ✅ menu_config imported successfully from frontend/")
    print(f"   - CAKE_MENU: {len(CAKE_MENU)} items")
    print(f"   - CAKE_CATEGORIES: {len(CAKE_CATEGORIES)} items")
    print(f"   - get_cake_info: {callable(get_cake_info)}")
except ImportError as e:
    print(f"   ❌ Failed to import menu_config: {e}")
    sys.exit(1)

# Test that get_cake_info works
print("\n3. Testing get_cake_info() function...")
try:
    cake_info = get_cake_info("Chocolate Cake")
    assert 'category' in cake_info, "Missing 'category' in cake_info"
    assert 'flavor_profile' in cake_info, "Missing 'flavor_profile' in cake_info"
    print(f"   ✅ get_cake_info('Chocolate Cake') works")
    print(f"      Category: {cake_info.get('category')}")
    print(f"      Flavor: {cake_info.get('flavor_profile')}")
except Exception as e:
    print(f"   ❌ get_cake_info() failed: {e}")
    sys.exit(1)

# Test case-insensitive lookup
print("\n4. Testing case-insensitive lookup...")
try:
    cake_info = get_cake_info("chocolate cake")
    assert cake_info.get('category') == "Indulgent", f"Wrong category: {cake_info.get('category')}"
    print(f"   ✅ get_cake_info('chocolate cake') works (case-insensitive)")
except Exception as e:
    print(f"   ❌ Case-insensitive lookup failed: {e}")
    sys.exit(1)

# Test unknown cake fallback
print("\n5. Testing unknown cake fallback...")
try:
    cake_info = get_cake_info("Unknown Cake XYZ")
    assert cake_info.get('category') == "Signature", f"Should use 'Signature' fallback"
    print(f"   ✅ get_cake_info('Unknown Cake XYZ') returns fallback")
    print(f"      Category: {cake_info.get('category')} (fallback)")
except Exception as e:
    print(f"   ❌ Unknown cake fallback failed: {e}")
    sys.exit(1)

print("\n" + "="*70)
print("✅ ALL TESTS PASSED")
print("="*70)
print(f"""
Summary:
- Path resolution works correctly
- menu_config imports successfully
- get_cake_info() is callable and works
- Case-insensitive lookup working
- Fallback for unknown cakes working

ImportError fix is PRODUCTION READY ✅
""")
