# Model Usage Guide

How to load, use, and integrate the trained model into your application.

---

## 🚀 Quick Usage

### Basic Prediction

```python
import joblib
import numpy as np

# Load the model and metadata
model = joblib.load('backend/models/best_model.joblib')
metadata = joblib.load('backend/models/feature_info.joblib')

# Prepare your features (must match training format!)
# This is a 1D array of features in the same order as training
features = np.array([[2, 15.5, 45, 60, 3, 2, 1, 7, ...]])

# Make prediction
prediction = model.predict(features)
probabilities = model.predict_proba(features)

# Get results
predicted_class_idx = prediction[0]
predicted_class_name = metadata['target_classes'][predicted_class_idx]
confidence = probabilities[0][predicted_class_idx]

print(f"Prediction: {predicted_class_name}")
print(f"Confidence: {confidence:.2%}")
```

---

## 📋 Feature Requirements

Your input features **MUST** match the training data exactly:

### Feature Order & Format

```python
metadata = joblib.load('backend/models/feature_info.joblib')
feature_names = metadata['features']
target_classes = metadata['target_classes']

print(f"Required features: {feature_names}")
print(f"Expected classes: {target_classes}")

# Output example:
# Required features: ['mood_happy', 'mood_sad', 'weather_sunny', ..., 'humidity', ...]
# Expected classes: ['Chocolate Cake', 'Vanilla Cake', 'Red Velvet Cake', ...]
```

### Feature Format Details

**Important:** The features must be preprocessed the **exact same way** as training:

1. **Categorical features** → One-Hot Encoded
2. **Numerical features** → StandardScaler normalized
3. **Order** → Must match original training order
4. **Data type** → numpy array or list of floats

---

## 🔄 Complete Production Example

```python
import joblib
import numpy as np
from typing import Dict, Tuple, List

class CakeRecommender:
    """Production-ready cake recommendation system"""
    
    def __init__(self, model_path: str, metadata_path: str):
        """Initialize with trained model"""
        self.model = joblib.load(model_path)
        self.metadata = joblib.load(metadata_path)
        self.feature_names = self.metadata['features']
        self.class_names = self.metadata['target_classes']
    
    def prepare_features(self, raw_data: Dict) -> np.ndarray:
        """
        Convert raw user input to feature array
        
        Args:
            raw_data: {
                'mood': 'happy',
                'weather': 'sunny',
                'temperature': 25.5,
                'humidity': 60,
                ...
            }
        
        Returns:
            Feature array ready for prediction
        """
        # This should match your training preprocessing pipeline
        features = []
        
        # Example categorical encoding
        mood_map = {'happy': [1, 0, 0], 'sad': [0, 1, 0], 'neutral': [0, 0, 1]}
        features.extend(mood_map.get(raw_data['mood'], [0, 0, 0]))
        
        # Example numerical normalization (must use training mean/std!)
        temperature_normalized = (raw_data['temperature'] - 15.0) / 10.0
        features.append(temperature_normalized)
        
        # Add more features...
        
        return np.array([features])
    
    def predict(self, raw_data: Dict) -> Dict:
        """
        Make a recommendation
        
        Args:
            raw_data: Raw user input
        
        Returns:
            {
                'recommendation': 'Chocolate Cake',
                'confidence': 0.95,
                'all_predictions': {
                    'Chocolate Cake': 0.95,
                    'Vanilla Cake': 0.04,
                    'Red Velvet Cake': 0.01
                }
            }
        """
        try:
            # Prepare features
            features = self.prepare_features(raw_data)
            
            # Make prediction
            prediction_idx = self.model.predict(features)[0]
            probabilities = self.model.predict_proba(features)[0]
            
            # Format output
            recommended_cake = self.class_names[prediction_idx]
            confidence = probabilities[prediction_idx]
            
            # All predictions with confidence scores
            all_predictions = {
                cake: float(prob)
                for cake, prob in zip(self.class_names, probabilities)
            }
            
            return {
                'success': True,
                'recommendation': recommended_cake,
                'confidence': float(confidence),
                'all_scores': all_predictions,
                'input': raw_data
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

# Usage
recommender = CakeRecommender(
    'backend/models/best_model.joblib',
    'backend/models/feature_info.joblib'
)

user_input = {
    'mood': 'happy',
    'temperature': 25.5,
    'humidity': 60,
    'weather': 'sunny'
    # ... more features
}

result = recommender.predict(user_input)
print(f"🍰 Recommended: {result['recommendation']}")
print(f"   Confidence: {result['confidence']:.1%}")
```

