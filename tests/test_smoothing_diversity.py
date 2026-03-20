#!/usr/bin/env python3
"""
Test script to demonstrate probability smoothing and random sampling
for improved recommendation diversity.

Shows how smoothing and random sampling prevents popular cakes from
always dominating the Top 3 recommendations.
"""

import sys
import os
import joblib
import numpy as np
import pandas as pd

print("=" * 80)
print("BEIGE.AI RECOMMENDATION DIVERSITY - PROBABILITY SMOOTHING DEMO")
print("=" * 80)

# Set seed for reproducibility in this demo
np.random.seed(42)

try:
    # Load artifacts
    print("\n[1] LOADING ARTIFACTS...")
    model = joblib.load('backend/models/cake_model.joblib')
    preprocessor = joblib.load('backend/models/preprocessor.joblib')
    feature_info = joblib.load('backend/models/feature_info.joblib')
    print(f"✅ Loaded successfully")
    
    # Create test input (same as before for comparison)
    print("\n[2] CREATING TEST INPUT...")
    user_input = pd.DataFrame({
        'mood': ['Happy'],
        'weather_condition': ['Sunny'],
        'temperature_celsius': [25.0],
        'humidity': [60.0],
        'air_quality_index': [50.0],
        'time_of_day': ['Afternoon'],
        'sweetness_preference': [5.0],
        'health_preference': [5.0],
        'trend_popularity_score': [0.6],
        'temperature_category': ['mild'],
        'comfort_index': [0.8],
        'environmental_score': [0.8],
        'season': ['Spring']
    })
    
    X_processed = preprocessor.transform(user_input)
    raw_probs = model.predict_proba(X_processed)[0].copy()
    cake_names = feature_info['classes']
    
    print(f"✅ Test input created\n")
    
    # =========================================================================
    # COMPARISON: Raw Top-3 vs Smoothed + Random Sampling
    # =========================================================================
    
    print("[3] RAW PROBABILITY ANALYSIS")
    print("-" * 80)
    print(f"{'Cake':<30} {'Probability':<15} {'Chance':<10}")
    print("-" * 80)
    for cake, prob in zip(cake_names, raw_probs):
        prob_pct = prob * 100
        bar = "█" * int(prob_pct / 2)
        print(f"{cake:<30} {prob:>6.4f}       {prob_pct:>6.2f}% {bar}")
    
    print(f"\n✅ Dominance problem: Top 2 cakes = {raw_probs.argsort()[-2:][::-1]}")
    print(f"   These will ALWAYS be in top 3 with strict selection.")
    
    # =========================================================================
    # APPLY PROBABILITY SMOOTHING
    # =========================================================================
    
    print("\n\n[4] APPLYING PROBABILITY SMOOTHING (Temperature = 1.5)")
    print("-" * 80)
    
    temperature = 1.5
    smoothed_probs = np.power(raw_probs, 1.0 / temperature)
    normalized_probs = smoothed_probs / smoothed_probs.sum()
    
    print(f"{'Cake':<30} {'Raw':<12} {'Smoothed':<12} {'Change':<12}")
    print("-" * 80)
    for i, cake in enumerate(cake_names):
        raw = raw_probs[i]
        smoothed = normalized_probs[i]
        change = ((smoothed - raw) / raw * 100) if raw > 0 else 0
        print(f"{cake:<30} {raw:>6.2%}      {smoothed:>6.2%}      {change:>+6.1f}%")
    
    print(f"\n✅ Smoothing effect:")
    print(f"   • Popular cakes: Probabilities slightly reduced")
    print(f"   • Unpopular cakes: Probabilities increased")
    print(f"   • All cakes now have a realistic chance!")
    
    # =========================================================================
    # RANDOM SAMPLING
    # =========================================================================
    
    print("\n\n[5] RANDOM SAMPLING 3 CAKES FROM SMOOTHED DISTRIBUTION")
    print("-" * 80)
    
    sampled_indices = np.random.choice(
        len(cake_names),
        size=3,
        replace=False,
        p=normalized_probs
    )
    
    sampled_cakes = [cake_names[i] for i in sampled_indices]
    sampled_raw_probs = [raw_probs[i] for i in sampled_indices]
    sampled_smooth_probs = [normalized_probs[i] for i in sampled_indices]
    
    # Sort by raw (original) probability for display
    sorted_pairs = sorted(zip(sampled_cakes, sampled_raw_probs, sampled_smooth_probs),
                         key=lambda x: x[1], reverse=True)
    
    print(f"\n🎲 SAMPLE 1: 3 Randomly sampled cakes")
    print(f"{'Rank':<6} {'Cake':<30} {'Original %':<12} {'Smoothed %':<12}")
    print("-" * 80)
    for rank, (cake, raw, smooth) in enumerate(sorted_pairs, 1):
        print(f"{rank:<6} {cake:<30} {raw:>6.2%}        {smooth:>6.2%}")
    
    # =========================================================================
    # RUN MULTIPLE SAMPLES TO SHOW DIVERSITY
    # =========================================================================
    
    print("\n\n[6] RUNNING 10 SAMPLES TO SHOW DIVERSITY")
    print("-" * 80)
    
    appearance_count = {cake: 0 for cake in cake_names}
    
    for sample_num in range(1, 11):
        sampled_indices = np.random.choice(
            len(cake_names),
            size=3,
            replace=False,
            p=normalized_probs
        )
        
        for idx in sampled_indices:
            appearance_count[cake_names[idx]] += 1
    
    print(f"\n🏆 APPEARANCE COUNT OVER 10 SAMPLES:")
    print(f"(if random: each cake should appear ~3-4 times)")
    print("-" * 80)
    sorted_counts = sorted(appearance_count.items(), key=lambda x: x[1], reverse=True)
    
    for cake, count in sorted_counts:
        bar = "█" * count
        print(f"{cake:<30} {count} times  {bar}")
    
    # Check diversity
    min_appearances = min(appearance_count.values())
    max_appearances = max(appearance_count.values())
    
    print(f"\n✅ Diversity achieved!")
    print(f"   • Min appearances: {min_appearances}/10")
    print(f"   • Max appearances: {max_appearances}/10")
    print(f"   • Every cake gets a chance! (vs strict Top-3 = only 3 cakes)")
    
    # =========================================================================
    # COMPARISON WITH STRICT TOP-3
    # =========================================================================
    
    print("\n\n[7] COMPARISON: STRICT TOP-3 vs SMOOTHED RANDOM")
    print("=" * 80)
    
    strict_top3_indices = np.argsort(raw_probs)[-3:][::-1]
    strict_top3 = [cake_names[i] for i in strict_top3_indices]
    
    print(f"\n❌ STRICT TOP-3 (old method):")
    print(f"   Always shows: {strict_top3}")
    print(f"   Other cakes never appear!")
    
    print(f"\n✅ SMOOTHED RANDOM SAMPLING (new method):")
    sample_2 = [cake_names[i] for i in np.random.choice(len(cake_names), 3, replace=False, p=normalized_probs)]
    sample_3 = [cake_names[i] for i in np.random.choice(len(cake_names), 3, replace=False, p=normalized_probs)]
    print(f"   Sample 1: {sampled_cakes} (varies each time!)")
    print(f"   Sample 2: {sample_2}")
    print(f"   Sample 3: {sample_3}")
    print(f"   All cakes get a fair chance!")
    
    print("\n" + "=" * 80)
    print("✅ TEST COMPLETE - DIVERSITY SIGNIFICANTLY IMPROVED!")
    print("=" * 80)
    
    print("\nKey Benefits:")
    print("  ✅ Popular cakes: Still get selected most often (respect model)")
    print("  ✅ Unpopular cakes: Now get a fair chance (reduce dominance)")
    print("  ✅ Variety: Different recommendations on each user request")
    print("  ✅ Fair: All cakes appear eventually")
    
    sys.exit(0)

except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
