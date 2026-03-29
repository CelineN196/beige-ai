"""
PRODUCTION FEATURE CONTRACT
===================================================================
Single source of truth for feature schema.
Used by training, inference, and validation.

Ensures:
- Consistent feature ordering
- Consistent categorical/numerical split
- Consistent feature names
- Safe transformation pipeline
"""

from typing import List, Dict, Tuple

# ===================================================================
# FEATURE SCHEMA (LOCKED - DO NOT MODIFY WITHOUT RETRAINING)
# ===================================================================

# Categorical features in exact order (must match training)
CATEGORICAL_FEATURES: List[str] = [
    'mood',
    'weather_condition', 
    'time_of_day',
    'season',
    'temperature_category'
]

# Numerical features in exact order (must match training)
NUMERICAL_FEATURES: List[str] = [
    'temperature_celsius',
    'humidity',
    'air_quality_index',
    'sweetness_preference',
    'health_preference',
    'trend_popularity_score',
    'comfort_index',
    'environmental_score'
]

# Categorical value enums (constraints)
CATEGORICAL_VALUES: Dict[str, List[str]] = {
    'mood': ['Happy', 'Stressed', 'Tired', 'Lonely', 'Celebratory'],
    'weather_condition': ['Sunny', 'Rainy', 'Cloudy', 'Snowy', 'Stormy'],
    'time_of_day': ['Morning', 'Afternoon', 'Evening', 'Night'],
    'season': ['Winter', 'Spring', 'Summer', 'Autumn'],
    'temperature_category': ['cold', 'mild', 'hot']
}

# Target classes (cake types) in exact order
CAKE_TYPES: List[str] = [
    'Berry Garden Cake',
    'Café Tiramisu',
    'Citrus Cloud Cake',
    'Dark Chocolate Sea Salt Cake',
    'Earthy Wellness Cake',
    'Korean Sesame Mini Bread',
    'Matcha Zen Cake',
    'Silk Cheesecake'
]

# ===================================================================
# DERIVED CONSTANTS
# ===================================================================

ALL_FEATURES: List[str] = CATEGORICAL_FEATURES + NUMERICAL_FEATURES
"""Complete list of input features in order."""

NUM_CATEGORICAL: int = len(CATEGORICAL_FEATURES)
NUM_NUMERICAL: int = len(NUMERICAL_FEATURES)
TOTAL_INPUT_FEATURES: int = len(ALL_FEATURES)

# After OneHotEncoding: 
# mood: 5 values → 5 columns
# weather_condition: 5 → 5
# time_of_day: 4 → 4
# season: 4 → 4
# temperature_category: 3 → 3
# Total: 5+5+4+4+3 = 21 one-hot features + 8 numerical = 29 total
ONE_HOT_FEATURES: int = 21
TOTAL_ENCODED_FEATURES: int = ONE_HOT_FEATURES + NUM_NUMERICAL  # 29
NUM_CLASSES: int = len(CAKE_TYPES)

# ===================================================================
# CONTRACT FUNCTIONS
# ===================================================================

def get_feature_schema() -> Dict[str, List[str]]:
    """Return the complete feature schema.
    
    Returns:
        Dict with 'categorical' and 'numerical' keys
    """
    return {
        'categorical': CATEGORICAL_FEATURES,
        'numerical': NUMERICAL_FEATURES,
        'all': ALL_FEATURES,
        'classes': CAKE_TYPES
    }

def validate_feature_order(columns: List[str]) -> Tuple[bool, str]:
    """Validate if DataFrame columns match contract.
    
    Args:
        columns: Column names from DataFrame
        
    Returns:
        (is_valid, message)
    """
    if list(columns) != ALL_FEATURES:
        return False, (
            f"Column mismatch. Expected: {ALL_FEATURES}, "
            f"Got: {list(columns)}"
        )
    return True, "✓ Feature order valid"

def validate_categorical_values(data_dict: Dict[str, any]) -> Tuple[bool, str]:
    """Validate categorical values are in allowed set.
    
    Args:
        data_dict: Dictionary with feature values
        
    Returns:
        (is_valid, message)
    """
    for cat_feature in CATEGORICAL_FEATURES:
        value = data_dict.get(cat_feature)
        allowed = CATEGORICAL_VALUES[cat_feature]
        
        if value not in allowed:
            return False, (
                f"{cat_feature}='{value}' not in allowed values: {allowed}"
            )
    
    return True, "✓ Categorical values valid"

def validate_encoded_features(num_encoded_features: int) -> Tuple[bool, str]:
    """Validate preprocessed feature count.
    
    After preprocessing, should have exactly TOTAL_ENCODED_FEATURES.
    
    Args:
        num_encoded_features: Number of features after preprocessing
        
    Returns:
        (is_valid, message)
    """
    if num_encoded_features != TOTAL_ENCODED_FEATURES:
        return False, (
            f"Encoded feature count mismatch. "
            f"Expected: {TOTAL_ENCODED_FEATURES}, Got: {num_encoded_features}"
        )
    return True, f"✓ Encoded features valid ({num_encoded_features})"

# ===================================================================
# PRINT UTILS (FOR DEBUGGING)
# ===================================================================

def print_schema():
    """Print feature contract for debugging."""
    print("\n" + "="*70)
    print("FEATURE CONTRACT")
    print("="*70)
    print(f"\nCategorical Features ({len(CATEGORICAL_FEATURES)}):")
    for i, f in enumerate(CATEGORICAL_FEATURES, 1):
        print(f"  {i}. {f}: {CATEGORICAL_VALUES[f]}")
    
    print(f"\nNumerical Features ({len(NUMERICAL_FEATURES)}):")
    for i, f in enumerate(NUMERICAL_FEATURES, 1):
        print(f"  {i}. {f}")
    
    print(f"\nTarget Classes ({len(CAKE_TYPES)}):")
    for i, c in enumerate(CAKE_TYPES):
        print(f"  {i}: {c}")
    
    print(f"\nEncoding Summary:")
    print(f"  One-hot features: {ONE_HOT_FEATURES}")
    print(f"  Numerical features: {NUM_NUMERICAL}")
    print(f"  Total encoded: {TOTAL_ENCODED_FEATURES}")
    print("="*70 + "\n")

if __name__ == "__main__":
    print_schema()
    
    # Test validation
    test_data = {
        'mood': 'Happy',
        'weather_condition': 'Sunny',
        'time_of_day': 'Morning',
        'season': 'Spring',
        'temperature_category': 'mild',
        'temperature_celsius': 20,
        'humidity': 60,
        'air_quality_index': 50,
        'sweetness_preference': 5,
        'health_preference': 7,
        'trend_popularity_score': 0.5,
        'comfort_index': 0.6,
        'environmental_score': 0.7
    }
    
    is_valid, msg = validate_categorical_values(test_data)
    print(f"Validation result: {is_valid} - {msg}")
