"""
ML COMPATIBILITY WRAPPER
===================================================================
Safe ML model loading with runtime version detection and graceful fallback.

Ensures app NEVER crashes due to model incompatibilities.
Provides debug info and fallback recommendation engine.
"""

import sys
import joblib
import warnings
import numpy as np
from pathlib import Path
from typing import Tuple, Optional, Dict, Any

# Suppress warnings
warnings.filterwarnings('ignore')

# ===================================================================
# VERSION DETECTION & COMPATIBILITY CHECKING
# ===================================================================

class VersionInfo:
    """Detect and store runtime version information."""
    
    @staticmethod
    def get_versions() -> Dict[str, str]:
        """Get all relevant package versions."""
        versions = {}
        
        # Core ML packages
        try:
            import sklearn
            versions['sklearn'] = sklearn.__version__
        except:
            versions['sklearn'] = "NOT_INSTALLED"
        
        try:
            import xgboost
            versions['xgboost'] = xgboost.__version__
        except:
            versions['xgboost'] = "NOT_INSTALLED"
        
        try:
            import numpy
            versions['numpy'] = numpy.__version__
        except:
            versions['numpy'] = "NOT_INSTALLED"
        
        try:
            import pandas
            versions['pandas'] = pandas.__version__
        except:
            versions['pandas'] = "NOT_INSTALLED"
        
        try:
            import joblib as jb
            versions['joblib'] = jb.__version__
        except:
            versions['joblib'] = "NOT_INSTALLED"
        
        return versions
    
    @staticmethod
    def check_compatibility(versions: Dict[str, str]) -> Tuple[bool, str]:
        """
        Check if current versions are compatible with ML stack.
        
        Returns:
            (is_compatible, message)
        """
        messages = []
        is_compatible = True
        
        # Check sklearn version (must include XGBoost classifier)
        if versions['sklearn'] == "NOT_INSTALLED":
            is_compatible = False
            messages.append("❌ scikit-learn not installed")
        elif versions['sklearn'].startswith('0.'):
            is_compatible = False
            messages.append(f"❌ scikit-learn {versions['sklearn']} too old")
        
        # Check xgboost
        if versions['xgboost'] == "NOT_INSTALLED":
            messages.append("⚠️ xgboost not installed (V2 model unavailable)")
        
        # Check numpy
        if versions['numpy'] == "NOT_INSTALLED":
            is_compatible = False
            messages.append("❌ numpy not installed")
        elif versions['numpy'].startswith('3.'):
            is_compatible = False
            messages.append(f"⚠️ numpy {versions['numpy']} may cause issues")
        
        status = "✅ Compatible" if is_compatible else "⚠️ Incompatible"
        return is_compatible, f"{status}: " + " | ".join(messages) if messages else status


# ===================================================================
# SAFE MODEL LOADER WITH GRACEFUL FALLBACK
# ===================================================================

class SafeMLLoader:
    """Load ML models with graceful error handling and fallback."""
    
    def __init__(self):
        self.model = None
        self.preprocessor = None
        self.label_encoder = None
        self.model_version = None
        self.load_status = "NOT_LOADED"
        self.load_error = None
        self.versions = VersionInfo.get_versions()
        self.is_compatible, self.compatibility_msg = VersionInfo.check_compatibility(self.versions)
    
    def load(self) -> Tuple[Optional[Any], Optional[Any], Optional[Any], str]:
        """
        Load ML model with fallback strategy.
        
        Try order:
        1. V2 (XGBoost unified container)
        2. V1 (RandomForest + preprocessor)
        3. Rule-based predictor (no ML)
        
        Returns:
            (model, preprocessor, label_encoder, version)
        """
        model_dir = Path(__file__).resolve().parent.parent / "models"
        
        # Try V2 Model (Primary)
        v2_path = model_dir / "v2_final_model.pkl"
        if v2_path.exists():
            try:
                container = joblib.load(v2_path)
                self.model = container.get('model')
                self.preprocessor = container.get('preprocessor')
                self.label_encoder = container.get('label_encoder')
                self.model_version = "V2_XGBOOST"
                self.load_status = "SUCCESS"
                return self.model, self.preprocessor, self.label_encoder, self.model_version
            except Exception as e:
                self.load_error = f"V2 load failed: {str(e)}"
        
        # Try V1 Model (Fallback)
        v1_path = model_dir / "cake_model.joblib"
        v1_preprocessor_path = model_dir / "preprocessor.joblib"
        
        if v1_path.exists() and v1_preprocessor_path.exists():
            try:
                self.model = joblib.load(v1_path)
                self.preprocessor = joblib.load(v1_preprocessor_path)
                self.model_version = "V1_FALLBACK"
                self.load_status = "FALLBACK"
                return self.model, self.preprocessor, None, self.model_version
            except Exception as e:
                self.load_error = f"V1 load failed: {str(e)}"
        
        # Fallback to rule-based predictor
        self.model_version = "RULE_BASED"
        self.load_status = "RULE_BASED"
        self.load_error = "Both V2 and V1 models unavailable"
        return None, None, None, self.model_version
    
    def get_status_dict(self) -> Dict[str, Any]:
        """Get detailed status dictionary for debugging."""
        return {
            'model_version': self.model_version,
            'load_status': self.load_status,
            'load_error': self.load_error,
            'versions': self.versions,
            'is_compatible': self.is_compatible,
            'compatibility_msg': self.compatibility_msg,
            'model_loaded': self.model is not None,
            'preprocessor_loaded': self.preprocessor is not None,
        }


