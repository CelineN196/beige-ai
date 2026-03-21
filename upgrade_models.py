#!/usr/bin/env python3
"""Upgrade models to scikit-learn 1.5.1 for Python 3.14 compatibility."""

import sys
import sklearn
import joblib
from pathlib import Path

print(f"Current scikit-learn version: {sklearn.__version__}")

models_dir = Path("models")

try:
    print("\nLoading models...")
    cake_model = joblib.load(models_dir / "cake_model.joblib")
    preprocessor = joblib.load(models_dir / "preprocessor.joblib")
    feature_info = joblib.load(models_dir / "feature_info.joblib")
    
    print("✓ All models loaded successfully!")
    
    # Re-save with new version
    print("\nRe-serializing models with sklearn 1.5.1...")
    joblib.dump(cake_model, models_dir / "cake_model.joblib", compress=3)
    joblib.dump(preprocessor, models_dir / "preprocessor.joblib", compress=3)
    joblib.dump(feature_info, models_dir / "feature_info.joblib", compress=3)
    print("✓ Models re-serialized successfully!")
    
    # Verify re-saved models
    print("\nVerifying re-saved models...")
    test_model = joblib.load(models_dir / "cake_model.joblib")
    print(f"✓ Verification passed: {type(test_model)}")
    print("\n✓ All done! Models are now compatible with scikit-learn 1.5.1 and Python 3.14")
    
except Exception as e:
    print(f"✗ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
