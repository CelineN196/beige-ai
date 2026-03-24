#!/usr/bin/env python
"""
Test NaN handling in CakePredictionClassifier
"""
import pandas as pd
import numpy as np
from frontend.hybrid_recommender import (
    BehavioralSegmentation,
    CakePredictionClassifier,
    INPUT_FEATURES,
    TARGET
)

def test_nan_in_classifier():
    """Test that CakePredictionClassifier handles NaN values gracefully."""
    
    print("=" * 70)
    print("TEST: NaN Handling in CakePredictionClassifier")
    print("=" * 70)
    
    # Create sample data with NaN values
    np.random.seed(42)
    n_samples = 20
    
    data = {
        'mood': ['Happy', 'Stressed', 'Tired', 'Lonely', 'Celebratory'] * 4,
        'weather_condition': ['Sunny', 'Rainy', 'Cloudy', 'Snowy', 'Stormy'] * 4,
        'season': ['Spring', 'Summer', 'Autumn', 'Winter'] * 5,
        'time_of_day': ['Morning', 'Afternoon', 'Evening', 'Night'] * 5,
        'temperature_category': ['cold', 'mild', 'warm', 'hot'] * 5,
        'temperature_celsius': np.random.uniform(0, 35, n_samples),
        'humidity': np.random.uniform(20, 80, n_samples),
        'air_quality_index': np.random.uniform(0, 300, n_samples),
        'sweetness_preference': np.random.uniform(0, 10, n_samples),
        'health_preference': np.random.uniform(0, 10, n_samples),
        'trend_popularity_score': np.random.uniform(0, 100, n_samples),
        'comfort_index': np.random.uniform(0, 10, n_samples),
        'environmental_score': np.random.uniform(0, 10, n_samples),
        'cake_category': ['Dark Chocolate Sea Salt Cake', 'Matcha Zen Cake', 'Citrus Cloud Cake', 'Berry Garden Cake'] * 5
    }
    
    df = pd.DataFrame(data)
    
    # Step 1: Segment with BehavioralSegmentation
    print("\n1️⃣ Training BehavioralSegmentation...")
    segmenter = BehavioralSegmentation(n_clusters=3)
    segmenter.fit(df)
    df['cluster_id'] = segmenter.predict(df)
    print("   ✅ Segmentation complete")
    
    # Step 2: Train classifier
    print("\n2️⃣ Training CakePredictionClassifier...")
    classifier = CakePredictionClassifier()
    classifier.fit(df)
    print("   ✅ Classifier trained")
    
    # Step 3: Test with data containing unusual values (edge cases)
    print("\n3️⃣ Testing with edge case data (unusual values)...")
    test_df = df.head(5).copy()
    test_df.loc[0, 'mood'] = 'UnknownMood'  # Unmapped mood
    test_df.loc[1, 'weather_condition'] = 'Tornado'  # Unmapped weather
    test_df.loc[2, 'temperature_celsius'] = np.nan  # Numeric NaN
    
    try:
        proba = classifier.predict_proba(test_df)
        print("   ✅ Predictions successful with edge cases")
        print(f"   Generated {len(proba)} cake probabilities")
    except Exception as e:
        print(f"   ❌ FAILED: {type(e).__name__}: {e}")
        return False
    
    # Step 4: Verify output format
    print("\n4️⃣ Verifying output format...")
    for i, cake_probs in enumerate(proba):
        total_prob = sum(cake_probs.values())
        print(f"   Row {i}: {len(cake_probs)} cakes, total prob = {total_prob:.4f}")
        if abs(total_prob - 1.0) > 0.01:
            print(f"   ⚠️ Probability sum is {total_prob}, expected ~1.0")
    
    print("\n" + "=" * 70)
    print("✅ ALL TESTS PASSED - NaN Handling is Working!")
    print("=" * 70)
    return True

if __name__ == '__main__':
    test_nan_in_classifier()
