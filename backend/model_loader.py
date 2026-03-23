"""
PRODUCTION MODEL LOADER
===================================================================
Safe, deterministic model loading with fallback and version tracking.

Responsibilities:
1. Load V2 model with all components (model + preprocessor + encoder)
2. Fallback to V1 if V2 loading fails
3. Track which model is active
4. Log version information for debugging
5. Validate model integrity
"""

import sys
import joblib
import warnings
from pathlib import Path
from typing import Tuple, Optional, Dict, Any

# Suppress warnings during loading
warnings.filterwarnings('ignore')

# ===================================================================
# CONSTANTS
# ===================================================================

# Relative paths from package root
MODEL_DIR = Path(__file__).resolve().parent.parent / "models"

V2_PRIMARY_MODEL = MODEL_DIR / "model.pkl"
V1_FALLBACK_MODEL = MODEL_DIR / "cake_model.joblib"
V1_FALLBACK_PREPROCESSOR = MODEL_DIR / "preprocessor.joblib"

# Version info for tracking
EXPECTED_V2_ENV = {
    'sklearn_version': '1.5.1',
    'xgboost_version': '2.0.3',
    'numpy_version': '1.24.3',
    'pandas_version': '2.0.3',
    'joblib_version': '1.3.2'
}

# ===================================================================
# MODEL LOADING CLASS (PRODUCTION-SAFE)
# ===================================================================

class ModelLoader:
    """Safe model loading with fallback and version tracking."""
    
    def __init__(self, verbose: bool = True):
        """Initialize loader.
        
        Args:
            verbose: Print debug information
        """
        self.verbose = verbose
        self.model = None
        self.preprocessor = None
        self.label_encoder = None
        self.model_version = None
        self.model_type = None
        self.training_env = None
        self._load_status = None
    
    def load(self) -> Tuple[Any, str]:
        """Load model with fallback strategy.
        
        Returns:
            (model, version) where version is "V2" or "V1"
            
        Raises:
            RuntimeError: If no model can be loaded
        """
        try:
            return self._load_v2()
        except Exception as e:
            if self.verbose:
                print(f"⚠️  V2 load failed: {str(e)[:100]}")
            
            try:
                return self._load_v1()
            except Exception as e:
                raise RuntimeError(
                    f"❌ FATAL: Cannot load any model.\n"
                    f"V2 error: {str(e)}\n"
                    f"V1 path exists: {V1_FALLBACK_MODEL.exists()}"
                )
    
    def load_preprocessor(self) -> Tuple[Any, str]:
        """Load preprocessor with fallback.
        
        Returns:
            (preprocessor, version) where version is "V2" or "V1"
        """
        try:
            return self._load_v2_preprocessor()
        except Exception as e:
            if self.verbose:
                print(f"⚠️  V2 preprocessor load failed: {str(e)[:100]}")
            
            try:
                return self._load_v1_preprocessor()
            except Exception as e:
                raise RuntimeError(f"Cannot load preprocessor: {str(e)}")
    
    def load_label_encoder(self) -> Optional[Any]:
        """Load label encoder if available.
        
        Returns:
            Label encoder or None if not available
        """
        try:
            if V2_PRIMARY_MODEL.exists():
                unified = joblib.load(V2_PRIMARY_MODEL)
                encoder = unified.get('label_encoder')
                if encoder and self.verbose:
                    print(f"✓ Label encoder loaded from V2")
                return encoder
        except Exception:
            pass
        
        if self.verbose:
            print("⚠️  Label encoder not available, will use indices")
        return None
    
    # ===================================================================
    # PRIVATE METHODS
    # ===================================================================
    
    def _load_v2(self) -> Tuple[Any, str]:
        """Load V2 unified model.
        
        V2 uses XGBoost with sklearn 1.5.1 and includes:
        - model (XGBClassifier)
        - preprocessor (ColumnTransformer)
        - label_encoder (LabelEncoder)
        - feature_names (list)
        - training_env (dict with version info)
        """
        if not V2_PRIMARY_MODEL.exists():
            raise FileNotFoundError(f"V2 model not found: {V2_PRIMARY_MODEL}")
        
        unified = joblib.load(V2_PRIMARY_MODEL)
        model = unified.get('model')
        
        if model is None:
            raise ValueError("V2 model file missing 'model' key")
        
        self.model = model
        self.preprocessor = unified.get('preprocessor')
        self.label_encoder = unified.get('label_encoder')
        self.training_env = unified.get('training_env', {})
        self.model_version = "V2"
        self.model_type = model.__class__.__name__
        self._load_status = "✓ V2 loaded (XGBoost)"
        
        if self.verbose:
            print(f"✓ V2 model loaded: {self.model_type}")
            if self.training_env:
                print(f"  Training: sklearn {self.training_env.get('sklearn_version')}, "
                      f"xgboost {self.training_env.get('xgboost_version')}")
        
        return self.model, "V2"
    
    def _load_v1(self) -> Tuple[Any, str]:
        """Load V1 fallback model (RandomForest).
        
        V1 uses scikit-learn RandomForest for safety/compatibility.
        """
        if not V1_FALLBACK_MODEL.exists():
            raise FileNotFoundError(f"V1 model not found: {V1_FALLBACK_MODEL}")
        
        model = joblib.load(V1_FALLBACK_MODEL)
        self.model = model
        self.model_version = "V1"
        self.model_type = model.__class__.__name__
        self._load_status = "ℹ️  V1 fallback loaded (RandomForest)"
        
        if self.verbose:
            print(f"ℹ️  V1 fallback loaded: {self.model_type}")
        
        return self.model, "V1"
    
    def _load_v2_preprocessor(self) -> Tuple[Any, str]:
        """Load preprocessor from V2 unified model."""
        if not V2_PRIMARY_MODEL.exists():
            raise FileNotFoundError(f"V2 model not found: {V2_PRIMARY_MODEL}")
        
        unified = joblib.load(V2_PRIMARY_MODEL)
        preprocessor = unified.get('preprocessor')
        
        if preprocessor is None:
            raise ValueError("V2 model missing 'preprocessor' key")
        
        if self.verbose:
            print(f"✓ V2 preprocessor loaded")
        
        return preprocessor, "V2"
    
    def _load_v1_preprocessor(self) -> Tuple[Any, str]:
        """Load preprocessor from V1."""
        if not V1_FALLBACK_PREPROCESSOR.exists():
            raise FileNotFoundError(f"V1 preprocessor not found: {V1_FALLBACK_PREPROCESSOR}")
        
        preprocessor = joblib.load(V1_FALLBACK_PREPROCESSOR)
        
        if self.verbose:
            print(f"ℹ️  V1 preprocessor loaded")
        
        return preprocessor, "V1"
    
    def get_status_report(self) -> Dict[str, Any]:
        """Get detailed status report for debugging.
        
        Returns:
            Dictionary with loading status and metadata
        """
        return {
            'status': self._load_status or "Not loaded",
            'model_version': self.model_version,
            'model_type': self.model_type,
            'training_env': self.training_env,
            'has_preprocessor': self.preprocessor is not None,
            'has_label_encoder': self.label_encoder is not None,
            'v2_path_exists': V2_PRIMARY_MODEL.exists(),
            'v1_path_exists': V1_FALLBACK_MODEL.exists(),
        }