# ===================================================================
# RULE-BASED FALLBACK RECOMMENDER
# ===================================================================

class RuleBasedPredictor:
    """Fallback rule-based recommendation engine when ML model unavailable."""
    
    CAKE_MENU = [
        'Chocolate Cake', 'Vanilla Cake', 'Lemon Cake',
        'Strawberry Cheesecake', 'Carrot Cake', 'Black Forest Cake',
        'Tiramisu Cake', 'Red Velvet Cake'
    ]
    
    MOOD_PREFERENCES = {
        'Happy': ['Strawberry Cheesecake', 'Vanilla Cake', 'Red Velvet Cake'],
        'Celebratory': ['Black Forest Cake', 'Strawberry Cheesecake', 'Tiramisu Cake'],
        'Tired': ['Chocolate Cake', 'Vanilla Cake', 'Carrot Cake'],
        'Stressed': ['Chocolate Cake', 'Tiramisu Cake', 'Lemon Cake'],
        'Lonely': ['Strawberry Cheesecake', 'Chocolate Cake', 'Vanilla Cake'],
    }
    
    WEATHER_PREFERENCES = {
        'Sunny': ['Lemon Cake', 'Strawberry Cheesecake', 'Vanilla Cake'],
        'Cloudy': ['Chocolate Cake', 'Vanilla Cake', 'Tiramisu Cake'],
        'Rainy': ['Chocolate Cake', 'Carrot Cake', 'Tiramisu Cake'],
        'Snowy': ['Hot Chocolate Cake', 'Vanilla Cake', 'Carrot Cake'],
        'Stormy': ['Chocolate Cake', 'Tiramisu Cake', 'Black Forest Cake'],
    }
    
    @classmethod
    def predict_proba(cls, mood: str, weather: str, **kwargs) -> np.ndarray:
        """
        Rule-based probability prediction.
        
        Returns array of class probabilities matching V2 label order.
        """
        mood_prefs = cls.MOOD_PREFERENCES.get(mood, ['Vanilla Cake', 'Chocolate Cake', 'Strawberry Cheesecake'])
        weather_prefs = cls.WEATHER_PREFERENCES.get(weather, ['Vanilla Cake', 'Chocolate Cake', 'Strawberry Cheesecake'])
        
        # Calculate scores based on preference overlap
        scores = {}
        for cake in cls.CAKE_MENU:
            mood_score = 0.8 if cake in mood_prefs else 0.3
            weather_score = 0.8 if cake in weather_prefs else 0.3
            scores[cake] = (mood_score * 0.6 + weather_score * 0.4)
        
        # Normalize to probabilities
        total = sum(scores.values())
        proba = np.array([scores.get(cake, 0.1) / total for cake in cls.CAKE_MENU])
        return proba
    
    @classmethod
    def get_feature_names(cls):
        """Returns feature names matching V2 model."""
        return cls.CAKE_MENU


# ===================================================================
# MODULE-LEVEL SINGLETON
# ===================================================================

_ml_loader = None

def get_safe_ml_loader() -> SafeMLLoader:
    """Get or create the ML loader singleton."""
    global _ml_loader
    if _ml_loader is None:
        _ml_loader = SafeMLLoader()
        _ml_loader.load()
    return _ml_loader


def get_model_and_preprocessor() -> Tuple[Optional[Any], Optional[Any], Optional[Any], str]:
    """Get model, preprocessor, and version. Handles all fallbacks internally."""
    loader = get_safe_ml_loader()
    return loader.model, loader.preprocessor, loader.label_encoder, loader.model_version


def get_ml_status() -> Dict[str, Any]:
    """Get ML system status for debugging."""
    loader = get_safe_ml_loader()
    return loader.get_status_dict()


if __name__ == "__main__":
    # Test the compatibility wrapper
    loader = SafeMLLoader()
    loader.load()
    
    print("ML Compatibility Wrapper Test")
    print("=" * 50)
    print(f"Model Version: {loader.model_version}")
    print(f"Load Status: {loader.load_status}")
    print(f"Versions: {loader.versions}")
    print(f"Compatibility: {loader.compatibility_msg}")
    print(f"Status: {loader.get_status_dict()}")
