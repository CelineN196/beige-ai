#!/usr/bin/env python3
"""
Beige.AI Cake Recommendation - Integration Examples

Shows how to use the inference pipeline in different scenarios:
1. Single prediction
2. Batch predictions
3. Real-time recommendations
4. Integration with backends

Author: ML Engineering Team
Date: March 19, 2026
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.inference import predict_cake
from backend.api import CakeRecommendationAPI
import json
from typing import List, Dict, Any


# ============================================================================
# EXAMPLE 1: SINGLE PREDICTION
# ============================================================================

def example_single_prediction():
    """Make a single recommendation."""
    
    print("\n" + "="*80)
    print("EXAMPLE 1: Single Prediction")
    print("="*80)
    
    # Define user input
    user_input = {
        'mood': 'Happy',
        'weather_condition': 'Sunny',
        'temperature_celsius': 28.0,
        'humidity': 45.0,
        'season': 'Summer',
        'air_quality_index': 40,
        'time_of_day': 'Afternoon',
        'sweetness_preference': 5,
        'health_preference': 8,
        'trend_popularity_score': 8.5
    }
    
    # Get recommendation
    result = predict_cake(user_input)
    
    # Display result
    print(f"\nTop Recommendation: {result['top_prediction']}")
    print(f"Confidence: {result['confidence']*100:.1f}%")
    print(f"\n{result['explanation']}")
    print(f"\nTop 3 Options:")
    for i, item in enumerate(result['top_3'], 1):
        print(f"  {i}. {item['cake']:<35} {item['probability']*100:5.1f}%")


# ============================================================================
# EXAMPLE 2: BATCH PREDICTIONS
# ============================================================================

def example_batch_predictions():
    """Make recommendations for multiple users."""
    
    print("\n" + "="*80)
    print("EXAMPLE 2: Batch Predictions")
    print("="*80)
    
    # Multiple user scenarios
    users = [
        {
            'name': 'Alice - Morning Commute',
            'input': {
                'mood': 'Tired',
                'weather_condition': 'Cloudy',
                'temperature_celsius': 15.0,
                'humidity': 60.0,
                'season': 'Autumn',
                'air_quality_index': 50,
                'time_of_day': 'Morning',
                'sweetness_preference': 7,
                'health_preference': 6,
                'trend_popularity_score': 6.0
            }
        },
        {
            'name': 'Bob - Stressful Day',
            'input': {
                'mood': 'Stressed',
                'weather_condition': 'Rainy',
                'temperature_celsius': 18.0,
                'humidity': 75.0,
                'season': 'Winter',
                'air_quality_index': 60,
                'time_of_day': 'Evening',
                'sweetness_preference': 8,
                'health_preference': 3,
                'trend_popularity_score': 5.0
            }
        },
        {
            'name': 'Carol - Celebration',
            'input': {
                'mood': 'Celebratory',
                'weather_condition': 'Sunny',
                'temperature_celsius': 25.0,
                'humidity': 40.0,
                'season': 'Spring',
                'air_quality_index': 35,
                'time_of_day': 'Evening',
                'sweetness_preference': 9,
                'health_preference': 5,
                'trend_popularity_score': 9.0
            }
        }
    ]
    
    # Make predictions for all users
    print(f"\nMaking predictions for {len(users)} users...\n")
    
    results = []
    for user in users:
        result = predict_cake(user['input'])
        result['user_name'] = user['name']
        results.append(result)
        
        print(f"👤 {user['name']}")
        print(f"   Recommendation: {result['top_prediction']}")
        print(f"   Confidence: {result['confidence']*100:.1f}%")
        print()
    
    return results


# ============================================================================
# EXAMPLE 3: REAL-TIME RECOMMENDATIONS
# ============================================================================

def example_real_time_recommendation():
    """Get recommendation based on current time and season."""
    
    print("\n" + "="*80)
    print("EXAMPLE 3: Real-Time Recommendations")
    print("="*80)
    
    from datetime import datetime
    
    now = datetime.now()
    hour = now.hour
    month = now.month
    
    # Determine time of day
    if 6 <= hour < 12:
        time_of_day = 'Morning'
    elif 12 <= hour < 17:
        time_of_day = 'Afternoon'
    elif 17 <= hour < 21:
        time_of_day = 'Evening'
    else:
        time_of_day = 'Night'
    
    # Determine season (simplified)
    if month in [12, 1, 2]:
        season = 'Winter'
    elif month in [3, 4, 5]:
        season = 'Spring'
    elif month in [6, 7, 8]:
        season = 'Summer'
    else:
        season = 'Autumn'
    
    # Create user input with current time/season
    # In real implementation, you'd get weather from an API
    user_input = {
        'mood': 'Happy',
        'weather_condition': 'Sunny',
        'temperature_celsius': 22.0,
        'humidity': 50.0,
        'season': season,
        'air_quality_index': 45,
        'time_of_day': time_of_day,
        'sweetness_preference': 5,
        'health_preference': 7,
        'trend_popularity_score': 7.0
    }
    
    result = predict_cake(user_input)
    
    print(f"\n📅 Current Time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏰ Time of Day: {time_of_day}")
    print(f"🍂 Season: {season}")
    print(f"\n🎂 Recommendation for now: {result['top_prediction']}")
    print(f"Confidence: {result['confidence']*100:.1f}%")


# ============================================================================
# EXAMPLE 4: API WRAPPER INTEGRATION
# ============================================================================

def example_api_wrapper():
    """Use the API wrapper for request validation and formatting."""
    
    print("\n" + "="*80)
    print("EXAMPLE 4: API Wrapper Integration")
    print("="*80)
    
    api = CakeRecommendationAPI()
    
    # Valid request
    valid_request = {
        'mood': 'Happy',
        'weather_condition': 'Sunny',
        'temperature_celsius': 25.0,
        'humidity': 50.0,
        'season': 'Summer',
        'air_quality_index': 40,
        'time_of_day': 'Afternoon',
        'sweetness_preference': 6,
        'health_preference': 7,
        'trend_popularity_score': 7.5
    }
    
    result = api.recommend(valid_request)
    
    print(f"\nAPI Health: {api.health_check()}")
    print(f"\nAPI Response Status: {result['status']}")
    
    if result['status'] == 'success':
        print(f"Recommendation: {result['data']['top_prediction']}")
        print(f"Confidence: {result['data']['confidence']}")
    else:
        print(f"Error: {result['message']}")
    
    print(f"\nAPI Stats:")
    print(f"  Total Predictions: {api.total_predictions}")
    print(f"  Total Errors: {len(api.inference_errors)}")


# ============================================================================
# EXAMPLE 5: JSON EXPORT
# ============================================================================

def example_json_export():
    """Export recommendations as JSON for API responses."""
    
    print("\n" + "="*80)
    print("EXAMPLE 5: JSON Export")
    print("="*80)
    
    user_input = {
        'mood': 'Happy',
        'weather_condition': 'Sunny',
        'temperature_celsius': 25.0,
        'humidity': 50.0,
        'season': 'Summer',
        'air_quality_index': 40,
        'time_of_day': 'Afternoon',
        'sweetness_preference': 5,
        'health_preference': 8,
        'trend_popularity_score': 8.5
    }
    
    result = predict_cake(user_input)
    
    # Format for JSON response
    json_response = {
        'status': 'success',
        'data': {
            'top_prediction': result['top_prediction'],
            'confidence': float(result['confidence']),
            'top_3': [
                {
                    'cake': item['cake'],
                    'probability': float(item['probability'])
                }
                for item in result['top_3']
            ]
        }
    }
    
    print(f"\nJSON Response:")
    print(json.dumps(json_response, indent=2))
    
    # Save to file
    with open('/tmp/recommendation_response.json', 'w') as f:
        json.dump(json_response, f, indent=2)
    
    print(f"\n✅ Saved to: /tmp/recommendation_response.json")


# ============================================================================
# EXAMPLE 6: ERROR HANDLING
# ============================================================================

def example_error_handling():
    """Show proper error handling."""
    
    print("\n" + "="*80)
    print("EXAMPLE 6: Error Handling")
    print("="*80)
    
    # Test case 1: Missing features
    print("\n1️⃣ Missing Features:")
    incomplete_input = {
        'mood': 'Happy',
        'weather_condition': 'Sunny',
        # Missing other required features
    }
    
    result = predict_cake(incomplete_input)
    if 'error' in result and result['error']:
        print(f"   ❌ Error: {result['error']}")
    
    # Test case 2: Invalid values (using API wrapper)
    print("\n2️⃣ Invalid Input Values:")
    api = CakeRecommendationAPI()
    
    invalid_request = {
        'mood': 'INVALID_MOOD',  # Not in allowed values
        'weather_condition': 'Sunny',
        'temperature_celsius': 25.0,
        'humidity': 50.0,
        'season': 'Summer',
        'air_quality_index': 40,
        'time_of_day': 'Afternoon',
        'sweetness_preference': 5,
        'health_preference': 8,
        'trend_popularity_score': 8.5
    }
    
    result = api.recommend(invalid_request)
    if result['status'] == 'error':
        print(f"   ❌ Error: {result['message']}")
    
    # Test case 3: Out of range values
    print("\n3️⃣ Out of Range Values:")
    out_of_range = {
        'mood': 'Happy',
        'weather_condition': 'Sunny',
        'temperature_celsius': 25.0,
        'humidity': 150.0,  # Invalid: should be 0-100
        'season': 'Summer',
        'air_quality_index': 40,
        'time_of_day': 'Afternoon',
        'sweetness_preference': 5,
        'health_preference': 8,
        'trend_popularity_score': 8.5
    }
    
    result = api.recommend(out_of_range)
    if result['status'] == 'error':
        print(f"   ❌ Error: {result['message']}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Run all examples."""
    
    print("\n" + "="*80)
    print("🍰 BEIGE.AI CAKE RECOMMENDATION - INTEGRATION EXAMPLES")
    print("="*80)
    
    examples = [
        ("Single Prediction", example_single_prediction),
        ("Batch Predictions", example_batch_predictions),
        ("Real-Time Recommendation", example_real_time_recommendation),
        ("API Wrapper Integration", example_api_wrapper),
        ("JSON Export", example_json_export),
        ("Error Handling", example_error_handling),
    ]
    
    for i, (title, func) in enumerate(examples, 1):
        try:
            func()
        except Exception as e:
            print(f"\n❌ Example {i} ({title}) failed: {str(e)}")
    
    print("\n" + "="*80)
    print("✅ All examples completed!")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
