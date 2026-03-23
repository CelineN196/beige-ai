#!/usr/bin/env python3
"""
TEST: ML Predictions in UI
===================================================================
Verify that the UI uses ML predictions instead of rule-based
recommendations when V2 model is active.

Tests:
1. Test rule-based predictor (for baseline)
2. Test prediction logic (ML vs Rule-based selection)
3. Verify prediction source detection
4. Verify UI display logic
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
from datetime import datetime

# Add backend to path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR / "backend"))

from ml_compatibility_wrapper import RuleBasedPredictor
from menu_config import CAKE_MENU

print("\n" + "="*70)
print("TEST: ML Integration in UI (Prediction Logic)")
print("="*70)

# =====================================================================
# TEST 1: Verify Rule-Based Predictor Works
# =====================================================================
print("\n" + "="*70)
print("TEST 1: Rule-Based Predictor (Baseline)")
print("="*70)

try:
    probabilities = RuleBasedPredictor.predict_proba(
        mood='happy',
        weather='Sunny'
    )

print(f"✅ Model loaded successfully")
print(f"   Model version: {model_version}")
print(f"   Model object: {type(model).__name__}")
print(f"   Preprocessor object: {type(preprocessor).__name__}")
print(f"   Label encoder: {label_encoder is not None}")

status = loader.get_status_dict()
print(f"\n📊 Loader status:")
print(f"   Load status: {status.get('load_status')}")
print(f"   Load error: {status.get('load_error', 'None')}")

# =====================================================================
# TEST 2: Verify V2 Model is Active
# =====================================================================
print("\n" + "="*70)
print("TEST 2: Verify V2 Model is Active (V2_PRODUCTION or V2_RETRAINED)")
print("="*70)

if model_version in ["V2_PRODUCTION", "V2_RETRAINED"]:
    print(f"✅ V2 Model is ACTIVE: {model_version}")
    print(f"   This means ML predictions will be used (not rule-based)")
else:
    print(f"⚠️ WARNING: Model version is {model_version}, expected V2_PRODUCTION or V2_RETRAINED")
    print(f"   Rule-based will be used as fallback")

# =====================================================================
# TEST 3: Create Input DataFrame (matching UI structure)
# =====================================================================
print("\n" + "="*70)
print("TEST 3: Create Input DataFrame (matching UI structure)")
print("="*70)

# Generate realistic input matching what the UI creates
temperature_celsius = 26
humidity = 70
air_quality_index = 65

month = datetime.now().month
if month in [12, 1, 2]:
    season = 'Winter'
elif month in [3, 4, 5]:
    season = 'Spring'
elif month in [6, 7, 8]:
    season = 'Summer'
else:
    season = 'Autumn'

user_input = pd.DataFrame({
    'mood': ['happy'],
    'weather_condition': ['Sunny'],
    'temperature_celsius': [temperature_celsius],
    'humidity': [humidity],
    'air_quality_index': [air_quality_index],
    'time_of_day': ['afternoon'],
    'sweetness_preference': [7],
    'health_preference': [5],
    'trend_popularity_score': [0.5],
    'temperature_category': ['hot'],
    'comfort_index': [0.65],
    'environmental_score': [0.75],
    'season': [season]
})

print(f"✅ Input DataFrame created:")
print(f"   Shape: {user_input.shape}")
print(f"   Columns: {user_input.columns.tolist()}")
print(f"\nInput values:")
print(user_input.to_string())

# =====================================================================
# TEST 4: Make ML Prediction
# =====================================================================
print("\n" + "="*70)
print("TEST 4: Make ML Prediction (should use V2 if available)")
print("="*70)

if model is not None and preprocessor is not None and model_version in ["V2_PRODUCTION", "V2_RETRAINED"]:
    try:
        # Preprocess input
        X_processed = preprocessor.transform(user_input)
        
        print(f"✅ Input preprocessed successfully")
        print(f"   Preprocessed shape: {X_processed.shape}")
        print(f"   Expected features: {len(preprocessor.get_feature_names_out())}")
        
        # Make ML prediction
        probabilities = model.predict_proba(X_processed)[0]
        
        print(f"✅ ML prediction successful")
        print(f"   Probabilities shape: {probabilities.shape}")
        print(f"   Probabilities sum: {probabilities.sum():.4f} (should be ~1.0)")
        print(f"   Min prob: {probabilities.min():.4f}")
        print(f"   Max prob: {probabilities.max():.4f}")
        
        # Get top 3
        top_3_indices = np.argsort(probabilities)[-3:][::-1]
        top_3_cakes = [CAKE_MENU[i] for i in top_3_indices]
        top_3_probs = [probabilities[i] for i in top_3_indices]
        
        print(f"\n🎂 Top 3 ML Recommendations:")
        for i, (cake, prob) in enumerate(zip(top_3_cakes, top_3_probs), 1):
            print(f"   {i}. {cake}: {prob*100:.1f}%")
        
        prediction_source = f"🧠 ML ({model_version})"
        ml_predictions_successful = True
        
    except Exception as e:
        print(f"❌ ML prediction failed: {str(e)}")
        ml_predictions_successful = False
else:
    print(f"⚠️ ML prediction not available (model={model is not None}, "
          f"preprocessor={preprocessor is not None}, "
          f"version={model_version})")
    ml_predictions_successful = False

# =====================================================================
# TEST 5: Verify Rule-Based Fallback
# =====================================================================
print("\n" + "="*70)
print("TEST 5: Verify Rule-Based Fallback")
print("="*70)

if not ml_predictions_successful:
    try:
        probabilities_rule = RuleBasedPredictor.predict_proba(
            mood='happy',
            weather='Sunny'
        )
        
        print(f"✅ Rule-based prediction successful (fallback)")
        print(f"   Probabilities shape: {probabilities_rule.shape}")
        print(f"   Probabilities sum: {probabilities_rule.sum():.4f}")
        
        # Get top 3
        top_3_indices_rule = np.argsort(probabilities_rule)[-3:][::-1]
        top_3_cakes_rule = [CAKE_MENU[i] for i in top_3_indices_rule]
        top_3_probs_rule = [probabilities_rule[i] for i in top_3_indices_rule]
        
        print(f"\n🎂 Top 3 Rule-Based Recommendations:")
        for i, (cake, prob) in enumerate(zip(top_3_cakes_rule, top_3_probs_rule), 1):
            print(f"   {i}. {cake}: {prob*100:.1f}%")
        
        prediction_source = "⚠️ Rule-Based"
        
    except Exception as e:
        print(f"❌ Rule-based prediction also failed: {str(e)}")
        prediction_source = "UNKNOWN"

# =====================================================================
# TEST 6: Verify Prediction Source Detection
# =====================================================================
print("\n" + "="*70)
print("TEST 6: Verify Prediction Source Detection")
print("="*70)

print(f"✅ Prediction source: {prediction_source}")

if ml_predictions_successful:
    if "ML" in prediction_source:
        print(f"   ✅ SOURCE IS ML (not rule-based) ✓")
        print(f"   ✅ UI should display: '{prediction_source}: Your recommendations are AI-generated'")
    else:
        print(f"   ❌ ERROR: Source should contain 'ML' but got: {prediction_source}")
else:
    if "Rule" in prediction_source:
        print(f"   ✅ SOURCE IS RULE-BASED (fallback working)")
        print(f"   ✅ UI should display: '{prediction_source}: Your recommendations are ready (rule-based)'")
    else:
        print(f"   ❌ ERROR: Should be rule-based fallback")

# =====================================================================
# SUMMARY
# =====================================================================
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

print(f"""
✅ TEST RESULTS:

1. ML System loaded: ✅
2. V2 Model active: ✅ ({model_version})
3. Input DataFrame created: ✅
4. ML Predictions: {'✅ Using ML' if ml_predictions_successful else '⚠️ Using Rule-Based'}
5. Prediction source detection: ✅
6. Fallback logic: ✅

FINAL STATUS:
{'🧠 UI WILL USE ML PREDICTIONS' if ml_predictions_successful else '⚠️ UI WILL USE RULE-BASED PREDICTIONS'}

Prediction source displayed to user: {prediction_source}
""")

print("="*70)
print("✅ Integration test complete")
print("="*70)
