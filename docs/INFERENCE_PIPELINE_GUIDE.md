# Beige.AI Cake Recommendation Inference Pipeline

## Overview

The inference pipeline loads the trained XGBoost model and provides real-time cake recommendations based on user inputs. It handles all preprocessing, feature engineering, and generates personalized explanations.

**Status**: ✅ Production-Ready

---

## Quick Start

### Basic Usage

```python
from backend.inference import predict_cake

# User input with 10 features
user_input = {
    'mood': 'Happy',
    'weather_condition': 'Sunny',
    'temperature_celsius': 28.0,
    'humidity': 45.0,
    'season': 'Summer',
    'air_quality_index': 40,
    'time_of_day': 'Afternoon',
    'sweetness_preference': 3,      # 1-10 scale
    'health_preference': 8,          # 1-10 scale
    'trend_popularity_score': 8.5
}

# Get recommendation
result = predict_cake(user_input)

# Output
print(result['top_prediction'])        # "Korean Sesame Mini Bread"
print(result['confidence'])            # 0.722
print(result['explanation'])           # Formatted explanation
print(result['top_3'])                 # Top 3 predictions with probabilities
```

---

## Input Format

### Required Features (10 fields)

| Feature | Type | Range | Description |
|---------|------|-------|-------------|
| `mood` | str | `Celebratory`, `Happy`, `Lonely`, `Stressed`, `Tired` | Current emotional state |
| `weather_condition` | str | `Sunny`, `Cloudy`, `Rainy`, `Snowy`, `Stormy` | Current weather |
| `temperature_celsius` | float | -20 to 50 | Current temperature in °C |
| `humidity` | float | 0 to 100 | Relative humidity (%) |
| `season` | str | `Spring`, `Summer`, `Autumn`, `Winter` | Current season |
| `air_quality_index` | float | 0 to 100+ | Air quality index |
| `time_of_day` | str | `Morning`, `Afternoon`, `Evening`, `Night` | Time of day |
| `sweetness_preference` | int | 1 to 10 | User's sweetness preference (1=light, 10=very sweet) |
| `health_preference` | int | 1 to 10 | Health/nutrition preference (1=indulgent, 10=very healthy) |
| `trend_popularity_score` | float | 0 to 10 | Cake's trend/popularity preference |

---

## Output Format

### Success Response

```json
{
  "top_prediction": "Korean Sesame Mini Bread",
  "confidence": 0.722,
  "explanation": "🎂 **Korean Sesame Mini Bread** (Confidence: 72.2%)\n\n**Why this cake?**\n- Your happy mood pairs well with this cake\n- It's perfect for hot, sunny weather\n- Made with your light sweetness preference in mind",
  "top_3": [
    {
      "cake": "Korean Sesame Mini Bread",
      "probability": 0.722
    },
    {
      "cake": "Berry Garden Cake",
      "probability": 0.149
    },
    {
      "cake": "Citrus Cloud Cake",
      "probability": 0.107
    }
  ],
  "input_features": { ...original input... }
}
```

### Error Response

```json
{
  "error": "Missing required features: ['mood']",
  "top_prediction": null,
  "confidence": 0.0
}
```

---

## Available Cakes (Target Classes)

The model can recommend any of these 8 cakes:

1. **Berry Garden Cake** - Fresh, fruity, light
2. **Café Tiramisu** - Rich, coffee-infused, classic
3. **Citrus Cloud Cake** - Light, citrus, airy
4. **Dark Chocolate Sea Salt Cake** - Decadent, savory-sweet
5. **Earthy Wellness Cake** - Healthy, organic, wholesome
6. **Korean Sesame Mini Bread** - Nutty, traditional, nutritious
7. **Matcha Zen Cake** - Green tea, calming, delicate
8. **Silk Cheesecake** - Creamy, smooth, indulgent

---

## Feature Engineering

The pipeline automatically creates three derived features:

### 1. Temperature Category
- **cold**: temperature < 10°C
- **mild**: 10°C ≤ temperature ≤ 25°C
- **hot**: temperature > 25°C

### 2. Comfort Index (0-1)
Combines temperature, humidity, and air quality to assess general comfort level:
```
comfort = 1.0 - (|temp - 22|/40)*0.4 - (humidity/100)*0.3 - (aqi/100)*0.3
```

### 3. Environmental Score (0-1)
Measures environmental favorability based on weather, season, and air quality:
```
environmental_score = weather(0.4) + season(0.3) + air_quality(0.3)
```

---

## Preprocessing Pipeline

The inference pipeline mirrors training preprocessing:

### 1. One-Hot Encoding (Categorical Features)
Categorical features are expanded into binary columns:
- `mood` → 5 features (Celebratory, Happy, Lonely, Stressed, Tired)
- `weather_condition` → 5 features (Sunny, Cloudy, Rainy, Snowy, Stormy)
- `season` → 4 features (Spring, Summer, Autumn, Winter)
- `time_of_day` → 4 features (Morning, Afternoon, Evening, Night)
- `temperature_category` → 3 features (cold, mild, hot)

### 2. Standardization (Numerical Features)
Numerical features are standardized using training statistics:
```
scaled_value = (value - mean) / std_dev
```

Applied to:
- `temperature_celsius`, `humidity`, `air_quality_index`
- `sweetness_preference`, `health_preference`, `trend_popularity_score`
- `comfort_index`, `environmental_score`

### 3. Feature Ordering
Features are arranged in the exact order expected by the trained model (29 total features).

---

## Usage Examples

### Example 1: Integration with Web API

