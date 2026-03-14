# Beige.AI Model Deployment & Usage Guide

## Quick Start: Making Predictions

### 1. Load the Model

```python
import joblib
import pandas as pd
import numpy as np

# Load artifacts
model = joblib.load('best_model.joblib')
preprocessor = joblib.load('preprocessor.joblib')
feature_info = joblib.load('feature_info.joblib')

print(f"Model loaded: {feature_info['model_type']}")
print(f"Test accuracy: {feature_info['test_accuracy']:.2%}")
print(f"Available cakes: {feature_info['cake_menu']}")
```

### 2. Prepare Input Data

```python
# Create a sample customer profile
sample_data = pd.DataFrame({
    'mood': ['Happy'],
    'weather_condition': ['Sunny'],
    'time_of_day': ['Afternoon'],
    'season': ['Summer'],
    'temperature_category': ['hot'],
    'temperature_celsius': [32.5],
    'humidity': [65.0],
    'air_quality_index': [85.0],
    'sweetness_preference': [8],
    'health_preference': [4],
    'trend_popularity_score': [0.75],
    'comfort_index': [0.8],
    'environmental_score': [0.55]
})
```

### 3. Make Prediction

```python
# Preprocess input
X_processed = preprocessor.transform(sample_data)

# Get prediction and confidence
prediction = model.predict(X_processed)[0]
probabilities = model.predict_proba(X_processed)[0]

print(f"Predicted cake: {prediction}")
print(f"Confidence: {probabilities.max():.2%}")

# Show all probabilities
for cake, prob in zip(feature_info['classes'], probabilities):
    print(f"  {cake}: {prob:.2%}")
```

---

## Python API Example

### Complete Prediction Function

```python
import joblib
import pandas as pd

class BeigeAIPrediction:
    def __init__(self):
        self.model = joblib.load('best_model.joblib')
        self.preprocessor = joblib.load('preprocessor.joblib')
        self.feature_info = joblib.load('feature_info.joblib')
    
    def predict(self, customer_profile):
        """
        Predict cake category for a customer.
        
        Args:
            customer_profile (dict): Customer features
            
        Returns:
            dict: Prediction and probabilities
        """
        # Create DataFrame from dict
        df = pd.DataFrame([customer_profile])
        
        # Preprocess
        X = self.preprocessor.transform(df)
        
        # Predict
        prediction = self.model.predict(X)[0]
        probabilities = self.model.predict_proba(X)[0]
        
        # Format results
        prob_dict = {
            cake: float(prob) 
            for cake, prob in zip(self.feature_info['classes'], probabilities)
        }
        
        return {
            'prediction': prediction,
            'confidence': float(probabilities.max()),
            'probabilities': prob_dict
        }

# Usage
predictor = BeigeAIPrediction()

customer = {
    'mood': 'Stressed',
    'weather_condition': 'Rainy',
    'time_of_day': 'Evening',
    'season': 'Autumn',
    'temperature_category': 'cold',
    'temperature_celsius': 8.5,
    'humidity': 78.0,
    'air_quality_index': 120.0,
    'sweetness_preference': 9,
    'health_preference': 2,
    'trend_popularity_score': 0.3,
    'comfort_index': 0.35,
    'environmental_score': 0.45
}

result = predictor.predict(customer)
print(f"Prediction: {result['prediction']}")
print(f"Confidence: {result['confidence']:.2%}")
```

---

## Feature Descriptions

### Categorical Features

| Feature | Valid Values |
|---------|--------------|
| **mood** | Happy, Stressed, Tired, Lonely, Celebratory |
| **weather_condition** | Sunny, Rainy, Cloudy, Snowy, Stormy |
| **time_of_day** | Morning, Afternoon, Evening, Night |
| **season** | Spring, Summer, Autumn, Winter |
| **temperature_category** | cold, mild, hot |

### Numerical Features

| Feature | Range | Example |
|---------|-------|---------|
| **temperature_celsius** | -10 to 40 | 22.5 |
| **humidity** | 20 to 95 | 65.0 |
| **air_quality_index** | 0 to 300 | 100.0 |
| **sweetness_preference** | 1 to 10 | 7 |
| **health_preference** | 1 to 10 | 6 |
| **trend_popularity_score** | 0.0 to 1.0 | 0.75 |
| **comfort_index** | 0.0 to 1.0 | 0.68 |
| **environmental_score** | 0.0 to 1.0 | 0.52 |

---

## Example Predictions

### Scenario 1: Happy Summer Customer (Afternoon)

