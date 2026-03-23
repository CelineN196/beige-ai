#!/usr/bin/env python3
"""Test if model.pkl loads and works correctly."""

import joblib
import pandas as pd

print("=" * 70)
print("MODEL LOAD TEST")
print("=" * 70)

print("\n📦 Loading model.pkl...")
try:
    container = joblib.load('models/model.pkl')
    print("✅ Model loaded successfully\n")
except Exception as e:
    print(f"❌ Loading failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Verify components
model = container.get('model')
preprocessor = container.get('preprocessor')
label_encoder = container.get('label_encoder')

print("📊 Components:")
print(f"  - Model: {type(model).__name__} ✅")
print(f"  - Preprocessor: {type(preprocessor).__name__} ✅")
print(f"  - LabelEncoder: {type(label_encoder).__name__} ✅")

# Test prediction pipeline
print("\n🔧 Testing preprocessing...")
features = container['categorical_features'] + container['numerical_features']
test_data = pd.DataFrame([[
    'happy', 'sunny', 'morning', 'spring', 'warm',
    25, 60, 50, 7, 8, 85, 4.5, 4.2
]], columns=features)

X_processed = preprocessor.transform(test_data)
print(f"  Input shape: {test_data.shape}")
print(f"  Processed shape: {X_processed.shape} ✅")

print("\n🎯 Testing prediction...")
pred = model.predict(X_processed)
proba = model.predict_proba(X_processed)
cake_name = label_encoder.inverse_transform(pred)[0]

print(f"  Predicted cake: {cake_name}")
print(f"  Probabilities shape: {proba.shape}")
print(f"  Probabilities sum: {proba[0].sum():.4f} ✅")

print("\n" + "=" * 70)
print("✅ MODEL FULLY FUNCTIONAL - Ready for deployment")
print("=" * 70)