---

## 🌐 Flask API Integration

```python
from flask import Flask, request, jsonify
import joblib
import numpy as np

app = Flask(__name__)

# Load model once at startup
model = joblib.load('backend/models/best_model.joblib')
metadata = joblib.load('backend/models/feature_info.joblib')

@app.route('/api/recommend', methods=['POST'])
def recommend_cake():
    """
    API endpoint for cake recommendations
    
    Request body:
    {
        "mood": "happy",
        "temperature": 25.5,
        "humidity": 60,
        ...
    }
    
    Response:
    {
        "success": true,
        "recommendation": "Chocolate Cake",
        "confidence": 0.95,
        "scores": {...}
    }
    """
    try:
        # Get input data
        data = request.get_json()
        
        # Validate required fields
        required = ['mood', 'temperature', 'humidity']
        if not all(field in data for field in required):
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {required}'
            }), 400
        
        # Preprocess features (must match training preprocessing!)
        features = np.array([[
            data['temperature'],
            data['humidity'],
            # ... process other features
        ]])
        
        # Make prediction
        prediction = model.predict(features)[0]
        probabilities = model.predict_proba(features)[0]
        
        # Format response
        return jsonify({
            'success': True,
            'recommendation': metadata['target_classes'][prediction],
            'confidence': float(probabilities[prediction]),
            'scores': {
                cake: float(prob)
                for cake, prob in zip(metadata['target_classes'], probabilities)
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/model-info', methods=['GET'])
def model_info():
    """Get model information and feature requirements"""
    return jsonify({
        'model_type': metadata['model_type'],
        'classes': metadata['target_classes'],
        'n_features': len(metadata['features']),
        'features': metadata['features']
    })

if __name__ == '__main__':
    app.run(debug=False, port=5000)
```

### Test the API

```bash
# Make a prediction
curl -X POST http://localhost:5000/api/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "mood": "happy",
    "temperature": 25.5,
    "humidity": 60
  }'

# Get model info
curl http://localhost:5000/api/model-info
```

---

## 🔧 Feature Preprocessing Template

You **must** use the exact same preprocessing as training:

```python
import numpy as np
from sklearn.preprocessing import StandardScaler, OneHotEncoder

def preprocess_single_sample(raw_data: dict) -> np.ndarray:
    """
    Preprocess a single sample for prediction
    
    IMPORTANT: Use the SAME preprocessing as training!
    
    Args:
        raw_data: Dict with raw feature values
    
    Returns:
        Preprocessed feature array
    """
    features = []
    
    # 1. CATEGORICAL FEATURES (One-Hot Encoded)
    # ==========================================
    
    # Mood: happy=1,0,0 | sad=0,1,0 | neutral=0,0,1
    mood_encoding = {
        'happy': [1, 0, 0],
        'sad': [0, 1, 0],
        'neutral': [0, 0, 1]
    }
    mood = raw_data.get('mood', 'neutral')
    features.extend(mood_encoding.get(mood, [0, 0, 1]))
    
    # Weather: sunny, rainy, cloudy
    weather_encoding = {
        'sunny': [1, 0, 0],
        'rainy': [0, 1, 0],
        'cloudy': [0, 0, 1]
    }
    weather = raw_data.get('weather', 'sunny')
    features.extend(weather_encoding.get(weather, [1, 0, 0]))
    
    # ... other categorical features ...
    
    # 2. NUMERICAL FEATURES (StandardScaler normalized)
    # ==================================================
    # Use the SAME mean and std from training data!
    
    # Temperature (training mean=20.0, std=10.0)
    temp = raw_data.get('temperature', 20.0)
    temp_normalized = (temp - 20.0) / 10.0
    features.append(temp_normalized)
    
    # Humidity (training mean=60.0, std=20.0)
    humidity = raw_data.get('humidity', 60.0)
    humidity_normalized = (humidity - 60.0) / 20.0
    features.append(humidity_normalized)
    
    # ... other numerical features ...
    
    return np.array([features])
```

---

## ⚠️ Common Mistakes

### ❌ Mistake 1: Wrong Feature Order

```python
# WRONG - Features in different order
features = [temperature, humidity, mood]

# CORRECT - Must match training order exactly
features = [mood_encoded, weather_encoded, temperature_norm, humidity_norm, ...]
```

### ❌ Mistake 2: Forgetting to Normalize

```python
# WRONG - Raw temperature value
features.append(25.5)

# CORRECT - Normalized using training mean/std
features.append((25.5 - 20.0) / 10.0)
```

