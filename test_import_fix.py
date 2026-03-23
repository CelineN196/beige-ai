"""
Test retrain_v2_final import fix
Forces the retrain code path to verify import works correctly
"""

import sys
sys.path.insert(0, '/Users/queenceline/Downloads/Beige AI')
sys.path.insert(0, '/Users/queenceline/Downloads/Beige AI/backend')

import os
import shutil
from pathlib import Path
from ml_compatibility_wrapper import SafeMLLoader

print("\n" + "="*70)
print("🔧 IMPORT FIX TEST - FORCE RETRAIN CODE PATH")
print("="*70 + "\n")

# Setup: Backup and corrupt the model to trigger retrain
model_dir = Path('/Users/queenceline/Downloads/Beige AI/models')
v2_path = model_dir / 'v2_final_model.pkl'
backup_path = model_dir / 'v2_final_model.pkl.import_test_backup'

print("Step 1: Backing up working model...")
shutil.copy2(str(v2_path), str(backup_path))
print(f"✅ Backup created at {backup_path}\n")

print("Step 2: Corrupting model to trigger retrain...")
with open(str(v2_path), 'w') as f:
    f.write("CORRUPTED DATA TO FORCE RETRAIN")
print(f"✅ Model corrupted (size: {os.path.getsize(str(v2_path))} bytes)\n")

print("Step 3: Loading model (should trigger retrain)...")
print("="*70)

loader = SafeMLLoader()
model, preprocessor, encoder, version = loader.load()

print("\n" + "="*70)
print("RESULTS")
print("="*70 + "\n")

if version == "V2_RETRAINED":
    print(f"✅ SUCCESS: Retrain triggered successfully")
    print(f"   Version: {version}")
    print(f"   Status: {loader.load_status}")
    print(f"   Model loaded: {model is not None}")
    print(f"\n✅ IMPORT FIX VERIFIED: train_model() imported and executed successfully")
elif version == "V2_PRODUCTION":
    print(f"ℹ️  Model loaded from disk (no retrain needed)")
    print(f"   Version: {version}")
else:
    print(f"❌ ERROR: Unexpected version {version}")
    print(f"   Load error: {loader.load_error}")

print("\nStep 4: Cleaning up...")
# Restore original model
shutil.copy2(str(backup_path), str(v2_path))
os.remove(str(backup_path))
print("✅ Original model restored\n")

print("="*70)
