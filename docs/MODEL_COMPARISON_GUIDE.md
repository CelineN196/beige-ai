# Model Comparison & Selection Guide

## Overview

This document provides a comprehensive guide to the Beige.AI model comparison and selection pipeline. The pipeline trains three classification models, performs hyperparameter tuning, and selects the best performer for production.

---

## Architecture

### Three Classification Models

#### 1. **Decision Tree (DT)**

**Pros:**
- ✅ Highly interpretable - can visualize decision rules
- ✅ Fast inference time - O(log n)
- ✅ No feature scaling required
- ✅ Handles non-linear relationships

**Cons:**
- ❌ Prone to overfitting
- ❌ Unstable with small data changes
- ❌ High variance

**When to use:**
- Interpretability is critical
- Small datasets
- Real-time predictions needed
- Explainability required for business stakeholders

**Hyperparameter Tuning Space:**
```python
max_depth: [3, 5, 7, 10, 15, 20, None]
min_samples_split: [2, 5, 10, 20]
min_samples_leaf: [1, 2, 4, 8]
```

---

#### 2. **Random Forest (RF)**

**Pros:**
- ✅ Excellent generalization - reduces overfitting
- ✅ Robust to outliers and missing values
- ✅ Feature importance ranking
- ✅ Parallel training capability
- ✅ Good baseline for most problems

**Cons:**
- ❌ Less interpretable than single trees
- ❌ Memory intensive with large n_estimators
- ❌ Slower predict than decision tree
- ❌ Black-box nature

**When to use:**
- Balanced accuracy-interpretability tradeoff needed
- Medium to large datasets
- Feature importance analysis desired
- Default choice when unsure

**Hyperparameter Tuning Space:**
```python
n_estimators: [50, 100, 200, 300]
max_depth: [5, 10, 15, 20, None]
min_samples_split: [2, 5, 10]
min_samples_leaf: [1, 2, 4]
```

---

#### 3. **Gradient Boosting (GB)**

**Pros:**
- ✅ Often highest accuracy
- ✅ Complex pattern learning capacity
- ✅ Feature importance scores
- ✅ Handles mixed data types well

**Cons:**
- ❌ Prone to overfitting if not tuned carefully
- ❌ Slower training time
- ❌ More hyperparameters to tune
- ❌ Sequential training (not parallelizable)

**When to use:**
- Maximum accuracy needed
- Large datasets available
- Time/resources for careful tuning
- Production system can afford slower training

**Hyperparameter Tuning Space:**
```python
n_estimators: [50, 100, 200]
learning_rate: [0.01, 0.05, 0.1, 0.15]
max_depth: [3, 5, 7, 10]
```

---

## Methodology

### 1. Data Preprocessing Pipeline

```
Raw Data
    ↓
Load CSV → Identify Features/Target
    ↓
Separate Categorical & Numerical
    ↓
Categorical Features → OneHotEncoder
Numerical Features → StandardScaler
    ↓
Combined Feature Matrix
    ↓
80/20 Train/Test Split (Stratified)
```

**Key Points:**
- Stratified split ensures class distribution is preserved
- OneHotEncoding for categorical features
- StandardScaler normalization for numerical features
- Missing value handling in preprocessing

### 2. Hyperparameter Tuning

**Method:** RandomizedSearchCV
- **CV Folds:** 5 (cross-validation)
- **Scoring Metric:** F1-weighted (handles class imbalance)
- **Iterations:** 20 random parameter combinations per model
- **Random Seed:** 42 (reproducibility)

**Why RandomizedSearchCV?**
- More efficient than GridSearchCV for large parameter spaces
- Better exploration of hyperparameter space
- Faster execution time
- Captures most of the performance improvement with fewer iterations

**Why F1-weighted?**
- Accounts for class imbalance
- Balances precision and recall
- More robust than accuracy for imbalanced datasets
- Weighted average accounts for all classes fairly

### 3. Model Evaluation

**Metrics Calculated:**

1. **Accuracy** = (TP + TN) / (TP + TN + FP + FN)
   - Overall correctness
   - Misleading with imbalanced data

