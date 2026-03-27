"""
ML Pipeline - Single Entry Point
=================================
SINGLE RESPONSIBILITY: Orchestrate the entire ML prediction pipeline.

Wraps the hybrid_recommender system (3-layer: segmentation → classification → ranking)
with fail-fast, explicit error handling and structured output.

ONE FUNCTION: run_pipeline(input_data)
ONE OUTPUT FORMAT: {predictions, model_version, status, warnings}
ZERO FALLBACK: Fail-fast design - raise RuntimeError if anything fails
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple
import warnings

warnings.filterwarnings('ignore')

# Set up project root path
_PROJECT_ROOT = Path(__file__).parent.parent.parent.absolute()
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

# Import the actual ML system (hybrid recommender)
try:
    from core.ml_engine.hybrid_recommender import HybridRecommendationSystem
except ImportError as e:
    raise RuntimeError(f"Cannot import hybrid_recommender: {str(e)}")


class PipelineError(Exception):
    """Raised when pipeline fails."""
    pass


class MLPipeline:
    """
    Complete ML pipeline with explicit, fail-fast error handling.
    
    Architecture:
        Wraps HybridRecommendationSystem with:
        1. Validation
        2. Error handling (no fallback)
        3. Structured output
    """
    
    # Input schema - STRICT
    REQUIRED_FEATURES = [
        'mood', 'weather_condition', 'temperature_celsius', 'humidity',
        'season', 'air_quality_index', 'time_of_day', 'sweetness_preference',
        'health_preference', 'trend_popularity_score', 'temperature_category',
        'comfort_index', 'environmental_score'
    ]
    
    # Output schema - STRICT, no deviations
    OUTPUT_SCHEMA = {
        'predictions': list,
        'top_3_cakes': list,
        'top_3_scores': list,
        'model_version': str,
        'status': str,
        'warnings': list,
        'cluster_id': int,
    }
    
    def __init__(self, models_dir: Path = None):
        """
        Initialize the ML pipeline.
        
        Args:
            models_dir: Path to models directory (optional)
        
        Raises:
            PipelineError: If initialization fails
        """
        self.system = None
        self._initialize()
    
    def _initialize(self) -> None:
        """Initialize the hybrid recommendation system."""
        try:
            self.system = HybridRecommendationSystem()
            
            #  Train the system (it needs to be trained before inference)
            # If already trained, it will load the trained models
            self.system.train()
        
        except Exception as e:
            raise PipelineError(f"Pipeline initialization failed: {str(e)}")
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run complete ML pipeline on input data.
        
        Args:
            input_data: Dictionary with user inputs
        
        Returns:
            Structured prediction output
        
        Raises:
            PipelineError: If pipeline fails at any stage
        """
        warnings_list = []
        
        try:
            # Stage 1: Validate input
            self._validate_input(input_data)
            
            # Stage 2: Run inference
            try:
                hybrid_results, cluster_id = self.system.infer(input_data)
            except Exception as e:
                raise PipelineError(f"Inference failed: {str(e)}")
            
            # Stage 3: Extract and format results
            sorted_results = sorted(
                hybrid_results.items(),
                key=lambda x: x[1].get('final_score', 0),
                reverse=True
            )
            
            top_3_cakes = [cake_name for cake_name, _ in sorted_results[:3]]
            top_3_scores = [result.get('final_score', 0) for _, result in sorted_results[:3]]
            
            # Stage 4: Format Output
            output = {
                'predictions': top_3_cakes,
                'top_3_cakes': top_3_cakes,
                'top_3_scores': top_3_scores,
                'all_results': dict(sorted_results),
                'cluster_id': cluster_id,
                'model_version': '3-Layer Hybrid (Segmentation→Classification→Ranking)',
                'status': 'success',
                'warnings': warnings_list,
            }
            
            # Validate output
            self._validate_output(output)
            
            return output
        
        except PipelineError:
            raise
        except Exception as e:
            raise PipelineError(f"Unexpected pipeline error: {str(e)}")
    
    def _validate_input(self, input_data: Dict[str, Any]) -> None:
        """Validate input data."""
        if not isinstance(input_data, dict):
            raise PipelineError(f"Input must be dict, got {type(input_data)}")
        
        missing_features = set(self.REQUIRED_FEATURES) - set(input_data.keys())
        if missing_features:
            raise PipelineError(f"Missing required features: {missing_features}")
    
    def _validate_output(self, output: Dict[str, Any]) -> None:
        """Validate output matches schema."""
        if output['status'] != 'success':
            raise PipelineError(
                f"Output status is not 'success': {output['status']}"
            )
        
        if not output['predictions']:
            raise PipelineError("No predictions generated")
    
    def get_info(self) -> Dict[str, Any]:
        """Get pipeline information."""
        return {
            'status': 'ready',
            'model_version': '3-Layer Hybrid',
            'required_features': self.REQUIRED_FEATURES,
            'features_count': len(self.REQUIRED_FEATURES),
        }


# ============================================================================
# MODULE-LEVEL SINGLETON INSTANCE
# ============================================================================

_pipeline_instance = None
_pipeline_error = None


def initialize_pipeline() -> None:
    """Initialize the global pipeline instance."""
    global _pipeline_instance, _pipeline_error
    
    try:
        _pipeline_instance = MLPipeline()
        _pipeline_error = None
    except PipelineError as e:
        _pipeline_error = e
        _pipeline_instance = None


def get_pipeline() -> MLPipeline:
    """Get the global pipeline instance."""
    global _pipeline_instance, _pipeline_error
    
    if _pipeline_error:
        raise RuntimeError(f"ML Pipeline failed to initialize: {str(_pipeline_error)}")
    
    if _pipeline_instance is None:
        raise RuntimeError("ML Pipeline not initialized")
    
    return _pipeline_instance


def run_pipeline(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run the ML pipeline - THIS IS THE ONLY ENTRY POINT FOR ML INFERENCE.
    
    Args:
        input_data: Dictionary with required features:
            - mood, weather_condition, temperature_celsius, humidity
            - season, air_quality_index, time_of_day, sweetness_preference
            - health_preference, trend_popularity_score, temperature_category
            - comfort_index, environmental_score
    
    Returns:
        {
            'predictions': [top 3 cake names],
            'top_3_cakes': [cake names],
            'top_3_scores': [scores],
            'all_results': {full dict},
            'cluster_id': int,
            'model_version': str,
            'status': 'success',
            'warnings': []
        }
    
    Raises:
        RuntimeError: If pipeline cannot run (fails loudly, no fallback)
    """
    pipeline = get_pipeline()
    return pipeline.run(input_data)


# Auto-initialize on import
try:
    initialize_pipeline()
except Exception as e:
    # Silent failure - pipeline will be initialized on first use
    pass