### ❌ Mistake 3: One-Hot Encoding Error

```python
# WRONG - String category
features.append("happy")

# CORRECT - One-hot encoded
features.extend([1, 0, 0])  # happy
```

### ❌ Mistake 4: Wrong Array Shape

```python
# WRONG - Missing outer array
features = [1, 0, 0, 25.5, 60]
prediction = model.predict(features)  # Error!

# CORRECT - 2D array (batch of 1)
features = np.array([[1, 0, 0, 25.5, 60]])
prediction = model.predict(features)  # Works!
```

---

## 🧪 Testing Your Integration

```python
def test_model_integration():
    """Test the model integration"""
    import joblib
    import numpy as np
    
    # Load model
    model = joblib.load('backend/models/best_model.joblib')
    metadata = joblib.load('backend/models/feature_info.joblib')
    
    # Create test data (must match feature count!)
    n_features = len(metadata['features'])
    test_features = np.random.randn(1, n_features)
    
    # Test prediction
    prediction = model.predict(test_features)
    probabilities = model.predict_proba(test_features)
    
    # Verify outputs
    assert prediction.shape == (1,), "Prediction shape wrong"
    assert probabilities.shape == (1, len(metadata['target_classes'])), \
        "Probabilities shape wrong"
    assert 0 <= prediction[0] < len(metadata['target_classes']), \
        "Invalid class index"
    assert np.isclose(probabilities[0].sum(), 1.0), \
        "Probabilities don't sum to 1"
    
    print("✅ Model integration test passed!")
    print(f"   Prediction: {metadata['target_classes'][prediction[0]]}")
    print(f"   Confidence: {probabilities[0].max():.2%}")

test_model_integration()
```

---

## 📊 Interpreting Model Outputs

### Understanding Probabilities

```python
# Model outputs probabilities for each class
probabilities = model.predict_proba(features)[0]
# Result: [0.85, 0.10, 0.05] for 3 classes

# Convert to readable format
for cake, prob in zip(metadata['target_classes'], probabilities):
    confidence = int(prob * 100)
    bar = '█' * (confidence // 5) + '░' * (20 - confidence // 5)
    print(f"{cake:20} {bar} {confidence}%")

# Output:
# Chocolate Cake      ████████████████░░░░ 85%
# Vanilla Cake        ██░░░░░░░░░░░░░░░░░░ 10%
# Red Velvet Cake     █░░░░░░░░░░░░░░░░░░░  5%
```

### Confidence Thresholds

```python
# Set minimum confidence threshold
MIN_CONFIDENCE = 0.70

prediction_idx = model.predict(features)[0]
confidence = model.predict_proba(features)[0][prediction_idx]

if confidence >= MIN_CONFIDENCE:
    recommendation = metadata['target_classes'][prediction_idx]
    print(f"✅ Confident recommendation: {recommendation}")
else:
    print(f"⚠️  Low confidence ({confidence:.0%}), ask for more preferences")
```

---

## 🔍 Debugging

### Check Model Properties

```python
print("Model type:", type(model).__name__)
print("Number of features:", model.n_features_in_)
print("Classes:", model.classes_)
print("Feature importances:", model.feature_importances_)
```

### Validate Input Data

```python
import numpy as np

def validate_input(features: np.ndarray, expected_shape: int) -> bool:
    """Validate input before prediction"""
    
    # Check shape
    if len(features.shape) != 2:
        print(f"❌ Expected 2D array, got {len(features.shape)}D")
        return False
    
    if features.shape[1] != expected_shape:
        print(f"❌ Expected {expected_shape} features, got {features.shape[1]}")
        return False
    
    # Check for NaN/Inf
    if np.isnan(features).any():
        print("❌ Input contains NaN values")
        return False
    
    if np.isinf(features).any():
        print("❌ Input contains infinite values")
        return False
    
    print("✅ Input validation passed")
    return True
```

---

## 📈 Monitoring Production Model

Track these metrics in production:

```python
def log_prediction(features: np.ndarray, prediction: int, confidence: float):
    """Log prediction for monitoring"""
    import json
    from datetime import datetime
    
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'predicted_class': int(prediction),
        'confidence': float(confidence)
    }
    
    # Log to monitoring system
    with open('predictions.jsonl', 'a') as f:
        f.write(json.dumps(log_entry) + '\n')

# Monitor for:
# - Average confidence dropping (model uncertainty)
# - Prediction distribution changes (data drift)
# - Error rates increasing (model degradation)
```

---

**Last Updated:** March 19, 2024
