# Quick Reference: Model Comparison Pipeline

## 🚀 Quick Start (30 seconds)

```bash
# 1. Navigate to training directory
cd backend/training

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the pipeline
python compare_models.py
```

## 📊 What Gets Compared

| Model | Type | Best For | Training Time |
|-------|------|----------|----------------|
| **Decision Tree** | Single Tree | Interpretability | Fast (seconds) |
| **Random Forest** | Ensemble (Bagging) | Balance & Stability | Medium (1-2 min) |
| **Gradient Boosting** | Ensemble (Boosting) | Maximum Accuracy | Slow (2-5 min) |

## 🎯 Selection Logic

The pipeline **automatically selects the best model** using F1-weighted score:

```
Compare F1-Scores →→ Pick Highest →→ Save Best Model
```

## 📈 Key Metrics Explained

**F1-Score** (decides winner) - Harmonic mean of precision & recall
- Range: 0.0 to 1.0
- Higher is better
- 0.85+ = Excellent

**Accuracy** - Percentage of correct predictions
- Can be misleading with imbalanced classes

**Precision** - "When model says YES, how often is it right?"
- Critical when false positives are costly

**Recall** - "How many actual positives did we find?"
- Critical when false negatives are costly

## 📁 Output Files

**After running, you'll have:**

```
backend/models/
├── best_model.joblib          # ← Use this for predictions
└── feature_info.joblib        # ← Metadata & features

docs/
├── MODEL_TRAINING_REPORT.md   # ← Full analysis report
└── confusion_matrix_*.png     # ← Visual breakdown
```

## 💻 Using the Best Model

```python
import joblib

# Load the trained model
model = joblib.load('backend/models/best_model.joblib')

# Load metadata
info = joblib.load('backend/models/feature_info.joblib')

# Make predictions
features = [[2, 3.14, 1, 0]]  # Preprocessed features
prediction = model.predict(features)[0]
confidence = model.predict_proba(features)[0].max()

print(f"Prediction: {info['target_classes'][prediction]}")
print(f"Confidence: {confidence:.2%}")
```

## ⚙️ Hyperparameter Tuning Summary

**Decision Tree:**
- Tests: max_depth, min_samples_split, min_samples_leaf
- Goal: Find optimal tree depth & split criteria

**Random Forest:**
- Tests: n_estimators, max_depth, min_samples_split
- Goal: Balance ensemble size with tree constraints

**Gradient Boosting:**
- Tests: n_estimators, learning_rate, max_depth
- Goal: Balance boosting rate with tree complexity

**Method:** RandomizedSearchCV (5-fold cross-validation)

## 🔍 Interpreting Results

```
✅ SELECTED MODEL: Random Forest (F1: 0.8567)
   • Accuracy: 0.8412
   • Precision: 0.8521
   • Recall: 0.8634
```

**What This Means:**
- Model correctly classifies **84.1%** of all samples
- When it predicts a class, it's **85.2%** correct (precision)
- It finds **86.3%** of true positives (recall)
- **F1-score of 0.8567 = Excellent performance**

## 🚨 Troubleshooting

**"ModuleNotFoundError: No module named 'sklearn'"**
```bash
→ pip install scikit-learn
```

**"FileNotFoundError: dataset not found"**
```bash
→ Check that beige_ai_cake_dataset_v2.csv exists in backend/data/
```

**"Low accuracy on test data"**
```bash
→ Check data quality
→ Add more training samples
→ Engineer more relevant features
→ Increase hyperparameter search space
```

## 📋 Model Comparison Table

After running, you'll see a comparison table:

| Model | Accuracy | Precision | Recall | F1-Score |
|-------|----------|-----------|--------|----------|
| Decision Tree | 0.82 | 0.81 | 0.82 | 0.8165 |
| Random Forest | 0.84 | 0.85 | 0.86 | **0.8567** ✅ |
| Gradient Boosting | 0.83 | 0.84 | 0.83 | 0.8340 |

**Winner:** Random Forest (highest F1-score)

## ⏱️ Expected Runtime

- **Decision Tree:** ~30 seconds
- **Random Forest:** ~90 seconds
- **Gradient Boosting:** ~120 seconds
- **Total:** ~4 minutes

*(Times vary by dataset size and hardware)*

## 📊 Understanding the Confusion Matrix

```
                Predicted
            Cake A  Cake B  Cake C
    Cake A   45      5      0
    Cake B    2     48      0
    Cake C    1      2     47
```

**Diagonal = Correct predictions**
**Off-diagonal = Errors (which classes are confused)**

Higher numbers on diagonal = Better model

## 🎓 Learning Resources

1. **F1-Score:** https://en.wikipedia.org/wiki/F-score
2. **Confusion Matrix:** https://en.wikipedia.org/wiki/Confusion_matrix
3. **Hyperparameter Tuning:** https://scikit-learn.org/stable/modules/grid_search.html
4. **Tree-Based Models:** https://scikit-learn.org/stable/modules/tree.html

## 🔄 Retraining Checklist

When to retrain the model:
- [ ] Monthly scheduled retraining
- [ ] New training data available
- [ ] Performance drops >2% on new data
- [ ] Feature distribution changes
- [ ] Business requirements change

## 📞 Next Steps

1. ✅ Review MODEL_TRAINING_REPORT.md for detailed analysis
2. ✅ Examine confusion matrix for error patterns
3. ✅ Check feature importance from Random Forest
4. ✅ Deploy best model to production
5. ✅ Set up monitoring for real-world performance

---

**Last Updated:** March 19, 2024
