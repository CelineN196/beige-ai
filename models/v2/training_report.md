# Beige AI V2 - Training Report

**Date:** 2026-03-22 16:30:09
**Best Model:** XGBoost

## Model Comparison

| Model | Accuracy | F1-Score (weighted) | Log Loss |
|-------|----------|-------------------|----------|
| Gradient Boosting | 0.7782 | 0.7729 | 0.5041 |
| XGBoost | 0.7880 | 0.7833 | 0.4749 |

## Features Used

**Categorical Features (5):**
mood, weather_condition, time_of_day, season, temperature_category

**Numerical Features (8):**
temperature_celsius, humidity, air_quality_index, sweetness_preference, health_preference, trend_popularity_score, comfort_index, environmental_score

**Total Features After Encoding:** 29

## Dataset Information

- Total Samples: ~50,000
- Train/Val/Test Split: 60% / 20% / 20%
- Target Variable: cake_category
- Number of Classes: ~8 cake types

## Key Hyperparameters (Best Model)

See `metrics.json` for complete metadata.

## Files Generated

- `best_model.pkl` - Production model
- `preprocessor.pkl` - Feature preprocessing pipeline
- `feature_names.json` - All feature names after encoding
- `metrics.json` - Model performance metrics
