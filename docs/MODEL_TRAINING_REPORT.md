# Beige.AI Model Training Report

**Generated:** 2026-03-19 21:32:53  
**Report Version:** 1.0

---

## Executive Summary

This report documents the training, hyperparameter tuning, and evaluation of three classification models for the Beige.AI cake recommendation system:

1. **Decision Tree**
2. **Random Forest**
3. **Gradient Boosting**

All models were trained on 4 different architectures using **RandomizedSearchCV with 5-fold cross-validation**, optimizing for **F1-weighted score** to account for potential class imbalance.

---

## Model Comparison

### Summary Table

| Model | Accuracy | Precision | Recall | F1-Score |
|-------|----------|-----------|--------|----------|
| Decision Tree | 0.7886 | 0.7964 | 0.7886 | 0.7879 |
| Random Forest | 0.7864 | 0.7752 | 0.7864 | 0.7796 |
| Gradient Boosting | 0.7886 | 0.7823 | 0.7886 | 0.7832 |
| XGBoost | 0.7934 | 0.7905 | 0.7934 | 0.7891 |

### Best Model: **XGBoost**

The **XGBoost** model achieved the highest F1-score of **0.7891**, making it the recommended model for production deployment.

---

## Detailed Model Analysis

### 1. Decision Tree

**Hyperparameter Tuning Space:**
- `max_depth`: [3, 5, 7, 10, 15, 20, None]
- `min_samples_split`: [2, 5, 10, 20]
- `min_samples_leaf`: [1, 2, 4, 8]

**Best Parameters:**
```python
{'ccp_alpha': 0.0, 'class_weight': None, 'criterion': 'gini', 'max_depth': 7, 'max_features': None, 'max_leaf_nodes': None, 'min_impurity_decrease': 0.0, 'min_samples_leaf': 4, 'min_samples_split': 2, 'min_weight_fraction_leaf': 0.0, 'random_state': 42, 'splitter': 'best'}
```

**Performance Metrics:**
- Accuracy: 0.7886
- Precision: 0.7964
- Recall: 0.7886
- F1-Score: 0.7879

### 2. Random Forest

**Hyperparameter Tuning Space:**
- `n_estimators`: [50, 100, 200, 300]
- `max_depth`: [5, 10, 15, 20, None]
- `min_samples_split`: [2, 5, 10]
- `min_samples_leaf`: [1, 2, 4]

**Best Parameters:**
```python
{'bootstrap': True, 'ccp_alpha': 0.0, 'class_weight': None, 'criterion': 'gini', 'max_depth': None, 'max_features': 'sqrt', 'max_leaf_nodes': None, 'max_samples': None, 'min_impurity_decrease': 0.0, 'min_samples_leaf': 1, 'min_samples_split': 10, 'min_weight_fraction_leaf': 0.0, 'n_estimators': 100, 'n_jobs': None, 'oob_score': False, 'random_state': 42, 'verbose': 0, 'warm_start': False}
```

**Performance Metrics:**
- Accuracy: 0.7864
- Precision: 0.7752
- Recall: 0.7864
- F1-Score: 0.7796

### 3. Gradient Boosting

**Hyperparameter Tuning Space:**
- `n_estimators`: [50, 100, 200]
- `learning_rate`: [0.01, 0.05, 0.1, 0.15]
- `max_depth`: [3, 5, 7, 10]

**Best Parameters:**
```python
{'ccp_alpha': 0.0, 'criterion': 'friedman_mse', 'init': None, 'learning_rate': 0.1, 'loss': 'log_loss', 'max_depth': 5, 'max_features': None, 'max_leaf_nodes': None, 'min_impurity_decrease': 0.0, 'min_samples_leaf': 1, 'min_samples_split': 2, 'min_weight_fraction_leaf': 0.0, 'n_estimators': 50, 'n_iter_no_change': None, 'random_state': 42, 'subsample': 1.0, 'tol': 0.0001, 'validation_fraction': 0.1, 'verbose': 0, 'warm_start': False}
```

