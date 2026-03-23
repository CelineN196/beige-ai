"""
Simulate app startup to verify V2 model is loaded with correct version
"""

import sys
sys.path.insert(0, '/Users/queenceline/Downloads/Beige AI')
sys.path.insert(0, '/Users/queenceline/Downloads/Beige AI/backend')

# Import the exact functions the app uses
from ml_compatibility_wrapper import SafeMLLoader, RuleBasedPredictor

print("\n" + "="*70)
print("🔥 APP STARTUP SIMULATION - V2 FORCING TEST")
print("="*70 + "\n")

print("Step 1: Creating SafeMLLoader (like app does)...")
loader = SafeMLLoader()
print("✅ SafeMLLoader created\n")

print("Step 2: Loading model (like app does)...")
model, preprocessor, label_encoder, version = loader.load()
print(f"✅ Model loaded, version={version}\n")

print("Step 3: Getting status (like app does)...")
status = loader.get_status_dict()
print("✅ Status retrieved\n")

print("="*70)
print("APP STARTUP RESULTS")
print("="*70 + "\n")

print(f"📊 Load Status: {status.get('load_status')}")
print(f"📊 Model Version: {status.get('model_version')}")
print(f"📊 Model Loaded: {model is not None}")
print(f"📊 Load Error: {status.get('load_error') or 'None'}\n")

# Verify V2 is being used
version = status.get('model_version', 'UNKNOWN')
if version.startswith('V2'):
    print(f"✅ SUCCESS: App will show V2 model")
    print(f"   Version: {version}")
    print(f"   Status: {status.get('load_status')}")
elif version == 'V1_FALLBACK':
    print(f"❌ ERROR: App showing V1_FALLBACK instead of V2")
    print(f"   This means V2-forcing did not work properly")
else:
    print(f"⚠️  Using {version} mode")

print("\n" + "="*70)
