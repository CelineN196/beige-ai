"""
Model Loader - Explicit, Fail-Fast Model Loading
==================================================
SINGLE RESPONSIBILITY: Validate production model registry.

NO FALLBACK LOGIC - If anything fails, raise RuntimeError immediately.

CRITICAL: This module validates that ALL required production models exist
before the app attempts to load them.
"""

import joblib
import pickle
import os
from pathlib import Path
from typing import Tuple, Any
import warnings

warnings.filterwarnings('ignore')

# ============================================================================
# PRODUCTION MODEL REGISTRY
# ============================================================================
# These are the ONLY models used in production
# Fail-fast if any are missing

REQUIRED_PRODUCTION_FILES = {
    "models/production/kmeans_model.pkl": "K-Means segmentation model",
    "models/production/kmeans_scaler.pkl": "K-Means feature scaler",
    "models/production/classifier_model.pkl": "Random Forest classifier",
    "models/production/classifier_encoder.pkl": "Classifier label encoder",
    "models/production/classifier_scaler.pkl": "Classifier feature scaler",
    "models/production/cluster_stats.pkl": "Ranking layer cluster statistics",
}


class ModelLoadError(Exception):
    """Raised when model loading fails."""
    pass


class ModelLoader:
    """
    Production Model Registry Validator
    
    CRITICAL RESPONSIBILITY: Validate that ALL required production models exist
    before the ML engine attempts to load them.
    
    NO FALLBACK: Fails immediately if any required file is missing.
    """
    
    def __init__(self, project_root: Path = None):
        """
        Initialize the model loader.
        
        Args:
            project_root: Path to project root (auto-detected if None)
        
        Raises:
            ModelLoadError: If initialization fails
        """
        if project_root is None:
            # Auto-detect project root from this file's location
            # This file is at core/ml_engine/model_loader.py
            project_root = Path(__file__).resolve().parent.parent.parent
        
        self.project_root = project_root
        self.production_models_dir = project_root / "models" / "production"
        self.is_validated = False
    
    def validate_production_registry(self) -> dict:
        """
        CRITICAL: Validate that ALL required production models exist.
        
        Fails immediately if ANY file is missing.
        
        Returns:
            Dictionary with validation results
        
        Raises:
            ModelLoadError: If any required file is missing
        """
        missing_files = []
        found_files = []
        
        # Check each required file
        for relative_path, description in REQUIRED_PRODUCTION_FILES.items():
            full_path = self.project_root / relative_path
            
            if full_path.exists():
                found_files.append({
                    'path': relative_path,
                    'description': description,
                    'status': 'FOUND'
                })
            else:
                missing_files.append({
                    'path': relative_path,
                    'description': description,
                    'status': 'MISSING',
                    'full_path': str(full_path)
                })
        
        # If ANY files are missing, fail immediately
        if missing_files:
            error_lines = [
                "CRITICAL: Production model registry validation FAILED",
                f"Missing {len(missing_files)} required file(s):",
                ""
            ]
            for item in missing_files:
                error_lines.append(f"  ❌ {item['path']}")
                error_lines.append(f"     Description: {item['description']}")
                error_lines.append(f"     Expected at: {item['full_path']}")
            
            error_lines.extend([
                "",
                "All production models must be in: models/production/",
                "Do NOT load from legacy/ or other locations.",
                "",
                "To recover:",
                "1. Check that models/production/ contains exactly these files:",
                "   - kmeans_model.pkl",
                "   - kmeans_scaler.pkl",
                "   - classifier_model.pkl",
                "   - classifier_encoder.pkl",
                "   - classifier_scaler.pkl",
                "   - cluster_stats.pkl",
                "2. Re-train the model if files are corrupted",
                "3. Do NOT use legacy models from models/legacy/",
            ])
            
            raise ModelLoadError("\n".join(error_lines))
        
        # All files found - log status
        self.is_validated = True
        
        return {
            'status': 'VALID',
            'found_count': len(found_files),
            'missing_count': 0,
            'found_files': found_files,
            'production_models_dir': str(self.production_models_dir),
        }
    
    def get_production_models_dir(self) -> Path:
        """Get the production models directory."""
        if not self.is_validated:
            self.validate_production_registry()
        
        return self.production_models_dir
    
    def get_status(self) -> dict:
        """Get current loader status."""
        return {
            'is_validated': self.is_validated,
            'project_root': str(self.project_root),
            'production_models_dir': str(self.production_models_dir),
            'registry_required_files': len(REQUIRED_PRODUCTION_FILES),
        }
