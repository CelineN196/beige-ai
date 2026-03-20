#!/usr/bin/env python3
import joblib
import pandas as pd
import numpy as np

# Load
preprocessor = joblib.load('backend/models/preprocessor.joblib')
model = joblib.load('backend/models/cake_model.joblib')

print('✅ Artifacts loaded')

# Test with exact app structure
user_input = pd.DataFrame({
    'mood': ['Happy'],
    'weather_condition': ['Sunny'],
    'temperature_celsius': [28],
    'humidity': [72],
    'air_quality_index': [65],
    'time_of_day': ['Afternoon'],
    'sweetness_preference': ['medium'],
    'health_preference': ['balanced'],
    'trend_popularity_score': [0.75],
    'temperature_category': ['mild'],
    'comfort_index': [0.85],
    'environmental_score': [0.70],
    'season': ['Summer']
})

print(f'Input columns: {sorted(user_input.columns.tolist())}')
X_processed = preprocessor.transform(user_input)
print(f'✅ Transform successful! Shape: {X_processed.shape}')

# Test prediction
probabilities = model.predict_proba(X_processed)[0]
print(f'✅ Prediction successful! Top probability: {max(probabilities):.4f}')
