"""
INFERENCE PIPELINE - SAFE FEATURE VALIDATION
===================================================================
Validates and transforms feature inputs before model prediction.

Responsibilities:
1. Validate feature schema
2. Check categorical value constraints
3. Validate numerical ranges
4. Handle missing/unknown values gracefully
5. Ensure shape matches model expectations
6. Provide clear error messages
"""

import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any, List
import sys

from backend.feature_contract import (
    CATEGORICAL_FEATURES,
    NUMERICAL_FEATURES,
    CATEGORICAL_VALUES,
    validate_feature_order,
    validate_categorical_values,
    validate_encoded_features,
    ALL_FEATURES,
    TOTAL_ENCODED_FEATURES,
)

# ===================================================================
# INPUT VALIDATION
# ===================================================================

class FeaturePipelineValidator:
    """Validates features before inference."""
    
    @staticmethod
    def validate_raw_input(data_dict: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate raw input dictionary.
        
        Args:
            data_dict: Dictionary with feature values
            
        Returns:
            (is_valid, message)
        """
        # Check all features present
        missing = set(ALL_FEATURES) - set(data_dict.keys())
        if missing:
            return False, f"Missing features: {missing}"
        
        # Validate categorical values
        is_valid, msg = validate_categorical_values(data_dict)
        if not is_valid:
            return False, msg
        
        # Validate numerical ranges (basic sanity checks)
        for num_feat in NUMERICAL_FEATURES:
            value = data_dict.get(num_feat)
            if value is None:
                return False, f"Missing numerical feature: {num_feat}"
            
            # Basic range checks (not too extreme)
            if not isinstance(value, (int, float)):
                return False, f"{num_feat} must be numeric, got {type(value)}"
            
            if np.isnan(value) or np.isinf(value):
                return False, f"{num_feat} has invalid value: {value}"
        
        return True, "✓ Raw input valid"
    
    @staticmethod
    def create_dataframe(data_dict: Dict[str, Any]) -> pd.DataFrame:
        """Create DataFrame from input dictionary.
        
        Ensures column order matches contract.
        
        Args:
            data_dict: Dictionary with feature values
            
        Returns:
            DataFrame with correct column order
            
        Raises:
            ValueError: If data doesn't match schema
        """
        # Validate first
        is_valid, msg = FeaturePipelineValidator.validate_raw_input(data_dict)
        if not is_valid:
            raise ValueError(f"Input validation failed: {msg}")
        
        # Create DataFrame with correct column order
        df = pd.DataFrame([{feat: data_dict[feat] for feat in ALL_FEATURES}])
        
        # Validate column order
        is_valid, msg = validate_feature_order(df.columns.tolist())
        if not is_valid:
            raise ValueError(f"Column order validation failed: {msg}")
        
        return df
    
    @staticmethod
    def validate_preprocessed_features(
        X_processed: np.ndarray,
        preprocessor: Any
    ) -> Tuple[bool, str]:
        """Validate preprocessed features.
        
        Args:
            X_processed: Preprocessed feature array
            preprocessor: The ColumnTransformer used for preprocessing
            
        Returns:
            (is_valid, message)
        """
        # Check shape
        if len(X_processed.shape) != 2:
            return False, f"Expected 2D array, got shape {X_processed.shape}"
        
        expected_features = TOTAL_ENCODED_FEATURES
        actual_features = X_processed.shape[1]
        
        if actual_features != expected_features:
            return False, (
                f"Feature count mismatch after preprocessing. "
                f"Expected {expected_features}, got {actual_features}"
            )
        
        # Check for NaN values
        if np.isnan(X_processed).any():
            return False, "Preprocessed features contain NaN values"
        
        # Check for infinite values
        if np.isinf(X_processed).any():
            return False, "Preprocessed features contain infinite values"
        
        return True, f"✓ Preprocessed features valid ({actual_features})"
    
    @staticmethod
    def validate_predictions(
        y_proba: np.ndarray,
        expected_classes: int
    ) -> Tuple[bool, str]:
        """Validate prediction output.
        
        Args:
            y_proba: Probability array from predict_proba
            expected_classes: Expected number of classes
            
        Returns:
            (is_valid, message)
        """
        # Check shape
        if len(y_proba.shape) != 2:
            return False, f"Expected 2D probabilities, got {y_proba.shape}"
        
        if y_proba.shape[1] != expected_classes:
            return False, (
                f"Class count mismatch. "
                f"Expected {expected_classes}, got {y_proba.shape[1]}"
            )
        
        # Check probabilities sum to ~1.0
        proba_sums = y_proba.sum(axis=1)
        if not np.allclose(proba_sums, 1.0, atol=1e-5):
            return False, f"Probabilities don't sum to 1.0: {proba_sums}"
        
        # Check values in [0, 1]
        if (y_proba < 0).any() or (y_proba > 1).any():
            return False, "Probabilities outside [0, 1]"
        
        return True, "✓ Prediction output valid"


# ===================================================================
# SAFE INFERENCE PIPELINE
# ===================================================================

class InferencePipeline:
    """Safe, validated inference pipeline."""
    
    def __init__(self, model: Any, preprocessor: Any, label_encoder: Any = None, verbose: bool = True):
        """Initialize pipeline.
        
        Args:
            model: Fitted model with predict_proba
            preprocessor: Fitted preprocessing pipeline
            label_encoder: Optional label encoder for class names
            verbose: Print debug info
        """
        self.model = model
        self.preprocessor = preprocessor
        self.label_encoder = label_encoder
        self.verbose = verbose
        self.validator = FeaturePipelineValidator()
    
    def predict_proba_safe(
        self,
        input_dict: Dict[str, Any]
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Safe prediction with validation.
        
        Args:
            input_dict: Dictionary with feature values
            
        Returns:
            (probabilities, debug_info)
            
        Raises:
            ValueError: If validation fails at any stage
        """
        debug_info = {}
        
        try:
            # Step 1: Validate raw input
            is_valid, msg = self.validator.validate_raw_input(input_dict)
            if not is_valid:
                raise ValueError(f"Input validation: {msg}")
            debug_info['raw_input_valid'] = True
            
            # Step 2: Create DataFrame
            df = self.validator.create_dataframe(input_dict)
            debug_info['dataframe_created'] = True
            
            # Step 3: Preprocess
            X_processed = self.preprocessor.transform(df)
            debug_info['preprocessed'] = True
            
            # Step 4: Validate preprocessed features
            is_valid, msg = self.validator.validate_preprocessed_features(
                X_processed, self.preprocessor
            )
            if not is_valid:
                raise ValueError(f"Preprocessing validation: {msg}")
            debug_info['preprocessed_valid'] = True
            debug_info['num_features_processed'] = X_processed.shape[1]
            
            # Step 5: Predict
            y_proba = self.model.predict_proba(X_processed)
            debug_info['prediction_made'] = True
            
            # Step 6: Validate predictions
            is_valid, msg = self.validator.validate_predictions(
                y_proba, len(self._get_classes())
            )
            if not is_valid:
                raise ValueError(f"Prediction validation: {msg}")
            debug_info['prediction_valid'] = True
            
            if self.verbose:
                print(f"✓ Inference successful")
            
            return y_proba[0], debug_info
            
        except Exception as e:
            debug_info['error'] = str(e)
            if self.verbose:
                print(f"❌ Inference failed: {str(e)}")
            raise
    
    def predict_with_explanations(
        self,
        input_dict: Dict[str, Any],
        top_k: int = 3
    ) -> Dict[str, Any]:
        """Predict and return top recommendations with explanations.
        
        Args:
            input_dict: Dictionary with feature values
            top_k: Number of top recommendations
            
        Returns:
            Dictionary with predictions and metadata
        """
        y_proba, debug_info = self.predict_proba_safe(input_dict)
        
        # Get top K
        top_indices = np.argsort(y_proba)[-top_k:][::-1]
        classes = self._get_classes()
        
        return {
            'probabilities': y_proba.tolist(),
            'top_k': [
                {
                    'rank': i + 1,
                    'class': classes[idx],
                    'probability': float(y_proba[idx])
                }
                for i, idx in enumerate(top_indices)
            ],
            'debug': debug_info
        }
    
    def _get_classes(self) -> List[str]:
        """Get class names."""
        if self.label_encoder is not None:
            return list(self.label_encoder.classes_)
        else:
            # Fallback to indices
            return [f"Class_{i}" for i in range(len(self.model.classes_))]


# ===================================================================
# CONVENIENCE FUNCTIONS
# ===================================================================

def create_inference_pipeline(
    model: Any,
    preprocessor: Any,
    label_encoder: Any = None,
    verbose: bool = True
) -> InferencePipeline:
    """Create a safe inference pipeline.
    
    Args:
        model: Fitted model
        preprocessor: Fitted preprocessing pipeline
        label_encoder: Optional label encoder
        verbose: Print debug info
        
    Returns:
        InferencePipeline instance
    """
    return InferencePipeline(model, preprocessor, label_encoder, verbose)

if __name__ == "__main__":
    # Test validation
    test_input = {
        'mood': 'Happy',
        'weather_condition': 'Sunny',
        'temperature_celsius': 25,
        'humidity': 60,
        'air_quality_index': 50,
        'time_of_day': 'Morning',
        'sweetness_preference': 7,
        'health_preference': 6,
        'trend_popularity_score': 0.5,
        'temperature_category': 'mild',
        'comfort_index': 0.6,
        'environmental_score': 0.7,
        'season': 'Summer'
    }
    
    validator = FeaturePipelineValidator()
    is_valid, msg = validator.validate_raw_input(test_input)
    print(f"Validation: {is_valid} - {msg}")
    
    df = validator.create_dataframe(test_input)
    print(f"DataFrame shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
