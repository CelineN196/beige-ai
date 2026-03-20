#!/usr/bin/env python3
"""
Beige.AI Cake Recommendation API Wrapper

Provides Flask and FastAPI integration examples for the inference pipeline.
Makes it easy to deploy the model as a REST API.

Author: ML Engineering Team
Date: March 19, 2026
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.inference import predict_cake
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import json


# ============================================================================
# REQUEST/RESPONSE DATA CLASSES
# ============================================================================

@dataclass
class RecommendationRequest:
    """API request schema for cake recommendation."""
    mood: str
    weather_condition: str
    temperature_celsius: float
    humidity: float
    season: str
    air_quality_index: float
    time_of_day: str
    sweetness_preference: int
    health_preference: int
    trend_popularity_score: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for inference."""
        return asdict(self)
    
    def validate(self) -> Optional[str]:
        """Validate input constraints. Returns error message if invalid."""
        
        valid_moods = {'Celebratory', 'Happy', 'Lonely', 'Stressed', 'Tired'}
        if self.mood not in valid_moods:
            return f"Invalid mood. Must be one of: {valid_moods}"
        
        valid_weather = {'Sunny', 'Cloudy', 'Rainy', 'Snowy', 'Stormy'}
        if self.weather_condition not in valid_weather:
            return f"Invalid weather_condition. Must be one of: {valid_weather}"
        
        if not -50 <= self.temperature_celsius <= 60:
            return "temperature_celsius must be between -50 and 60"
        
        if not 0 <= self.humidity <= 100:
            return "humidity must be between 0 and 100"
        
        valid_seasons = {'Spring', 'Summer', 'Autumn', 'Winter'}
        if self.season not in valid_seasons:
            return f"Invalid season. Must be one of: {valid_seasons}"
        
        if self.air_quality_index < 0:
            return "air_quality_index must be non-negative"
        
        valid_times = {'Morning', 'Afternoon', 'Evening', 'Night'}
        if self.time_of_day not in valid_times:
            return f"Invalid time_of_day. Must be one of: {valid_times}"
        
        if not 1 <= self.sweetness_preference <= 10:
            return "sweetness_preference must be between 1 and 10"
        
        if not 1 <= self.health_preference <= 10:
            return "health_preference must be between 1 and 10"
        
        if not 0 <= self.trend_popularity_score <= 10:
            return "trend_popularity_score must be between 0 and 10"
        
        return None


@dataclass
class TopPrediction:
    """Single top prediction item."""
    cake: str
    probability: float


@dataclass
class RecommendationResponse:
    """API response schema for cake recommendation."""
    top_prediction: str
    confidence: float
    explanation: str
    top_3: list  # List[TopPrediction]
    timestamp: str = None
    input_features: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


# ============================================================================
# API WRAPPER CLASS
# ============================================================================

