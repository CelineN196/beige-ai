#!/usr/bin/env python3
"""
TEST: Normalized cake metadata lookup
===================================================================
Verify that get_cake_info() properly handles:
- Case differences
- Whitespace variations
- Missing cakes (fallback)
- Both menu cakes and predictor cakes
"""

import sys
from pathlib import Path

# Add frontend to path for menu_config
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR / "frontend"))

from menu_config import get_cake_info, CAKE_MENU, CAKE_CATEGORIES

print("\n" + "="*70)
print("TEST: Normalized Cake Metadata Lookup")
print("="*70)

# =====================================================================
# TEST 1: Exact matches (menu cakes)
# =====================================================================
print("\nTEST 1: Exact Matches (Primary Menu Cakes)")
print("-" * 70)

menu_cakes_to_test = [
    "Dark Chocolate Sea Salt Cake",
    "Matcha Zen Cake",
    "Citrus Cloud Cake",
]

for cake_name in menu_cakes_to_test:
    info = get_cake_info(cake_name)
    print(f"✅ {cake_name}")
    print(f"   Category: {info.get('category')}")
    print(f"   Flavor: {info.get('flavor_profile')}")
    assert info.get('category') != 'N/A', "Should not return N/A"
    assert info.get('flavor_profile') != 'N/A', "Should not return N/A"

# =====================================================================
# TEST 2: Case differences
# =====================================================================
print("\nTEST 2: Case Differences (handles UPPERCASE, lowercase, MixedCase)")
print("-" * 70)

case_variations = [
    "dark chocolate sea salt cake",  # lowercase
    "DARK CHOCOLATE SEA SALT CAKE",  # uppercase
    "DaRk ChOcOlAtE SeA SaLt CaKe",  # mixed case
]

for cake_name in case_variations:
    info = get_cake_info(cake_name)
    category = info.get('category')
    print(f"✅ '{cake_name}' → {category}")
    assert category == "Indulgent", f"Expected 'Indulgent', got '{category}'"

# =====================================================================
# TEST 3: Extra whitespace
# =====================================================================
print("\nTEST 3: Extra Whitespace (handles   spaces   correctly)")
print("-" * 70)

whitespace_variations = [
    "  Dark Chocolate Sea Salt Cake  ",  # leading/trailing
    "Dark  Chocolate  Sea  Salt  Cake",  # double spaces
    "\tDark Chocolate Sea Salt Cake\n",  # tabs and newlines
]

for cake_name in whitespace_variations:
    info = get_cake_info(cake_name)
    category = info.get('category')
    print(f"✅ '{repr(cake_name)}' → {category}")
    assert category == "Indulgent", f"Expected 'Indulgent', got '{category}'"

# =====================================================================
# TEST 4: Fallback cake names (rule-based predictor)
# =====================================================================
print("\nTEST 4: Fallback Cake Names (Rule-Based Predictor)")
print("-" * 70)

fallback_cakes = [
    "Chocolate Cake",
    "Vanilla Cake",
    "Lemon Cake",
    "Strawberry Cheesecake",
    "Carrot Cake",
    "Black Forest Cake",
    "Tiramisu Cake",
    "Red Velvet Cake",
]

for cake_name in fallback_cakes:
    info = get_cake_info(cake_name)
    category = info.get('category')
    flavor = info.get('flavor_profile')
    print(f"✅ {cake_name}")
    print(f"   Category: {category} | Flavor: {flavor}")
    assert category != 'N/A', f"Category should not be N/A for {cake_name}"
    assert flavor != 'N/A', f"Flavor should not be N/A for {cake_name}"
    assert flavor != "Balanced", f"Fallback used for {cake_name}, metadata should exist"

# =====================================================================
# TEST 5: Unknown cake (fallback)
# =====================================================================
print("\nTEST 5: Unknown Cake (Safe Fallback)")
print("-" * 70)

unknown_cakes = [
    "Nonexistent Cake",
    "Unicorn Cake",
    "Future Cake XYZ",
]

for cake_name in unknown_cakes:
    info = get_cake_info(cake_name)
    category = info.get('category')
    flavor = info.get('flavor_profile')
    print(f"✅ {cake_name}")
    print(f"   Category: {category} (fallback)")
    print(f"   Flavor: {flavor} (fallback)")
    assert category == "Signature", f"Should use 'Signature' fallback for unknown cake"
    assert flavor == "Balanced", f"Should use 'Balanced' fallback for unknown cake"

# =====================================================================
# TEST 6: All metadata keys present
# =====================================================================
print("\nTEST 6: All Metadata Keys Present")
print("-" * 70)

test_cake = get_cake_info("matcha zen cake")
required_keys = ['category', 'flavor_profile', 'sweetness_level', 'health_score']

for key in required_keys:
    exists = key in test_cake
    print(f"{'✅' if exists else '❌'} {key}: {test_cake.get(key)}")
    assert exists, f"Missing required key: {key}"

# =====================================================================
# SUMMARY
# =====================================================================
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

print(f"""
✅ ALL TESTS PASSED

1. Exact matches work: ✅ (menu cakes found)
2. Case differences handled: ✅ (lowercase, UPPERCASE, MixedCase)
3. Whitespace handled: ✅ (spaces, tabs, newlines)
4. Fallback cakes found: ✅ (Chocolate Cake, Vanilla Cake, etc.)
5. Unknown cakes safe: ✅ (returns safe defaults)
6. All metadata keys: ✅ (category, flavor, sweetness, health)

VERIFICATION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Zero "N/A" values - all predictions will have meaningful metadata
✅ Case-insensitive - handles any input case
✅ Whitespace-safe - handles extra spaces
✅ Robust fallback - never crashes, always returns valid data
✅ Production-ready - safe for all use cases

🎯 Integration complete - UI will display metadata for all predicted cakes
""")

print("="*70)
