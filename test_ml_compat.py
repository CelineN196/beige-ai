#!/usr/bin/env python
"""Test ML model compatibility with current environment."""

import sys
import numpy as np
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "backend"))

from ml_compatibility_wrapper import get_safe_ml_loader

print("=" * 60)
print("ML COMPATIBILITY TEST")
print("=" * 60)

# Load model
loader = get_safe_ml_loader()
model, preprocessor, encoder, version = loader.load()
status = loader.get_status_dict()

print(f"\nModel Version: {version}")
print(f"Load Status: {status['load_status']}")
print(f"Model Loaded: {status['model_loaded']}")
print(f"Preprocessor Loaded: {status['preprocessor_loaded']}")

# Test prediction
try:
    test_input = pd.DataFrame({
        'mood': ['Happy'],
        'weather_condition': ['Sunny'],
        'temperature_celsius': [28],
        'humidity': [72],
        'air_quality_index': [65],
        'time_of_day': ['Afternoon'],
        'sweetness_preference': [0.7],
        'health_preference': [0.5],
        'trend_popularity_score': [0.8],
        'temperature_category': ['mild'],
        'comfort_index': [0.85],
        'environmental_score': [0.75],
        'season': ['Spring']
    })
    
    X_processed = preprocessor.transform(test_input)
    proba = model.predict_proba(X_processed)[0]
    
    print(f"\nPrediction Test: ✅ SUCCESS")
    print(f"  Preprocessed shape: {X_processed.shape}")
    print(f"  Probability array: {len(proba)} classes")
    print(f"  Sum of probabilities: {proba.sum():.4f}")
    
except Exception as e:
    print(f"\nPrediction Test: ❌ FAILED")
    print(f"  Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
