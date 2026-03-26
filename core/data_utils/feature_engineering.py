"""
Feature Engineering - Explicit Data Preprocessing
==================================================
SINGLE RESPONSIBILITY: Transform raw user input into ML-ready features.

All NaN handling, encoding, validation happens here ONLY.
"""

import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any
import warnings

warnings.filterwarnings('ignore')


class FeatureEngineeringError(Exception):
    """Raised when feature engineering fails."""
    pass


class FeatureEncoder:
    """Handle all feature encoding and preprocessing."""
    
    # Input features required by the model
    INPUT_FEATURES = [
        'mood', 'weather_condition', 'temperature_celsius', 'humidity',
        'season', 'air_quality_index', 'time_of_day', 'sweetness_preference',
        'health_preference', 'trend_popularity_score', 'temperature_category',
        'comfort_index', 'environmental_score'
    ]
    
    # Categorical mappings
    CATEGORICAL_MAPPINGS = {
        'mood': ['Happy', 'Stressed', 'Tired', 'Lonely', 'Celebratory'],
        'weather_condition': ['Sunny', 'Rainy', 'Cloudy', 'Snowy', 'Stormy'],
        'season': ['Spring', 'Summer', 'Autumn', 'Winter'],
        'time_of_day': ['Morning', 'Afternoon', 'Evening', 'Night'],
        'temperature_category': ['cold', 'mild', 'warm', 'hot']
    }
    
    def __init__(self):
        self.feature_names = self.INPUT_FEATURES
    
    def transform(self, input_data: Dict[str, Any]) -> np.ndarray:
        """
        Transform raw user input into ML-ready features.
        
        Args:
            input_data: Dictionary containing user inputs
        
        Returns:
            numpy array of shape (1, n_features) ready for model inference
        
        Raises:
            FeatureEngineeringError: If transformation fails
        """
        try:
            # Create DataFrame from input
            df = pd.DataFrame([input_data])
            
            # Validate all required features are present
            self._validate_features(df)
            
            # Handle categorical encoding (with safe NaN handling)
            df = self._encode_categorical(df)
            
            # Handle numeric NaNs
            df = self._handle_numeric_nans(df)
            
            # Final validation - no NaNs should remain
            self._validate_no_nans(df)
            
            # Return as numpy array
            X = df[self.INPUT_FEATURES].values
            
            return X
        
        except FeatureEngineeringError:
            raise
        except Exception as e:
            raise FeatureEngineeringError(
                f"Feature transformation failed: {str(e)}"
            )
    
    def _validate_features(self, df: pd.DataFrame) -> None:
        """Validate that all required features are present."""
        missing_features = set(self.INPUT_FEATURES) - set(df.columns)
        
        if missing_features:
            raise FeatureEngineeringError(
                f"Missing required features: {missing_features}"
            )
    
    def _encode_categorical(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Encode categorical features to integers.
        
        Safe mapping: unmapped values become 0 (safe default)
        """
        df = df.copy()
        
        for col, categories in self.CATEGORICAL_MAPPINGS.items():
            if col in df.columns:
                # Create mapping: category -> index
                mapping = {cat: idx for idx, cat in enumerate(categories)}
                
                # Apply mapping with safe default for unmapped values
                df[col] = df[col].astype(str).map(mapping).fillna(0).astype(int)
        
        return df
    
    def _handle_numeric_nans(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fill any remaining NaNs in numeric columns."""
        df = df.copy()
        
        # Fill numeric NaNs with 0
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if df[col].isna().any():
                df[col].fillna(0, inplace=True)
        
        return df
    
    def _validate_no_nans(self, df: pd.DataFrame) -> None:
        """Final validation: no NaNs should remain."""
        if df.isna().any().any():
            nan_cols = df.columns[df.isna().any()].tolist()
            raise FeatureEngineeringError(
                f"NaNs remain after preprocessing in columns: {nan_cols}"
            )
    
    def get_feature_info(self) -> Dict[str, Any]:
        """Get information about the feature set."""
        return {
            'n_features': len(self.INPUT_FEATURES),
            'feature_names': self.INPUT_FEATURES,
            'categorical_features': list(self.CATEGORICAL_MAPPINGS.keys()),
            'numeric_features': [
                f for f in self.INPUT_FEATURES 
                if f not in self.CATEGORICAL_MAPPINGS
            ]
        }