**Input:**
```python
{
    'mood': 'Happy',
    'weather_condition': 'Sunny',
    'time_of_day': 'Afternoon',
    'season': 'Summer',
    'temperature_category': 'hot',
    'temperature_celsius': 32.0,
    'humidity': 60.0,
    'air_quality_index': 75.0,
    'sweetness_preference': 6,
    'health_preference': 8,
    'trend_popularity_score': 0.7,
    'comfort_index': 0.87,
    'environmental_score': 0.62
}
```

**Expected Prediction:**
- **Korean Sesame Mini Bread** (Light, healthy, afternoon-friendly)

---

### Scenario 2: Stressed Evening Customer (Rainy)

**Input:**
```python
{
    'mood': 'Stressed',
    'weather_condition': 'Rainy',
    'time_of_day': 'Evening',
    'season': 'Autumn',
    'temperature_category': 'cold',
    'temperature_celsius': 12.0,
    'humidity': 80.0,
    'air_quality_index': 140.0,
    'sweetness_preference': 9,
    'health_preference': 2,
    'trend_popularity_score': 0.2,
    'comfort_index': 0.32,
    'environmental_score': 0.40
}
```

**Expected Prediction:**
- **Dark Chocolate Sea Salt Cake** (Comfort food, high sweetness)

---

### Scenario 3: Tired Morning Customer

**Input:**
```python
{
    'mood': 'Tired',
    'weather_condition': 'Cloudy',
    'time_of_day': 'Morning',
    'season': 'Winter',
    'temperature_category': 'cold',
    'temperature_celsius': 3.0,
    'humidity': 70.0,
    'air_quality_index': 95.0,
    'sweetness_preference': 5,
    'health_preference': 6,
    'trend_popularity_score': 0.6,
    'comfort_index': 0.48,
    'environmental_score': 0.52
}
```

**Expected Prediction:**
- **Matcha Zen Cake** (Energizing caffeine, morning-friendly)

---

## Batch Predictions

```python
import pandas as pd
import joblib

# Load model
model = joblib.load('best_model.joblib')
preprocessor = joblib.load('preprocessor.joblib')

# Load customer data (CSV)
customers = pd.read_csv('customer_profiles.csv')

# Make predictions for all customers
X_processed = preprocessor.transform(customers)
predictions = model.predict(X_processed)
confidences = model.predict_proba(X_processed).max(axis=1)

# Add predictions to dataframe
customers['predicted_cake'] = predictions
customers['confidence'] = confidences

# Save results
customers.to_csv('predictions.csv', index=False)

print(f"Predicted {len(customers)} customers")
print(f"Average confidence: {confidences.mean():.2%}")
```

---

## Model Limitations

### Classes with Lower Accuracy
- **Citrus Cloud Cake**: 28% recall (rare class)
- **Earthy Wellness Cake**: 24% recall (small sample)
- **Silk Cheesecake**: 20% recall (easily confused)
- **Berry Garden Cake**: 44% recall (imbalanced)

### Recommendations
1. Use higher confidence threshold (>70%) for critical decisions
2. Manual review for low-confidence predictions
3. Collect more data for minority classes
4. Consider ensemble methods for edge cases

---

## Production Deployment Checklist

- [ ] Load and test model artifacts
- [ ] Validate feature preprocessing
- [ ] Test with sample predictions
- [ ] Monitor prediction distribution
- [ ] Log all predictions
- [ ] Track accuracy metrics
- [ ] Set up alerts for failures
- [ ] Plan regular retraining

---

## Troubleshooting

### Issue: "Feature X not found"
**Solution:** Check feature names match the training dataset

### Issue: Low confidence predictions
**Solution:** Model uncertainty - may need manual review
Consider collecting more similar training data

### Issue: Unexpected predictions
**Solution:** Verify input values are in valid ranges
Check categorical values match exact strings

---

## Next Steps

1. **Deploy to Web App** (Streamlit)
   ```bash
   streamlit run app.py
   ```

2. **Create REST API** (Flask)
   ```python
   flask run
   ```

3. **Monitor Performance**
   - Track real predictions vs actual choices
   - Identify drift in data distribution
   - Plan retraining schedule

4. **Improve Model**
   - Collect real-world customer data
   - Address class imbalance
   - Feature engineering improvements

---

## Support

For issues or questions:
1. Check `feature_info.joblib` for valid values
2. Review confusion matrix in `phase3_model_evaluation.png`
3. Refer to `PHASE_3_SUMMARY.md` for detailed metrics

---

**Model Version:** 1.0  
**Created:** March 14, 2026  
**Test Accuracy:** 78.80%  
**Status:** Production Ready ✅