2. **Precision** = TP / (TP + FP)
   - False positive rate control
   - "When the model says YES, how often is it right?"

3. **Recall** = TP / (TP + FN)
   - False negative rate control
   - "How many actual positives did we find?"

4. **F1-Score** = 2 × (Precision × Recall) / (Precision + Recall)
   - Harmonic mean of precision and recall
   - Primary optimization metric

5. **Confusion Matrix**
   - Detailed view of prediction breakdown
   - Identifies which classes are confused

### 4. Model Selection Criteria

**Primary Criterion:** Highest F1-weighted score
- Balances all performance aspects
- Accounts for class imbalance
- Most robust metric for decision making

**Secondary Criteria (if tied):**
1. Inference speed
2. Model complexity
3. Feature importance interpretability
4. Stability (variance across CV folds)

---

## Usage Guide

### Installation

```bash
# Install dependencies
cd backend/training
pip install -r requirements.txt
```

### Running the Pipeline

```bash
# Basic execution
python compare_models.py

# With custom dataset location
# Edit DATA_DIR in compare_models.py
```

### Expected Output

```
🔵 [2024-03-19 14:32:00] Loading dataset...
🔵 [2024-03-19 14:32:01] Dataset shape: (1000, 15)
✅ [2024-03-19 14:32:02] Train set: 800 samples
✅ [2024-03-19 14:32:02] Test set: 200 samples

🔵 [2024-03-19 14:32:03] Training Decision Tree...
✅ [2024-03-19 14:32:05] Best params: {'max_depth': 10, ...}
✅ [2024-03-19 14:32:05] Best CV score (F1): 0.8234

🔵 [2024-03-19 14:32:06] Training Random Forest...
✅ [2024-03-19 14:32:15] Best params: {'n_estimators': 200, ...}
✅ [2024-03-19 14:32:15] Best CV score (F1): 0.8567

🔵 [2024-03-19 14:32:16] Training Gradient Boosting...
✅ [2024-03-19 14:32:45] Best params: {'learning_rate': 0.1, ...}
✅ [2024-03-19 14:32:45] Best CV score (F1): 0.8721

🏆 BEST MODEL: Gradient Boosting (F1: 0.8721)
```

### Output Files

1. **Model Artifacts**
   - `backend/models/best_model.joblib` - Trained model (pickled)
   - `backend/models/feature_info.joblib` - Metadata and features

2. **Reports & Visualizations**
   - `docs/MODEL_TRAINING_REPORT.md` - Comprehensive report
   - `docs/confusion_matrix_gradient_boosting.png` - Confusion matrix visual

### Performance Interpretation

| Metric | Range | Interpretation |
|--------|-------|-----------------|
| F1-Score | 0.8-1.0 | Excellent |
| F1-Score | 0.6-0.8 | Good |
| F1-Score | 0.4-0.6 | Fair |
| F1-Score | 0.0-0.4 | Poor |

---

## Model Deployment

### Loading Trained Model

```python
import joblib

# Load model
model = joblib.load('backend/models/best_model.joblib')

# Load metadata
metadata = joblib.load('backend/models/feature_info.joblib')

# Make predictions
predictions = model.predict(X_new)
probabilities = model.predict_proba(X_new)
```

### API Integration

```python
from flask import Flask, request
import joblib

app = Flask(__name__)
model = joblib.load('models/best_model.joblib')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    features = prepare_features(data)  # Preprocess like training
    prediction = model.predict([features])[0]
    confidence = max(model.predict_proba([features])[0])
    return {'prediction': prediction, 'confidence': confidence}
```

---

## Troubleshooting

### Common Issues

**Issue: Import Error for sklearn**
```bash
Solution: pip install scikit-learn
```

**Issue: Data not found**
```
Error: FileNotFoundError at backend/data/beige_ai_cake_dataset_v2.csv
Solution: Ensure dataset exists at correct path, update DATA_DIR in script
```

**Issue: Out of Memory during training**
```
Solution: 
1. Reduce n_iter in RandomizedSearchCV (10 instead of 20)
2. Reduce n_jobs to 2 or 4 instead of -1 (all CPUs)
3. Use smaller CV folds (3 instead of 5)
```