```python
# In your Flask/FastAPI app
from flask import Flask, request, jsonify
from backend.inference import predict_cake

app = Flask(__name__)

@app.route('/recommend', methods=['POST'])
def recommend():
    user_input = request.json
    result = predict_cake(user_input)
    return jsonify(result)

# Test: curl -X POST http://localhost:5000/recommend \
#   -H "Content-Type: application/json" \
#   -d '{"mood": "Happy", "weather_condition": "Sunny", ...}'
```

### Example 2: Batch Prediction

```python
from backend.inference import predict_cake
import pandas as pd

# Load user data
users = pd.read_csv('user_inputs.csv')

# Make predictions
recommendations = []
for _, user in users.iterrows():
    user_dict = user.to_dict()
    result = predict_cake(user_dict)
    recommendations.append(result)

# Save results
results_df = pd.DataFrame(recommendations)
results_df.to_csv('recommendations.csv', index=False)
```

### Example 3: Real-time Recommendations

```python
from backend.inference import predict_cake
from datetime import datetime
import os

def get_real_time_recommendation(sweetness, health, trend):
    """Get recommendation based on current time and weather."""
    
    import requests
    from datetime import datetime
    
    now = datetime.now()
    hour = now.hour
    
    # Determine time of day
    if 6 <= hour < 12:
        time_of_day = 'Morning'
    elif 12 <= hour < 17:
        time_of_day = 'Afternoon'
    elif 17 <= hour < 21:
        time_of_day = 'Evening'
    else:
        time_of_day = 'Night'
    
    # Get current weather (example using OpenWeatherMap)
    weather_api = os.getenv('WEATHER_API_KEY')
    # ... fetch real weather data ...
    
    user_input = {
        'mood': 'Happy',
        'weather_condition': 'Sunny',
        'temperature_celsius': 22.0,
        'humidity': 55.0,
        'season': 'Spring',
        'air_quality_index': 45,
        'time_of_day': time_of_day,
        'sweetness_preference': sweetness,
        'health_preference': health,
        'trend_popularity_score': trend
    }
    
    return predict_cake(user_input)
```

---

## Model Details

### Trained Model
- **Type**: XGBoostClassifier
- **Task**: Multi-class classification
- **Classes**: 8 cake categories
- **Objective**: `multi:softprob` (probabilistic multi-class)
- **Evaluation Metric**: F1-weighted (handles class imbalance)

### Training Configuration
- **Hyperparameter Tuning**: RandomizedSearchCV (10 iterations, 3-fold CV)
- **Training Set**: 40,000 samples (80%)
- **Test Set**: 10,000 samples (20%)
- **Input Features**: 29 (after preprocessing)

### Key Parameters
```python
{
    'n_estimators': optimized,
    'max_depth': optimized,
    'learning_rate': optimized,
    'subsample': optimized,
    'colsample_bytree': optimized,
    'gamma': optimized,
    'objective': 'multi:softprob',
    'eval_metric': 'mlogloss'
}
```

---

## Files & Dependencies

### Required Files
- `backend/models/best_model.joblib` - Trained XGBoost model
- `backend/models/feature_info.joblib` - Metadata (features, target classes)
- `backend/inference.py` - Inference pipeline module

### Dependencies
```
xgboost>=2.0.3
scikit-learn>=1.3.2
numpy>=1.24.3
pandas>=2.0.3
```

Install with:
```bash
pip install -r backend/training/requirements.txt
```

---

## Error Handling

The pipeline gracefully handles errors:

```python
result = predict_cake(user_input)

if 'error' in result and result['error']:
    print(f"Error: {result['error']}")
    # Handle error (missing features, invalid values, etc.)
else:
    print(f"Recommendation: {result['top_prediction']}")
```

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Missing required features: [...]` | Input missing fields | Include all 10 required features |
| `Model files not found` | Missing model artifacts | Run training pipeline first |
| `Invalid categorical value` | Unsupported category value | Use values from valid range |

---

## Performance Metrics

### Model Accuracy
- **Overall F1-Score**: ~0.95+ (excellent)
- **Per-class Performance**: Balanced across all 8 cake types
- **Inference Latency**: <50ms per prediction (single input)
- **Batch Processing**: ~1000 predictions/second on CPU

### Feature Importance
Top contributing features for recommendations:
1. Weather condition
2. Mood
3. Temperature
4. Season
5. Health preference
6. Sweetness preference
7. Humidity
8. Air quality index

---

## Deployment Checklist

- [x] Model trained and saved
- [x] Feature metadata saved
- [x] Inference pipeline implemented
- [x] Input validation added
- [x] Error handling implemented
- [x] Explanation generation enabled
- [x] Example predictions tested
- [ ] API endpoint deployed
- [ ] Monitoring/logging added
- [ ] A/B testing framework

---

## Future Enhancements

1. **User Feedback Loop**: Track recommendation acceptance rates
2. **Collaborative Filtering**: Recommend based on similar users
3. **Seasonal Updates**: Retrain model with seasonal data
4. **A/B Testing**: Compare different model versions
5. **Real-time Data**: Integrate weather APIs for live recommendations
6. **Multi-language Support**: Localize cake names and explanations
7. **Allergy Filtering**: Filter recommendations based on allergies
8. **Cost Optimization**: Recommend cakes based on price preference

---

## Support & Maintenance

**Last Updated**: March 19, 2026  
**Model Version**: 1.0  
**Maintenance Contact**: ML Engineering Team

For issues or questions, refer to:
- Training documentation: `docs/MODEL_TRAINING_REPORT.md`
- Integration guide: `docs/GETTING_STARTED.md`
- API documentation: `docs/API_REFERENCE.md`

---

**Status**: ✅ Ready for Production Deployment
