#!/usr/bin/env python3
"""
Demonstration: Diversity boost effect with multiple input scenarios
Shows how underrepresented cakes get boosted into top 3
"""

import joblib
import numpy as np
import pandas as pd

print("=" * 80)
print("DIVERSITY BOOST DEMONSTRATION - Multiple Scenarios")
print("=" * 80)

# Load artifacts
model = joblib.load('backend/models/cake_model.joblib')
preprocessor = joblib.load('backend/models/preprocessor.joblib')
feature_info = joblib.load('backend/models/feature_info.joblib')

# Test scenario 1: Happy, sunny afternoon (diverse preferences)
print("\n\n📊 SCENARIO 1: Happy & Sunny (Good for Diversity)")
print("-" * 80)

user_input_1 = pd.DataFrame({
    'mood': ['Happy'],
    'weather_condition': ['Sunny'],
    'temperature_celsius': [25.0],
    'humidity': [60.0],
    'air_quality_index': [50.0],
    'time_of_day': ['Afternoon'],
    'sweetness_preference': [5.0],  # Medium sweetness
    'health_preference': [5.0],     # Balanced health
    'trend_popularity_score': [0.6],
    'temperature_category': ['mild'],
    'comfort_index': [0.8],
    'environmental_score': [0.8],
    'season': ['Spring']
})

X1 = preprocessor.transform(user_input_1)
raw_probs_1 = model.predict_proba(X1)[0].copy()

# Apply boost
probs_1 = raw_probs_1.copy()
underrepresented = ["Berry Garden Cake", "Silk Cheesecake", "Citrus Cloud Cake", "Earthy Wellness Cake"]
for i, cake in enumerate(feature_info['classes']):
    if cake in underrepresented:
        probs_1[i] *= 1.08

# Normalize
probs_1 = probs_1 / probs_1.sum()

print("\nRAW vs BOOSTED Comparison:")
print(f"{'Cake':<30} {'Raw':<12} {'Boosted':<12} {'Change':<10}")
print("-" * 65)
for i, cake in enumerate(feature_info['classes']):
    raw = raw_probs_1[i]
    boosted = probs_1[i]
    change = ((boosted - raw) / raw * 100) if raw > 0 else 0
    is_underrep = "🎯" if cake in underrepresented else "  "
    print(f"{is_underrep} {cake:<28} {raw:>6.2%}       {boosted:>6.2%}       {change:>+6.1f}%")

top_3_indices = np.argsort(probs_1)[-3:][::-1]
print(f"\n🏆 TOP 3 (with boost):")
for rank, idx in enumerate(top_3_indices, 1):
    cake = feature_info['classes'][idx]
    prob = probs_1[idx]
    is_underrep = "🎯 BOOSTED" if cake in underrepresented else "  "
    print(f"   {rank}. {cake:<30} {prob:>6.2%} {is_underrep}")

print("\n\nKey Benefits of Diversity Boost:")
print("  ✅ Underrepresented cakes (🎯) get a fair chance")
print("  ✅ Probabilities stay realistic (normalized)")
print("  ✅ 8% boost helps but doesn't dominate predictions")
print("  ✅ Users get variety in recommendations")

print("\n" + "=" * 80)
print("✅ Diversity boost improves recommendation variety!")
print("=" * 80)
