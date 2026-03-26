# 🚀 Model Diagnostics - Quick Start Guide

## 30-Second Setup

```bash
# Run basic analysis (15 seconds)
python analysis/model_diagnostics.py

# Run with clustering elbow curve (3 minutes)
python analysis/model_diagnostics.py --kmeans --plot
```

## What You'll See

### ✅ Basic Run Output

```
📥 LOADING DATA & PREPROCESSING
✓ Loaded: 50,000 samples, 14 columns
✓ After preprocessing: 29 features

📊 FEATURE VALIDATION
✓ Shape: (50000, 29)
✓ Missing Values: 0 total
✓ No NaN values detected

🎯 MODEL PERFORMANCE ANALYSIS
✓ Accuracy: 0.7493 (74.93%)
✓ F1-Score (weighted): 0.7323
✓ Avg Confidence: 0.8338

⭐ FEATURE IMPORTANCE (XGBoost)
Top 20 Most Important Features:
[Feature rankings]

🔮 SAMPLE PREDICTIONS
Sample Accuracy: 13/15 (86.67%)

🔄 CLUSTER DISTRIBUTION (K=5)
✓ Cluster Distribution:
[5 roughly balanced clusters]

✅ DIAGNOSTICS COMPLETE
```

## Files in analysis/ Directory

```
analysis/
├── model_diagnostics.py      ← Main script (619 lines)
├── README.md                 ← Full documentation
├── QUICKSTART.md             ← This file
└── elbow_curve.png           ← Generated (with --plot flag)
```

## Command Reference

| Command | Time | Output |
|---------|------|--------|
| `python analysis/model_diagnostics.py` | ~15s | Console output only |
| `python analysis/model_diagnostics.py --plot` | ~15s | Same + elbow_curve.png |
| `python analysis/model_diagnostics.py --kmeans` | ~2m | Same + elbow analysis |
| `python analysis/model_diagnostics.py --kmeans --plot` | ~3m | All sections + visualization |

## Key Metrics Explained

### Accuracy: 74.93%
- Model gets 74.93% of predictions correct
- Good baseline for 8-class chocolate recommendation
- Room for improvement but acceptable for production

### F1-Score: 0.7323
- Balance between precision and recall
- Weighted F1 accounts for class imbalance
- Higher is better (0-1 scale)

### Confidence Distribution
```
Very High (>0.9):  26,592 (53.18%)  ← Model very sure
High (0.8-0.9):    8,281 (16.56%)   ← Model confident
Medium (0.7-0.8):  3,102 (6.20%)    ← Model somewhat sure
Low (<0.7):        12,025 (24.05%)  ← Model uncertain
```

Interpretation:
- ✅ 53% of predictions are highly confident
- ⚠️ 24% lack confidence (these may be error-prone)
- 💡 Good opportunity to flag low-confidence predictions to user

### Feature Importance

Feature_12 is most important (13.41% of tree splits)
- Top 5 features drive 51.47% of model decisions
- Other 24 features: supporting roles

### Sample Predictions

Shows 15 examples:
- ✓ = Correct prediction
- ✗ = Wrong prediction (86.67% accuracy on sample)

### Cluster Distribution

K=5 clusters:
- Cluster 0: 8,988 (17.98%)
- Cluster 1: 10,253 (20.51%)
- Cluster 2: 7,664 (15.33%)
- Cluster 3: 12,350 (24.70%)
- Cluster 4: 10,745 (21.49%)

All roughly balanced = good feature diversity

## Troubleshooting

**Q: Script says "Model not found"?**
A: Model path issue. Check `models/v2_xgboost_model.pkl` exists.

**Q: Why does --kmeans take so long?**
A: KMeans on 50K samples is computationally expensive. Normal: 1-3 minutes.

**Q: Can I use this during development?**
A: Yes! Perfect for iterate development. Run after each model retrain.

**Q: What if all metrics are bad?**
A: Check feature validation section for data quality issues first.

## Common Analysis Workflows

### 👀 Quick Data Health Check (30 seconds)
```bash
python analysis/model_diagnostics.py | grep -E "✓|✅|Accuracy"
```
→ Check for NaN, feature ranges, basic metrics

### 📊 Model Investigation (15 seconds)
```bash
python analysis/model_diagnostics.py
```
→ Full diagnostics - accuracy, confidence, sample predictions

### 🔬 Deep Dive Analysis (3+ minutes)
```bash
python analysis/model_diagnostics.py --kmeans --plot
```
→ Everything + cluster structure investigation

### 🎯 Feature Importance Focus (15 seconds)
```bash
python analysis/model_diagnostics.py | grep -A 25 "FEATURE IMPORTANCE"
```
→ Which features drive predictions

## Next Steps

1. **After First Run:**
   - Review feature validation section (any NaNs? outliers?)
   - Check if accuracy is acceptable for your use case
   - Note which features are most important

2. **For Improvement:**
   - If accuracy < 75%: Review feature engineering
   - If confidence low: May need more training data
   - If clusters imbalanced: Check data collection process

3. **Ongoing Monitoring:**
   - Run after each model retrain
   - Track accuracy trends over time
   - Monitor for feature importance shifts

## Examples

### Example 1: Check Data Health After Upload
```bash
$ python analysis/model_diagnostics.py

✓ Missing Values: 0 total  ✅
✓ Infinite Values: 0 total ✅
✓ No NaN values detected   ✅

→ Data is clean! No preprocessing issues.
```

### Example 2: Find Why Predictions Are Wrong
```bash
$ python analysis/model_diagnostics.py | grep -A 18 "SAMPLE PREDICTIONS"

✗ Sample Accuracy: 13/15 (86.67%)

→ 13 out of 15 correct. Check which 2 were wrong in the output.
```

### Example 3: Learn Model's Feature Usage
```bash
$ python analysis/model_diagnostics.py | grep -A 3 "Top 5 features"

✓ Top 5 features account for 51.47% of importance

→ Model relies heavily on top features. Others have minimal impact.
```

## Performance Notes

- First run: ~15 seconds (data loading + analysis)
- Subsequent runs: ~15 seconds (no caching)
- With --kmeans: Add 1-3 minutes per run
- RAM usage: ~500MB (Python + numpy + data)
- Disk space: ~3MB for elbow_curve.png

## Integration with Development

This script is **completely standalone**:
- ✅ Doesn't modify Streamlit app
- ✅ Doesn't retrain models
- ✅ Doesn't require API
- ✅ Can run without internet
- ✅ Safe to run at any time

Perfect for:
- After model retraining → verify quality
- During feature engineering → test impact
- Before deployment → final health check
- Debugging user issues → replay data

## File Locations

```
/Users/queenceline/Downloads/Beige AI/
├── analysis/
│   ├── model_diagnostics.py     ← Main script
│   ├── README.md                ← Full guide
│   └── elbow_curve.png          ← Generated plot (--plot flag)
│
├── backend/data/
│   └── beige_ai_cake_dataset_v2.csv  ← Data source
│
├── models/
│   ├── v2_final_model.pkl       ← Fallback model
│   └── v2_xgboost_model.pkl     ← Primary model
│
└── backend/training/
    └── train_v2_pipeline.py     ← Retrain here if needed
```

---

**Ready to analyze?** Run: `python analysis/model_diagnostics.py` 🚀
