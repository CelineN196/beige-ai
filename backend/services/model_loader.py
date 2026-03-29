"""
PRODUCTION MODEL LOADER - FAIL-FAST ONLY
===================================================================
Direct, deterministic model loading with ZERO fallback logic.

Responsibilities:
1. Load V2 unified model (model + preprocessor + encoder)
2. Fail loudly and immediately if loading fails
3. No fallback to old models
4. Log version information for debugging

DESIGN PRINCIPLE:
If the ML system is unavailable, the app CRASHES.
There is NO silent fallback to rule-based predictions.
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

# V2 Unified Model (ONLY MODEL USED)
V2_PRIMARY_MODEL = MODEL_DIR / "v2_final_model.pkl"

# Version info for tracking
EXPECTED_V2_ENV = {
    'sklearn_version': '1.5.1',
    'xgboost_version': '2.0.3',
    'numpy_version': '1.24.3',
    'pandas_version': '2.0.3',
    'joblib_version': '1.3.2'
}

# ===================================================================
# MODEL LOADING CLASS (FAIL-FAST ONLY)
# ===================================================================

class ModelLoader:
    """Load V2 model with explicit error handling. NO FALLBACK."""
    
    def __init__(self, verbose: bool = True):
        """Initialize loader.
        
        Args:
            verbose: Print debug information
        """
        self.verbose = verbose
        self.model = None
        self.preprocessor = None
        self.label_encoder = None
        self.model_version = "V2"
        self.model_type = None
        self.training_env = None
        self._load_status = None
    
    def load(self) -> Tuple[Any, str]:
        """Load V2 model. NO FALLBACK - fails hard if not available.
        
        Returns:
            (model, version) where version is always "V2"
            
        Raises:
            RuntimeError: If V2 model cannot be loaded
        """
        return self._load_v2()
    
    def load_preprocessor(self) -> Tuple[Any, str]:
        """Load preprocessor from V2 unified model. NO FALLBACK.
        
        Returns:
            (preprocessor, version) where version is always "V2"
            
        Raises:
            RuntimeError: If preprocessor cannot be loaded
        """
        return self._load_v2_preprocessor()
    
    def load_label_encoder(self) -> Optional[Any]:
        """Load label encoder if available from V2.
        
        Returns:
            Label encoder or None if not available
            
        Raises:
            RuntimeError: If V2 model file cannot be loaded
        """
        if not V2_PRIMARY_MODEL.exists():
            raise RuntimeError(
                f"❌ FATAL: V2 model not found at {V2_PRIMARY_MODEL}\n"
                f"Cannot load label encoder without model."
            )
        
        try:
            unified = joblib.load(V2_PRIMARY_MODEL)
            encoder = unified.get('label_encoder')
            if encoder and self.verbose:
                print(f"✓ Label encoder loaded from V2")
            return encoder
        except Exception as e:
            raise RuntimeError(
                f"❌ FATAL: Cannot load V2 model for label encoder: {str(e)}"
            )
    
    # ===================================================================
    # PRIVATE METHODS - V2 ONLY
    # ===================================================================
    
    def _load_v2(self) -> Tuple[Any, str]:
        """Load V2 unified model. HARD FAIL if not available.
        
        V2 uses XGBoost with sklearn 1.5.1 and includes:
        - model (XGBClassifier)
        - preprocessor (ColumnTransformer)
        - label_encoder (LabelEncoder)
        - feature_names (list)
        - training_env (dict with version info)
        
        Raises:
            RuntimeError: If model cannot be loaded
        """
        if not V2_PRIMARY_MODEL.exists():
            raise RuntimeError(
                f"❌ FATAL: V2 model file not found at {V2_PRIMARY_MODEL}\n"
                f"The ML system is unavailable. Cannot proceed."
            )
        
        try:
            unified = joblib.load(V2_PRIMARY_MODEL)
        except Exception as e:
            raise RuntimeError(
                f"❌ FATAL: Cannot deserialize V2 model at {V2_PRIMARY_MODEL}\n"
                f"Error: {str(e)}\n"
                f"The ML system is broken. Cannot proceed."
            )
        
        model = unified.get('model')
        
        if model is None:
            raise RuntimeError(
                f"❌ FATAL: V2 model file missing 'model' key.\n"
                f"File is corrupted or incomplete."
            )
        
        self.model = model
        self.preprocessor = unified.get('preprocessor')
        self.label_encoder = unified.get('label_encoder')
        self.training_env = unified.get('training_env', {})
        self.model_version = "V2"
        self.model_type = model.__class__.__name__
        self._load_status = "✓ V2 loaded successfully (XGBoost)"
        
        if self.verbose:
            print(f"✓ V2 model loaded: {self.model_type}")
            if self.training_env:
                print(f"  Training: sklearn {self.training_env.get('sklearn_version')}, "
                      f"xgboost {self.training_env.get('xgboost_version')}")
        
        return self.model, "V2"
    
    def _load_v2_preprocessor(self) -> Tuple[Any, str]:
        """Load preprocessor from V2 unified model. HARD FAIL if not available.
        
        Raises:
            RuntimeError: If preprocessor cannot be loaded
        """
        if not V2_PRIMARY_MODEL.exists():
            raise RuntimeError(
                f"❌ FATAL: V2 model not found at {V2_PRIMARY_MODEL}\n"
                f"Cannot load preprocessor without model."
            )
        
        try:
            unified = joblib.load(V2_PRIMARY_MODEL)
        except Exception as e:
            raise RuntimeError(
                f"❌ FATAL: Cannot deserialize V2 model for preprocessor: {str(e)}"
            )
        
        preprocessor = unified.get('preprocessor')
        
        if preprocessor is None:
            raise RuntimeError(
                f"❌ FATAL: V2 model missing 'preprocessor' key.\n"
                f"File is corrupted or incomplete."
            )
        
        if self.verbose:
            print(f"✓ V2 preprocessor loaded")
        
        return preprocessor, "V2"
    
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
# CONVENIENCE FUNCTIONS (FOR STREAMLIT APP) - FAIL-FAST ONLY
# ===================================================================

def load_model_and_preprocessor_safe(verbose: bool = True) -> Tuple[Any, Any, str]:
    """Load model and preprocessor together. NO FALLBACK - hard fails if not available.
    
    This is the main entry point for the Streamlit app.
    If the ML system is not available, crashes hard with clear error.
    
    Args:
        verbose: Print debug info
        
    Returns:
        (model, preprocessor, version) where version is always "V2"
        
    Raises:
        RuntimeError: If V2 model cannot be loaded
    """
    loader = get_model_loader(verbose=verbose)
    model, model_version = loader.load()
    preprocessor, _ = loader.load_preprocessor()
    
    return model, preprocessor, model_version

def load_label_encoder_safe() -> Optional[Any]:
    """Load label encoder from V2 if available.
    
    Returns:
        LabelEncoder or None if not available
        
    Raises:
        RuntimeError: If V2 model cannot be loaded
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
# DEBUG UTILITIES - V2 ONLY
# ===================================================================

def print_model_diagnostics():
    """Print diagnostic information for debugging."""
    print("\n" + "="*70)
    print("MODEL LOADING DIAGNOSTICS - V2 ONLY")
    print("="*70)
    
    # Check file existence
    print("\nFile Status:")
    print(f"  V2 model: {V2_PRIMARY_MODEL.exists()} ({V2_PRIMARY_MODEL})")
    
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
        
    except RuntimeError as e:
        print(f"  ❌ FATAL ERROR: {str(e)}")
    
    print("="*70 + "\n")

if __name__ == "__main__":
    print_model_diagnostics()
