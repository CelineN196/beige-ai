"""
Test V2-FORCING model loading behavior
Ensures system always tries V2 first and retrain if necessary
"""

import sys
sys.path.insert(0, '/Users/queenceline/Downloads/Beige AI')

from backend.ml_compatibility_wrapper import SafeMLLoader

print("\n" + "="*70)
print("🔥 V2 FORCING TEST - CHECKING MODEL LOADING BEHAVIOR")
print("="*70 + "\n")

# Load model with new V2-forcing logic
loader = SafeMLLoader()
model, preprocessor, encoder, version = loader.load()

print("\n" + "="*70)
print("RESULTS")
print("="*70)

print(f"\n✓ Model version: {version}")
print(f"✓ Load status: {loader.load_status}")
print(f"✓ Model loaded: {model is not None}")

# Check that it's V2, not V1
if version.startswith("V2"):
    print(f"\n✅ SUCCESS: Using V2 model (version={version})")
    print(f"   This means either:")
    print(f"   - V2_PRODUCTION: Model loaded from disk")
    print(f"   - V2_RETRAINED: Model retrained automatically")
elif version == "V1_FALLBACK":
    print(f"\n❌ ERROR: Using V1_FALLBACK instead of V2")
    print(f"   The new V2-forcing logic did not work")
    print(f"   Load error: {loader.load_error}")
else:
    print(f"\n⚠️  Using {version} fallback")

print("\n" + "="*70)
