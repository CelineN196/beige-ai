# 🔍 Model Diagnostics & Analysis Tool

Standalone script for analyzing and debugging Beige.AI ML model behavior.

## Overview

`analysis/model_diagnostics.py` provides comprehensive insights into:
- ✅ Feature validation (shape, NaN checks, value ranges)
- ✅ Model performance metrics (accuracy, F1-score, confidence distribution)
- ✅ Feature importance analysis (XGBoost feature rankings)
- ✅ Sample predictions with confidence scores
- ✅ Cluster analysis (KMeans distribution, silhouette scores)
- ✅ Elbow curve visualization (for optimal K selection)

## Quick Start

### Basic Analysis (Recommended)
```bash
python analysis/model_diagnostics.py
```

**Output:**
- Feature validation summary
- Model accuracy & F1-score
- Top 20 most important features
- 15 sample predictions with confidence
- KMeans cluster distribution (K=5)

### With Visualizations
```bash
python analysis/model_diagnostics.py --plot --kmeans
```

**Output:** All above + `analysis/elbow_curve.png`

### KMeans Only Analysis
```bash
python analysis/model_diagnostics.py --kmeans
```

**Note:** KMeans analysis on 50K samples can take 2-5 minutes.

## Command-Line Options

```
--plot              Generate matplotlib visualizations
--kmeans            Include KMeans elbow curve analysis
--help              Show full help message
```

## Features in Detail

### 1. Feature Validation

Checks data quality:

```
✓ Shape: (50000, 29)
  - Samples: 50,000
  - Features: 29

✓ Missing Values: 0 total
  ✅ No NaN values detected

✓ Value Ranges:
  - Global Min: -2.8490
  - Global Max: 2.8534
  - Global Mean: 0.1724
  - Global Std: 0.6470
```

**What to Look For:**
- NaN count = 0 ✅
- Inf count = 0 ✅
- Mean ~0 for scaled features ✅
- Std independent of feature ✅

### 2. Model Performance Analysis

Evaluates model accuracy:

```
✓ Accuracy: 0.7484 (74.84%)
✓ F1-Score (weighted): 0.7312

✓ Prediction Confidence:
  - Mean: 0.8325
  - Std: 0.1964

  Very High (>0.9): 26,558 (53.12%)
  High (0.8-0.9):   8,136 (16.27%)
  Medium (0.7-0.8):  3,173 (6.35%)
  Low (<0.7):      12,133 (24.27%)
```

**Interpretation:**
- Accuracy 74.84% = Good baseline for 8-class problem
- 53% very high confidence = Model is confident on majority of samples
- 24% low confidence = Harder samples model struggles with

### 3. Feature Importance

XGBoost feature rankings:

```
Top 20 Most Important Features:
Rank   Feature         Importance      Relative (%)
1      Feature_12      0.128508         12.85% ██████
2      Feature_4       0.119803         11.98% █████
3      Feature_11      0.105828         10.58% █████
...
```

**Key Insights:**
- Top 5 features = 53.65% of importance
- Feature_12 most predictive (12.85%)
- Long tail: many features with <2% importance

### 4. Sample Predictions

Shows predictions on first 15 samples:

```
Idx   True    Pred    Confidence    Match
0     6       6       0.9934        ✓
1     6       6       0.7104        ✓
2     3       3       0.6812        ✓
...
Sample Accuracy: 13/15 (86.67%)
```

**What to Check:**
- Match ✓ = Correct prediction
- Match ✗ = Incorrect prediction
- Sample accuracy should be near overall accuracy

### 5. Cluster Analysis (KMeans)

Unsupervised clustering on features:

```
✓ Cluster Distribution (K=5):
Cluster    Count      Percentage
0          12,362     24.72%
1          6,970      13.94%
2          8,952      17.90%
3          9,833      19.67%
4          11,883     23.77%
```

**Interpretation:**
- Balanced clusters = Good feature diversity
- Skewed clusters = Some groups may dominate

### 6. Elbow Curve (Optional)

KMeans inertia & silhouette scores:

```
K=1: Inertia=12345.67, Silhouette=0.0000
K=2: Inertia=11234.56, Silhouette=0.2341
K=3: Inertia=10456.78, Silhouette=0.3124
K=4: Inertia=9876.54, Silhouette=0.3567
K=5: Inertia=9345.67, Silhouette=0.3821  ← Suggested elbow
```

**How to Read:**
- **Inertia decreases** as K increases (always true)
- **Elbow point** = where reduction slows down
- **Silhouette score** = goodness of clustering (0-1)

## Data Pipeline

The script replicates the training pipeline:

```
Raw CSV (50K samples, 14 features)
    ↓
Derive Features (temperature_category, comfort_index, environmental_score)
    ↓
Categorical Features: OneHotEncoder
Numerical Features: StandardScaler
    ↓
Preprocessed Array (50K × 29 features)
    ↓
Load Trained XGBoost Model
    ↓
Analyze & Report
```

## Feature Definitions

### Categorical Features (5)
- `mood` - User emotional state
- `weather_condition` - Current weather
- `time_of_day` - Morning/Afternoon/Evening/Night
- `season` - Spring/Summer/Autumn/Winter
- `temperature_category` - Cold/Mild/Hot (derived)

### Numerical Features (8)
- `temperature_celsius` - Exact temperature
- `humidity` - Relative humidity (0-100)
- `air_quality_index` - AQI score (0-500)
- `sweetness_preference` - User preference (0-10)
- `health_preference` - Health consciousness (0-10)
- `trend_popularity_score` - Trending score (0-100)
- `comfort_index` - Derived comfort metric (0-1)
- `environmental_score` - Derived environmental metric (0-1)

