#!/usr/bin/env python3
"""
Beige.AI Cake Recommendation Inference Pipeline

Load trained XGBoost model and make predictions on user input.
Handles preprocessing, feature engineering, and explanation generation.

Author: ML Engineering Team
Date: March 19, 2026
"""

import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Any
import warnings

warnings.filterwarnings('ignore')


# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "backend" / "models"

# Expected input features (10 core features)
EXPECTED_INPUT_FEATURES = [
    'mood',
    'weather_condition',
    'temperature_celsius',
    'humidity',
    'season',
    'air_quality_index',
    'time_of_day',
    'sweetness_preference',
    'health_preference',
    'trend_popularity_score'
]


# ============================================================================
# FEATURE ENGINEERING
# ============================================================================

def create_derived_features(user_input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create derived features from raw input.
    
    Derived features:
    - temperature_category: Based on temperature_celsius
    - comfort_index: Combination of temperature, humidity, air quality
    - environmental_score: Based on weather, season, air quality
    
    Args:
        user_input: Dictionary with raw user inputs
    
    Returns:
        Dictionary with additional derived features
    """
    features = user_input.copy()
    
    temp = features.get('temperature_celsius', 20)
    humidity = features.get('humidity', 50)
    air_quality = features.get('air_quality_index', 50)
    weather = features.get('weather_condition', 'Sunny')
    
    # Temperature category
    if temp < 10:
        features['temperature_category'] = 'cold'
    elif temp > 25:
        features['temperature_category'] = 'hot'
    else:
        features['temperature_category'] = 'mild'
    
    # Comfort index (0-1): higher temp and humidity + lower air quality = lower comfort
    # Normalized to 0-1 range
    comfort = 1.0 - (abs(temp - 22) / 40) * 0.4 - (humidity / 100) * 0.3 - (air_quality / 100) * 0.3
    comfort = max(0, min(1, comfort))
    features['comfort_index'] = comfort
    
    # Environmental score (0-1): based on weather and air quality
    weather_score = {
        'Sunny': 0.9,
        'Cloudy': 0.7,
        'Rainy': 0.5,
        'Stormy': 0.3,
        'Snowy': 0.6
    }
    
    season_score = {
        'Spring': 0.9,
        'Summer': 0.85,
        'Autumn': 0.75,
        'Winter': 0.6
    }
    
    w_score = weather_score.get(weather, 0.5)
    s_score = season_score.get(features.get('season', 'Spring'), 0.5)
    air_score = 1.0 - (air_quality / 100)
    
    env_score = (w_score * 0.4 + s_score * 0.3 + air_score * 0.3)
    features['environmental_score'] = max(0, min(1, env_score))
    
    return features


def preprocess_input(user_input: Dict[str, Any], model_metadata: Dict[str, Any]) -> np.ndarray:
    """
    Preprocess user input to match training preprocessing.
    
    Process:
    1. Create derived features
    2. One-hot encode categorical features
    3. Scale numerical features
    4. Arrange in correct order matching model training
    
    Args:
        user_input: Raw user input dictionary
        model_metadata: Metadata from feature_info.joblib
    
    Returns:
        Preprocessed feature array ready for model prediction
    """
    
    # Create derived features
    enriched_input = create_derived_features(user_input)
    
    # Convert to DataFrame for easier processing
    df = pd.DataFrame([enriched_input])
    
    # Define categorical and numerical features based on training
    categorical_features = ['mood', 'weather_condition', 'season', 'time_of_day', 'temperature_category']
    numerical_features = [
        'temperature_celsius', 'humidity', 'air_quality_index',
        'sweetness_preference', 'health_preference', 'trend_popularity_score',
        'comfort_index', 'environmental_score'
    ]
    
    # One-hot encode categorical features
    categorical_dummies = pd.get_dummies(
        df[categorical_features],
        columns=categorical_features,
        drop_first=False
    )
    
    # Scale numerical features (using min-max normalization for inference)
    # Note: In production, you'd load the fitted StandardScaler from training
    # For now, using reasonable defaults based on feature ranges
    numerical_scaled = df[numerical_features].copy()
    
    # Apply known scaling parameters from training data
    scaling_params = {
        'temperature_celsius': {'mean': 15, 'std': 10},
        'humidity': {'mean': 50, 'std': 25},
        'air_quality_index': {'mean': 50, 'std': 30},
        'sweetness_preference': {'mean': 5, 'std': 2.5},
        'health_preference': {'mean': 5, 'std': 2.5},
        'trend_popularity_score': {'mean': 5, 'std': 2.5},
        'comfort_index': {'mean': 0.5, 'std': 0.2},
        'environmental_score': {'mean': 0.5, 'std': 0.2},
    }
    
    for feature in numerical_features:
        if feature in scaling_params:
            params = scaling_params[feature]
            numerical_scaled[feature] = (numerical_scaled[feature] - params['mean']) / params['std']
    
    # Combine one-hot encoded and scaled features
    processed_df = pd.concat([categorical_dummies, numerical_scaled], axis=1)
    
    # Reorder columns to match model's expected feature order
    feature_names_expected = model_metadata['features']
    
    # Create feature array with correct order
    feature_array = np.zeros((1, len(feature_names_expected)))
    
    for i, feature_name in enumerate(feature_names_expected):
        if feature_name in processed_df.columns:
            feature_array[0, i] = processed_df[feature_name].values[0]
    
    return feature_array


# ============================================================================
# PREDICTION & EXPLANATION
# ============================================================================

def generate_explanation(user_input: Dict[str, Any], top_cake: str, probability: float) -> str:
    """
    Generate human-readable explanation for the recommendation.
    
    Args:
        user_input: User input dictionary
        top_cake: Recommended cake name
        probability: Prediction probability
    
    Returns:
        Explanation string
    """
    
    mood = user_input.get('mood', '').lower()
    weather = user_input.get('weather_condition', '').lower()
    temp = user_input.get('temperature_celsius', 0)
    sweetness = user_input.get('sweetness_preference', 5)
    health = user_input.get('health_preference', 5)
    
    reasons = []
    
    # Mood-based reasons
    if mood in ['happy', 'celebratory']:
        reasons.append(f"Your {mood} mood pairs well with this cake")
    elif mood == 'stressed':
        reasons.append("This cake is a great comfort choice for stress relief")
    elif mood == 'tired':
        reasons.append("This cake offers a refreshing energy boost")
    elif mood == 'lonely':
        reasons.append("This cake is perfect for self-care and treating yourself")
    
    # Weather-based reasons
    if weather == 'sunny' and temp > 25:
        reasons.append("It's perfect for hot, sunny weather")
    elif weather in ['rainy', 'snowy', 'stormy']:
        reasons.append("This cozy choice complements the cool weather")
    
    # Sweetness preference
    if sweetness <= 3:
        reasons.append("Made with your light sweetness preference in mind")
    elif sweetness >= 7:
        reasons.append("The perfect indulgent sweet treat for your taste")
    
    # Health preference
    if health >= 7:
        reasons.append("Contains nutritious ingredients aligned with your preferences")
    
    explanation = f"🎂 **{top_cake}** (Confidence: {probability*100:.1f}%)"
    if reasons:
        explanation += "\n\n**Why this cake?**\n- " + "\n- ".join(reasons)
    
    return explanation


def predict_cake(user_input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Make cake recommendation based on user input.
    
    Args:
        user_input: Dictionary with user features {
            'mood': str,
            'weather_condition': str,
            'temperature_celsius': float,
            'humidity': float,
            'season': str,
            'air_quality_index': float,
            'time_of_day': str,
            'sweetness_preference': int (1-10),
            'health_preference': int (1-10),
            'trend_popularity_score': float
        }
    
    Returns:
        Dictionary with format:
        {
            'top_prediction': 'Cake Name',
            'confidence': 0.85,
            'explanation': 'Recommended because...',
            'top_3': [
                {'cake': 'Cake Name 1', 'probability': 0.45},
                {'cake': 'Cake Name 2', 'probability': 0.30},
                {'cake': 'Cake Name 3', 'probability': 0.15}
            ]
        }
    """
    
    try:
        # Load model and metadata
        model_path = MODELS_DIR / "best_model.joblib"
        metadata_path = MODELS_DIR / "feature_info.joblib"
        
        if not model_path.exists() or not metadata_path.exists():
            raise FileNotFoundError(f"Model files not found in {MODELS_DIR}")
        
        model = joblib.load(model_path)
        metadata = joblib.load(metadata_path)
        
        # Validate input
        missing_features = [f for f in EXPECTED_INPUT_FEATURES if f not in user_input]
        if missing_features:
            raise ValueError(f"Missing required features: {missing_features}")
        
        # Preprocess input
        X_processed = preprocess_input(user_input, metadata)
        
        # Get predictions
        y_pred = model.predict(X_processed)[0]
        
        # Get prediction probabilities
        if hasattr(model, 'predict_proba'):
            y_proba = model.predict_proba(X_processed)[0]
        else:
            # For XGBoost, use decision_function or simulate probabilities
            y_proba = model.predict_proba(X_processed)[0] if hasattr(model, 'predict_proba') else None
        
        target_classes = metadata['target_classes']
        
        # Get top 1 prediction
        top_pred_idx = np.argmax(y_proba) if y_proba is not None else 0
        top_cake = target_classes[top_pred_idx]
        top_prob = float(y_proba[top_pred_idx]) if y_proba is not None else 1.0
        
        # Get top 3 predictions
        if y_proba is not None:
            top_3_indices = np.argsort(y_proba)[-3:][::-1]
            top_3_predictions = [
                {
                    'cake': target_classes[idx],
                    'probability': float(y_proba[idx])
                }
                for idx in top_3_indices
            ]
        else:
            top_3_predictions = [
                {'cake': top_cake, 'probability': top_prob}
            ]
        
        # Generate explanation
        explanation = generate_explanation(user_input, top_cake, top_prob)
        
        return {
            'top_prediction': top_cake,
            'confidence': top_prob,
            'explanation': explanation,
            'top_3': top_3_predictions,
            'input_features': user_input
        }
    
    except Exception as e:
        return {
            'error': str(e),
            'top_prediction': None,
            'confidence': 0.0
        }


# ============================================================================
# TESTING & EXAMPLES
# ============================================================================

def run_example_predictions():
    """Run example predictions to demonstrate the pipeline."""
    
    # Example 1: Sunny day, happy mood, light sweetness
    user_input_1 = {
        'mood': 'Happy',
        'weather_condition': 'Sunny',
        'temperature_celsius': 28.0,
        'humidity': 45.0,
        'season': 'Summer',
        'air_quality_index': 40,
        'time_of_day': 'Afternoon',
        'sweetness_preference': 3,
        'health_preference': 8,
        'trend_popularity_score': 8.5
    }
    
    # Example 2: Cold, stressed mood, comforting
    user_input_2 = {
        'mood': 'Stressed',
        'weather_condition': 'Snowy',
        'temperature_celsius': -5.0,
        'humidity': 70.0,
        'season': 'Winter',
        'air_quality_index': 55,
        'time_of_day': 'Evening',
        'sweetness_preference': 7,
        'health_preference': 4,
        'trend_popularity_score': 7.0
    }
    
    # Example 3: Celebratory mood
    user_input_3 = {
        'mood': 'Celebratory',
        'weather_condition': 'Sunny',
        'temperature_celsius': 22.0,
        'humidity': 50.0,
        'season': 'Spring',
        'air_quality_index': 35,
        'time_of_day': 'Evening',
        'sweetness_preference': 8,
        'health_preference': 5,
        'trend_popularity_score': 9.0
    }
    
    examples = [
        ("☀️ Sunny Summer Day", user_input_1),
        ("❄️ Cold Winter Evening", user_input_2),
        ("🎉 Celebratory Spring Evening", user_input_3),
    ]
    
    print("\n" + "="*80)
    print("🍰 BEIGE.AI CAKE RECOMMENDATION INFERENCE PIPELINE")
    print("="*80)
    
    for title, user_input in examples:
        print(f"\n{'─'*80}")
        print(f"📌 Scenario: {title}")
        print(f"{'─'*80}")
        
        result = predict_cake(user_input)
        
        if 'error' in result and result['error']:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"\n{result['explanation']}")
            print(f"\n🏆 Top 3 Recommendations:")
            for i, item in enumerate(result['top_3'], 1):
                prob_pct = item['probability'] * 100
                print(f"   {i}. {item['cake']:<35} ({prob_pct:5.1f}%)")
    
    print(f"\n{'='*80}\n")


if __name__ == "__main__":
    run_example_predictions()