# ===================================================================
# SINGLETON INSTANCE (STREAMLIT SAFE)
# ===================================================================

_loader_instance: Optional[ModelLoader] = None

def get_model_loader(verbose: bool = True) -> ModelLoader:
    """Get or create model loader (singleton for efficiency).
    
    Args:
        verbose: Print debug info
        
    Returns:
        ModelLoader instance
    """
    global _loader_instance
    if _loader_instance is None:
        _loader_instance = ModelLoader(verbose=verbose)
    return _loader_instance

# ===================================================================
# CONVENIENCE FUNCTIONS (FOR STREAMLIT APP)
# ===================================================================

def load_model_and_preprocessor_safe(verbose: bool = True) -> Tuple[Any, Any, str]:
    """Load model and preprocessor together safely.
    
    This is the main entry point for the Streamlit app.
    
    Args:
        verbose: Print debug info
        
    Returns:
        (model, preprocessor, version) where version is "V2" or "V1"
        
    Raises:
        RuntimeError: If nothing can be loaded
    """
    loader = get_model_loader(verbose=verbose)
    model, model_version = loader.load()
    preprocessor, _ = loader.load_preprocessor()
    
    return model, preprocessor, model_version

def load_label_encoder_safe() -> Optional[Any]:
    """Load label encoder if available.
    
    Returns:
        LabelEncoder or None
    """
    loader = get_model_loader(verbose=False)
    return loader.load_label_encoder()

def get_model_status() -> Dict[str, Any]:
    """Get detailed model loading status.
    
    Returns:
        Status dictionary
    """
    loader = get_model_loader(verbose=False)
    return loader.get_status_report()

# ===================================================================
# DEBUG UTILITIES
# ===================================================================

def print_model_diagnostics():
    """Print diagnostic information for debugging."""
    print("\n" + "="*70)
    print("MODEL LOADING DIAGNOSTICS")
    print("="*70)
    
    # Check file existence
    print("\nFile Status:")
    print(f"  V2 model: {V2_PRIMARY_MODEL.exists()} ({V2_PRIMARY_MODEL})")
    print(f"  V1 model: {V1_FALLBACK_MODEL.exists()} ({V1_FALLBACK_MODEL})")
    print(f"  V1 preprocessor: {V1_FALLBACK_PREPROCESSOR.exists()} ({V1_FALLBACK_PREPROCESSOR})")
    
    # Try loading
    print("\nLoading Status:")
    try:
        loader = ModelLoader(verbose=True)
        model, version = loader.load()
        print(f"  Version: {version}")
        print(f"  Type: {model.__class__.__name__}")
        
        preprocessor, _ = loader.load_preprocessor()
        print(f"  Preprocessor: {preprocessor.__class__.__name__}")
        
        encoder = loader.load_label_encoder()
        print(f"  Label encoder: {encoder is not None}")
        
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
    
    print("="*70 + "\n")

if __name__ == "__main__":
    print_model_diagnostics()
