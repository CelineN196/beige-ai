"""
Prediction Engine - ML Inference Execution
===========================================
SINGLE RESPONSIBILITY: Run ML inference on preprocessed features.

NO LOGIC - Just calls the model with validated features.
"""

import numpy as np
from typing import Dict, List, Any
import warnings

warnings.filterwarnings('ignore')


class PredictionError(Exception):
    """Raised when prediction fails."""
    pass


class PredictionEngine:
    """Execute ML inference with explicit error handling."""
    
    def __init__(self, model: Any, label_encoder: Any):
        """
        Initialize prediction engine.
        
        Args:
            model: Trained ML model
            label_encoder: Label encoder for target classes
        """
        if model is None:
            raise PredictionError("Model is None")
        if label_encoder is None:
            raise PredictionError("Label encoder is None")
        
        self.model = model
        self.label_encoder = label_encoder
    
    def predict(self, X: np.ndarray) -> Dict[str, Any]:
        """
        Generate predictions from features.
        
        Args:
            X: numpy array of shape (n_samples, n_features)
        
        Returns:
            Dictionary with prediction results
        
        Raises:
            PredictionError: If prediction fails
        """
        try:
            # Validate input
            self._validate_input(X)
            
            # Get raw predictions
            predictions = self.model.predict(X)
            
            # Get probability distribution
            probabilities = self.model.predict_proba(X)
            
            # Decode predictions to class names
            decoded_predictions = self.label_encoder.inverse_transform(predictions)
            
            # Build result dictionary
            result = {
                'predictions': list(decoded_predictions),
                'probabilities': probabilities.tolist(),
                'confidence': float(np.max(probabilities)),
                'model_version': getattr(self.model, '__class__.__name__', 'unknown'),
            }
            
            return result
        
        except PredictionError:
            raise
        except Exception as e:
            raise PredictionError(
                f"Prediction failed: {str(e)}"
            )
    
    def predict_proba(self, X: np.ndarray) -> Dict[str, Any]:
        """
        Generate probability predictions from features.
        
        Args:
            X: numpy array of shape (n_samples, n_features)
        
        Returns:
            Dictionary with probability scores for all classes
        
        Raises:
            PredictionError: If prediction fails
        """
        try:
            self._validate_input(X)
            
            probabilities = self.model.predict_proba(X)
            class_names = self.label_encoder.classes_
            
            result = {
                'probabilities': probabilities.tolist(),
                'class_names': list(class_names),
                'n_classes': len(class_names),
            }
            
            return result
        
        except Exception as e:
            raise PredictionError(
                f"Probability prediction failed: {str(e)}"
            )
    
    def _validate_input(self, X: np.ndarray) -> None:
        """Validate input features."""
        if X is None:
            raise PredictionError("Input X is None")
        
        if not isinstance(X, np.ndarray):
            raise PredictionError(
                f"Input X must be numpy array, got {type(X)}"
            )
        
        if X.ndim != 2:
            raise PredictionError(
                f"Input X must be 2D array, got {X.ndim}D"
            )
        
        if np.isnan(X).any():
            raise PredictionError(
                "Input X contains NaN values"
            )
        
        if np.isinf(X).any():
            raise PredictionError(
                "Input X contains infinite values"
            )