class CakeRecommendationAPI:
    """
    Unified API wrapper for cake recommendations.
    Handles validation, transformation, and response formatting.
    """
    
    def __init__(self):
        """Initialize API wrapper."""
        self.inference_errors = []
        self.total_predictions = 0
    
    def recommend(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main recommendation endpoint.
        
        Args:
            request_data: Dictionary with 10 user features
        
        Returns:
            Response dictionary (formatted for JSON)
        """
        try:
            # Parse request
            request = RecommendationRequest(**request_data)
            
            # Validate input
            validation_error = request.validate()
            if validation_error:
                return {
                    'status': 'error',
                    'message': validation_error,
                    'timestamp': datetime.now().isoformat()
                }
            
            # Get recommendation
            result = predict_cake(request.to_dict())
            
            # Check for inference errors
            if 'error' in result and result['error']:
                self.inference_errors.append(result['error'])
                return {
                    'status': 'error',
                    'message': f"Inference error: {result['error']}",
                    'timestamp': datetime.now().isoformat()
                }
            
            # Format response
            self.total_predictions += 1
            
            return {
                'status': 'success',
                'data': {
                    'top_prediction': result['top_prediction'],
                    'confidence': round(result['confidence'], 4),
                    'explanation': result['explanation'],
                    'top_3': [
                        {
                            'cake': item['cake'],
                            'probability': round(item['probability'], 4)
                        }
                        for item in result['top_3']
                    ]
                },
                'timestamp': datetime.now().isoformat()
            }
        
        except TypeError as e:
            return {
                'status': 'error',
                'message': f"Invalid request format: {str(e)}",
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.inference_errors.append(str(e))
            return {
                'status': 'error',
                'message': f"Unexpected error: {str(e)}",
                'timestamp': datetime.now().isoformat()
            }
    
    def health_check(self) -> Dict[str, Any]:
        """Health check endpoint."""
        return {
            'status': 'healthy',
            'service': 'Beige.AI Cake Recommendation',
            'version': '1.0',
            'total_predictions': self.total_predictions,
            'errors': len(self.inference_errors),
            'timestamp': datetime.now().isoformat()
        }


# ============================================================================
# FLASK INTEGRATION
# ============================================================================

def create_flask_app(api: Optional[CakeRecommendationAPI] = None):
    """
    Create Flask application with API endpoints.
    
    Usage:
        app = create_flask_app()
        app.run(debug=False, host='0.0.0.0', port=5000)
    
    Endpoints:
        POST /api/recommend - Get cake recommendation
        GET  /api/health    - Health check
    """
    
    from flask import Flask, request, jsonify
    
    app = Flask(__name__)
    api = api or CakeRecommendationAPI()
    
    @app.route('/api/recommend', methods=['POST'])
    def recommend():
        """
        POST endpoint for cake recommendations.
        
        Request body (JSON):
        {
            "mood": "Happy",
            "weather_condition": "Sunny",
            ...
        }
        """
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'Request body must be JSON'
            }), 400
        
        result = api.recommend(data)
        
        status_code = 200 if result.get('status') == 'success' else 400
        return jsonify(result), status_code
    
    @app.route('/api/health', methods=['GET'])
    def health():
        """Health check endpoint."""
        return jsonify(api.health_check()), 200
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'status': 'error',
            'message': 'Endpoint not found',
            'available_endpoints': [
                'POST /api/recommend',
                'GET /api/health'
            ]
        }), 404
    
    return app


# ============================================================================
# FASTAPI INTEGRATION
# ============================================================================

def create_fastapi_app(api: Optional[CakeRecommendationAPI] = None):
    """
    Create FastAPI application with API endpoints.
    
    Usage:
        from fastapi import FastAPI
        app = create_fastapi_app()
        # Run with: uvicorn backend.api:app --reload
    
    Endpoints:
        POST /api/recommend - Get cake recommendation
        GET  /api/health    - Health check
    """
    
    try:
        from fastapi import FastAPI
    except ImportError:
        raise ImportError(
            "FastAPI not installed. Install with: pip install fastapi uvicorn"
        )
    
    app = FastAPI(
        title="Beige.AI Cake Recommendation API",
        description="Real-time cake recommendations based on user preferences",
        version="1.0"
    )
    
    api = api or CakeRecommendationAPI()
    
    @app.post("/api/recommend")
    async def recommend(request_data: Dict[str, Any]):
        """
        POST endpoint for cake recommendations.
        
        Request body (JSON):
        ```json
        {
            "mood": "Happy",
            "weather_condition": "Sunny",
            "temperature_celsius": 25.0,
            "humidity": 50.0,
            "season": "Summer",
            "air_quality_index": 40,
            "time_of_day": "Afternoon",
            "sweetness_preference": 5,
            "health_preference": 7,
            "trend_popularity_score": 8.0
        }
        ```
        """
        result = api.recommend(request_data)
        
        if result.get('status') == 'error':
            from fastapi import HTTPException
            raise HTTPException(
                status_code=400,
                detail=result.get('message')
            )
        
        return result
    
    @app.get("/api/health")
    async def health():
        """Health check endpoint."""
        return api.health_check()
    
    return app


# ============================================================================
# TESTING & EXAMPLES
# ============================================================================

def test_api_wrapper():
    """Test API wrapper with example requests."""
    
    api = CakeRecommendationAPI()
    
    test_cases = [
        {
            'name': 'Happy Summer Day',
            'input': {
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
        },
        {
            'name': 'Stressed Winter Night',
            'input': {
                'mood': 'Stressed',
                'weather_condition': 'Snowy',
                'temperature_celsius': -5.0,
                'humidity': 70.0,
                'season': 'Winter',
                'air_quality_index': 55,
                'time_of_day': 'Night',
                'sweetness_preference': 7,
                'health_preference': 4,
                'trend_popularity_score': 7.0
            }
        },
        {
            'name': 'Invalid input (bad mood)',
            'input': {
                'mood': 'INVALID',
                'weather_condition': 'Sunny',
                'temperature_celsius': 25.0,
                'humidity': 50.0,
                'season': 'Summer',
                'air_quality_index': 40,
                'time_of_day': 'Afternoon',
                'sweetness_preference': 5,
                'health_preference': 7,
                'trend_popularity_score': 8.0
            }
        }
    ]
    
    print("\n" + "="*80)
    print("🍰 API WRAPPER TEST SUITE")
    print("="*80)
    
    for test in test_cases:
        print(f"\n📌 Test: {test['name']}")
        print(f"{'─'*80}")
        
        result = api.recommend(test['input'])
        
        if result.get('status') == 'success':
            data = result['data']
            print(f"✅ Recommendation: {data['top_prediction']}")
            print(f"   Confidence: {data['confidence']*100:.1f}%")
            print(f"   Top 3: {[item['cake'] for item in data['top_3']]}")
        else:
            print(f"❌ Error: {result.get('message')}")
    
    print(f"\n{'='*80}")
    print(f"📊 Summary:")
    print(f"   Total Predictions: {api.total_predictions}")
    print(f"   Errors: {len(api.inference_errors)}")
    print(f"\n{'='*80}\n")


if __name__ == "__main__":
    test_api_wrapper()
