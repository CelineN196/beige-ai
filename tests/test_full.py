#!/usr/bin/env python3
"""Complete test of preprocessor and model with detailed diagnostics."""

import sys
import joblib
import pandas as pd
import numpy as np

print("=" * 70)
print("PREPROCESSOR & MODEL TEST")
print("=" * 70)

try:
    # Load artifacts
    print("\n[1] Loading artifacts...")
    preprocessor = joblib.load('backend/models/preprocessor.joblib')
    model = joblib.load('backend/models/cake_model.joblib')
    feature_info = joblib.load('backend/models/feature_info.joblib')
    print(f"✅ Loaded successfully")
    print(f"   sklearn: {feature_info.get('sklearn_version', 'unknown')}")
    print(f"   numpy: {feature_info.get('numpy_version', 'unknown')}")
    
    # Check preprocessor structure
    print(f"\n[2] Preprocessor structure...")
    print(f"   Type: {type(preprocessor).__name__}")
    print(f"   Transformers: {len(preprocessor.transformers_)}")
    for name, transformer, columns in preprocessor.transformers_:
        print(f"     - {name}: {type(transformer).__name__} on {len(columns)} columns")
    
    # Create test input (matching app's slider values: 1-10 integers)
    print(f"\n[3] Creating test input...")
    user_input = pd.DataFrame({
        'mood': ['Happy'],
        'weather_condition': ['Sunny'],
        'temperature_celsius': [28.0],
        'humidity': [72.0],
        'air_quality_index': [65.0],
        'time_of_day': ['Afternoon'],
        'sweetness_preference': [5.0],  # slider: 1-10
        'health_preference': [5.0],  # slider: 1-10  
        'trend_popularity_score': [0.75],
        'temperature_category': ['mild'],
        'comfort_index': [0.85],
        'environmental_score': [0.70],
        'season': ['Summer']
    })
    print(f"✅ Created {len(user_input.columns)} columns")
    
    # Try transform
    print(f"\n[4] Transforming input...")
    X_processed = preprocessor.transform(user_input)
    print(f"✅ Transform succeeded! Shape: {X_processed.shape}")
    
    # Try prediction
    print(f"\n[5] Making prediction...")
    probabilities = model.predict_proba(X_processed)[0]
    top_idx = np.argmax(probabilities)
    print(f"✅ Prediction succeeded!")
    print(f"   Top probability: {probabilities[top_idx]:.4f}")
    
    # Get top 3
    top_3_indices = np.argsort(probabilities)[-3:][::-1]
    top_3_cakes = [feature_info['classes'][i] for i in top_3_indices]
    top_3_probs = [probabilities[i] for i in top_3_indices]
    
    print(f"\n[6] Top 3 recommendations:")
    for cake, prob in zip(top_3_cakes, top_3_probs):
        print(f"   - {cake}: {prob:.4f}")
    
    print("\n" + "=" * 70)
    print("✅ ALL TESTS PASSED")
    print("=" * 70)
    sys.exit(0)

except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