## Common Issues & Solutions

### Model Loading Error: "No module named 'numpy._core'"

**Problem:** Model saved with numpy 1.24.3, loaded with newer numpy

**Solution:** 
```bash
# Retrain model with current environment
python backend/training/train_v2_pipeline.py
```

**Status:** Script includes fallback to alternative model files - should auto-recover

### Very Long Runtime (--kmeans flag)

**Problem:** KMeans on 50K samples takes 2-5 minutes per K value

**Solution:**
- Omit `--kmeans` flag for faster basic analysis
- Run `--kmeans` when you have time for full analysis
- Consider using smaller dataset for faster iteration

### All Predictions Wrong

**Problem:** Sample accuracy << overall accuracy

**Possible Causes:**
1. Different feature preprocessing
2. Model file corrupted or incompatible
3. Data ordering issue

**Debug Steps:**
1. Check "Feature Validation" section for anomalies
2. Verify "Global Min/Max" values are normalized
3. Confirm data shape matches expected (50000, 29)

## Code Structure

```
analysis/model_diagnostics.py

├── Configuration & Paths
│
├── Section 1: Feature Validation
│   └── validate_features(X)
│
├── Section 2: Model Performance Analysis
│   └── analyze_model(model, X, y)
│
├── Section 3: Feature Importance
│   └── analyze_feature_importance(model, top_n)
│
├── Section 4: Sample Predictions
│   └── show_sample_predictions(model, X, y)
│
├── Section 5: KMeans Elbow Curve
│   └── plot_elbow_curve(X, k_range)
│
├── Section 6: Cluster Distribution
│   └── analyze_cluster_distribution(X, y, k)
│
├── Section 7: Data Loading & Preprocessing
│   └── load_data(data_path)
│
└── Section 8: Main Execution
    └── main(args)
```

## Integration Notes

### ✅ What This Script Does
- Reads data from `backend/data/beige_ai_cake_dataset_v2.csv`
- Loads model from `models/v2_xgboost_model.pkl` (or fallback paths)
- Replicates training preprocessing pipeline exactly
- **Does NOT modify** model, data, or production files
- **Does NOT require** Streamlit or Flask

### ❌ What This Script Doesn't Do
- Modify training code
- Retrain or tune models
- Change Streamlit app
- Access API endpoints
- Require internet connection

## Output Files

When `--plot` flag is used:
- `analysis/elbow_curve.png` - Inertia & silhouette score plots

When run normally:
- No files created, only console output

## Example Run (Full Output)

```bash
$ python analysis/model_diagnostics.py

======================================================================
🔍 BEIGE.AI MODEL DIAGNOSTICS
======================================================================

[Loading Data...]
✓ Loaded: 50,000 samples, 14 columns
✓ Features: 13 (5 categorical, 8 numerical)
✓ Target classes: 8

[Feature Validation...]
✓ Shape: (50000, 29)
✓ Missing Values: 0 total
✓ No NaN values detected

[Loading Model...]
✓ Model loaded: XGBClassifier

[Performance Analysis...]
✓ Accuracy: 0.7484 (74.84%)
✓ F1-Score (weighted): 0.7312

[Feature Importance...]
Top 5 features account for 53.65% of importance

[Sample Predictions...]
Sample Accuracy: 13/15 (86.67%)

[Cluster Distribution...]
K=5 clusters (24.72% - 23.77% balanced)

======================================================================
✅ DIAGNOSTICS COMPLETE
======================================================================
```

## Next Steps After Diagnostics

1. **Feature Validation Issues?**
   - Check data for outliers
   - Verify preprocessing steps
   - Review data collection process

2. **Model Performance Lower Than Expected?**
   - Examine feature importance - are key features being used?
   - Check confidence distribution - is model uncertain?
   - Review sample predictions for patterns in errors

3. **High Feature Importance Concentration?**
   - Top 5 features = 50%+ importance suggests overfitting on key features
   - Consider feature engineering for other features
   - Evaluate multicollinearity

4. **Poor Cluster Distribution?**
   - If clusters are very unbalanced, data may have structure issues
   - Consider resampling or class weighting in training
   - Check for data quality issues

## Performance Notes

| Operation | Time | Notes |
|-----------|------|-------|
| Data Loading | ~2s | 50K samples from CSV |
| Feature Validation | <1s | Shape & statistics checks |
| Model Loading | <1s | XGBoost model deserialization |
| Model Analysis | ~5s | Accuracy, F1, confidence distribution |
| Feature Importance | <1s | Extract XGBoost importance scores |
| Sample Predictions | <1s | 15 sample predictions |
| Cluster Distribution | ~5s | KMeans with K=5, n_init=10 |
| Elbow Curve (10 iterations) | 2-5m | KMeans K=1..10 with silhouette scores |
| **Total (no --kmeans)** | **~15s** | All analyses except elbow curve |
| **Total (with --kmeans)** | **2-5m** | Includes 10 KMeans iterations |

## Troubleshooting

**Q: Script fails at model loading?**
A: Check that model files exist in `models/` directory. Script tries multiple fallback paths.

**Q: Features don't look preprocessed?**
A: That's correct! Script shows numerical features are standardized (mean~0, std~1).

**Q: Why are categorical features 0-1?**
A: OneHotEncoder creates binary columns (0 or 1) for each category.

**Q: Can I modify this script?**
A: Yes! It's a diagnostic tool. Common modifications:
   - Change `top_n` in feature importance
   - Change `k` in cluster distribution  
   - Add custom visualizations
   - Export results to CSV

## License

Part of Beige.AI project. For development use only.

---

**Questions or issues?** Check the code comments in `analysis/model_diagnostics.py` for detailed implementation notes.