**Issue: Class imbalance causing poor performance**
```
Solution:
1. Increase class_weight parameter
2. Use SMOTE for oversampling minority class
3. Adjust decision threshold
```

---

## Performance Optimization Tips

### For Training Speed
1. ✅ Use RandomizedSearchCV instead of GridSearchCV
2. ✅ Increase n_jobs to use all CPU cores
3. ✅ Reduce CV folds if acceptable (but 5 is standard)
4. ✅ Use fewer hyperparameter combinations

### For Model Accuracy
1. ✅ Increase hyperparameter search space (more iterations)
2. ✅ Use GridSearchCV for final tuning (after RandomizedSearch)
3. ✅ Add feature engineering steps
4. ✅ Collect more training data
5. ✅ Implement ensemble voting

### For Memory Efficiency
1. ✅ Use `sparse_output=True` in OneHotEncoder
2. ✅ Reduce n_estimators in Random Forest
3. ✅ Use `max_depth` to limit tree growth
4. ✅ Implement feature selection (select k-best)

---

## Advanced Customization

### Adding a Custom Model

```python
# In compare_models.py, add new function:

def train_custom_model(X_train, y_train, X_test, y_test):
    from xgboost import XGBClassifier
    
    xgb = XGBClassifier(random_state=RANDOM_STATE)
    
    xgb_params = {
        'n_estimators': [100, 200, 300],
        'learning_rate': [0.01, 0.05, 0.1],
        'max_depth': [3, 5, 7],
    }
    
    search = RandomizedSearchCV(xgb, xgb_params, n_iter=20, cv=5)
    search.fit(X_train, y_train)
    
    y_pred = search.best_estimator_.predict(X_test)
    metrics = evaluate_model(y_test, y_pred)
    
    return search.best_estimator_, metrics, y_pred

# Then in main(), add:
log("\n--- XGBoost ---", "INFO")
xgb_model, xgb_metrics, xgb_pred = train_custom_model(X_train, y_train, X_test, y_test)
results_dict['XGBoost'] = {
    'model': xgb_model,
    'metrics': xgb_metrics,
    'predictions': xgb_pred,
}
```

### Adjusting Hyperparameter Spaces

Edit the parameter distribution dictionaries at top of file:

```python
dt_param_dist = {
    'max_depth': [5, 10, 15],  # More conservative depth
    'min_samples_split': [5, 10],  # Reduce overfitting
    'min_samples_leaf': [2, 4],
}
```

---

## Monitoring & Maintenance

### Production Monitoring Dashboard

Track these metrics weekly:
- ✅ Model accuracy on new test data
- ✅ Precision and recall per class
- ✅ Confusion matrix patterns
- ✅ Prediction confidence distribution
- ✅ Feature value drift

### Retraining Triggers

Retrain the model when:
1. **Accuracy drops >2%** from baseline
2. **Monthly schedule** regardless of performance
3. **New features** are added to system
4. **Data distribution shifts** detected
5. **Significant feedback** from users/stakeholders

### Version Control

```bash
# Save model versions with timestamps
model_v1_2024_03_19.joblib
model_v1_2024_04_19.joblib
model_v2_2024_05_19.joblib
```

---

## References & Further Reading

1. **Scikit-learn Documentation**: https://scikit-learn.org/
2. **Hyperparameter Tuning Guide**: https://scikit-learn.org/stable/modules/grid_search.html
3. **Evaluation Metrics**: https://scikit-learn.org/stable/modules/model_evaluation.html
4. **Tree-based Models**: https://scikit-learn.org/stable/modules/tree.html
5. **Ensemble Methods**: https://scikit-learn.org/stable/modules/ensemble.html

---

## Support & Contact

For issues or questions:
1. Check the Troubleshooting section above
2. Review generated MODEL_TRAINING_REPORT.md
3. Consult scikit-learn documentation
4. Contact ML Engineering Team

---

**Last Updated:** March 19, 2024  
**Version:** 1.0  
**Author:** Beige.AI ML Engineering Team