**Performance Metrics:**
- Accuracy: 0.7886
- Precision: 0.7823
- Recall: 0.7886
- F1-Score: 0.7832

---

## Classification Report (Best Model: XGBoost)

```
                              precision    recall  f1-score   support

           Berry Garden Cake       0.46      0.44      0.45       206
               Café Tiramisu       0.68      0.58      0.63      1426
           Citrus Cloud Cake       0.37      0.29      0.32       196
Dark Chocolate Sea Salt Cake       0.86      0.92      0.89      3945
        Earthy Wellness Cake       0.41      0.47      0.44       259
    Korean Sesame Mini Bread       0.90      0.95      0.92      2182
             Matcha Zen Cake       0.80      0.65      0.72      1540
             Silk Cheesecake       0.36      0.47      0.41       246

                    accuracy                           0.79     10000
                   macro avg       0.60      0.60      0.60     10000
                weighted avg       0.79      0.79      0.79     10000

```

---

## Confusion Matrix

![Confusion Matrix](docs/confusion_matrix_xgboost.png)

---

## Key Insights

### Model Performance Analysis

1. **XGBoost Performance**
   - Highest F1-Score: 0.7891
   - Strong across precision and recall
   - Recommended for production use

2. **Relative Strengths:**
   - **Decision Tree**: Interpretability, fast inference
   - **Random Forest**: Ensemble robustness, feature importance
   - **Gradient Boosting**: Iterative optimization, complex patterns

3. **Trade-offs:**
   - Decision Tree: Simple but may underfit
   - Random Forest: Good balance of accuracy and speed
   - Gradient Boosting: Highest complexity, may require careful tuning

---

## Recommendations

### Immediate Actions
1. ✅ **Deploy XGBoost** to production
2. ✅ Monitor performance on real-world data
3. ✅ Set up regular retraining schedule (monthly recommended)

### Future Improvements
1. Incorporate additional features (customer history, seasonal trends)
2. Implement ensemble voting (combine multiple models)
3. Add class-weight balancing for imbalanced classes
4. Perform hyperparameter grid search for final fine-tuning
5. Implement A/B testing to validate production performance

### Model Maintenance
- **Retraining Frequency**: Monthly or when F1-score drops >2%
- **Versioning**: Keep model snapshots for rollback capability
- **Monitoring**: Track accuracy, precision, recall in production
- **Feature Drift**: Monitor input feature distributions

---

## Technical Details

### Data Statistics
- **Total Samples**: 0
- **Training Samples**: 0
- **Test Samples**: 0
- **Number of Classes**: 8
- **Class Labels**: Berry Garden Cake, Café Tiramisu, Citrus Cloud Cake, Dark Chocolate Sea Salt Cake, Earthy Wellness Cake, Korean Sesame Mini Bread, Matcha Zen Cake, Silk Cheesecake

### Hyperparameter Tuning Method
- **Method**: RandomizedSearchCV
- **Cross-Validation Folds**: 5
- **Scoring Metric**: F1-weighted
- **Iterations per Model**: 20

### Training Environment
- **Python Version**: 3.9.6
- **scikit-learn**: 2.0.3
- **Random Seed**: 42 (reproducibility)

---

## Files Generated

- ✅ `best_model.joblib` - Best trained model
- ✅ `feature_info.joblib` - Feature metadata & preprocessing info
- ✅ `confusion_matrix_*.png` - Confusion matrix visualization
- ✅ `MODEL_TRAINING_REPORT.md` - This report

---

## Appendix: Model Selection Rationale

The **XGBoost** model was selected based on:

1. **F1-Score**: 0.7891 (highest among all candidates)
2. **Balanced Performance**: Strong precision (0.7905) and recall (0.7934)
3. **Production Readiness**: Fast inference time, stable predictions
4. **Explainability**: Can extract feature importance for business insights

---

**Report Generated by**: Beige.AI ML Engineering Team  
**Next Review Date**: 2026-04-19

