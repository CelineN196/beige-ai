## DEPLOYMENT STABILITY ARCHITECTURE AUDIT

**Date:** March 22, 2026  
**Status:** ⚠️ CRITICAL ISSUES IDENTIFIED

---

## 1. VERSION CONSISTENCY CHECK

### Training Environment (Locked in v2_metadata.json)
```
scikit-learn: 1.5.1 ✓ PINNED
xgboost: 2.0.3 ✓ PINNED
numpy: 1.24.3 ✓ PINNED
pandas: 2.0.3 ✓ PINNED
joblib: 1.3.2 ✓ PINNED
```

### Inference Environment (requirements.txt)
```
streamlit (unpinned)
pandas (unpinned)
numpy (unpinned)
scikit-learn (unpinned) ⚠️
joblib (unpinned)
pillow (unpinned)
matplotlib (unpinned)
google-generativeai (unpinned)
xgboost ❌ MISSING
```

### Version Mismatch Risks

| Package | Trained | Deployed | Risk |
|---------|---------|----------|------|
| scikit-learn | 1.5.1 | Auto-resolve | 🔴 CRITICAL |
| xgboost | 2.0.3 | NOT INSTALLED | 🔴 CRITICAL |
| numpy | 1.24.3 | Auto-resolve | 🟡 MEDIUM |
| pandas | 2.0.3 | Auto-resolve | 🟡 MEDIUM |

---

## 2. MODEL ARTIFACT AUDIT

### V2 Final Model Structure
✅ **Location:** `models/v2_final_model.pkl` (3.2 MB)

**Unified Container Contents:**
```python
{
    'model': XGBClassifier(...),
    'preprocessor': ColumnTransformer(...),
    'label_encoder': LabelEncoder(...),
    'feature_names': [29 feature names],
    'categorical_features': [5 features],
    'numerical_features': [8 features],
    'metrics': {...},
    'training_env': {
        'sklearn_version': '1.5.1',
        'xgboost_version': '2.0.3',
        ...
    }
}
```

✅ **Preprocessor Included:** YES  
✅ **Label Encoder Included:** YES  
✅ **Feature Schema Locked:** YES  
✅ **Training Env Metadata:** YES  

### V1 Fallback Models
✅ `cake_model.joblib` (4.0 MB) — Exists  
✅ `preprocessor.joblib` (1.9 KB) — Exists  
✅ `feature_info.joblib` (564 B) — Exists  

---

## 3. INFERENCE SAFETY CHECK

### Model Loading (frontend/beige_ai_app.py)

**load_model_safe() Flow:**
```python
try:
    load v2_final_model.pkl → extract['model'] → return with "V2"
except Exception:
    fallback to cake_model.joblib → return with "V1"
except Exception:
    FATAL ERROR
```

✅ **Safe fallback present:** YES  
✅ **Try/except wrapping:** YES  
✅ **Error messaging:** YES  

### Preprocessor Loading

**load_preprocessor_safe() Flow:**
```python
try:
    load v2_final_model.pkl → extract['preprocessor'] → return "V2"
except Exception:
    fallback to preprocessor.joblib → return "V1"
```

✅ **Safe fallback present:** YES  
✅ **Unified extraction:** YES  

### Label Encoder Loading

**load_label_encoder() Flow:**
```python
try:
    load v2_final_model.pkl → extract['label_encoder']
except Exception:
    return None (graceful degrade)
```

✅ **Graceful degradation:** YES  

### Input Shape Validation

**Validation Code (lines 1432-1437):**
```python
expected_features = len(preprocessor.get_feature_names_out())
if X_processed.shape[1] != expected_features:
    raise ValueError(f"Expected {expected_features}, got {X_processed.shape[1]}")
```

✅ **Shape validation present:** YES  
✅ **Runs post-preprocessing:** YES (potential issue - see below)  

---

## 4. FEATURE PIPELINE CONSISTENCY

### Training Feature Schema (from training script)

**Categorical (5):**
1. `mood` (5 values: Happy, Stressed, Tired, Lonely, Celebratory)
2. `weather_condition` (5 values: Sunny, Rainy, Cloudy, Snowy, Stormy)
3. `time_of_day` (4 values: Morning, Afternoon, Evening, Night)
4. `season` (4 values: Winter, Spring, Summer, Autumn)
5. `temperature_category` (3 values: cold, mild, hot)

**Numerical (8):**
1. `temperature_celsius` (continuous)
2. `humidity` (0-100 %)
3. `air_quality_index` (continuous)
4. `sweetness_preference` (1-10 scale)
5. `health_preference` (1-10 scale)
6. `trend_popularity_score` (continuous)
7. `comfort_index` (computed from mood + weather)
8. `environmental_score` (computed from temp + humidity + AQI)

### Inference Feature Schema (from frontend input construction, lines 1402-1417)

DataFrame columns in exact order:
```python
{
    'mood': [user selection],
    'weather_condition': [session state],
    'temperature_celsius': [slider value],
    'humidity': [slider value],
    'air_quality_index': [slider value],
    'time_of_day': [session state],
    'sweetness_preference': [slider value],
    'health_preference': [slider value],
    'trend_popularity_score': [0.5 constant],
    'temperature_category': [computed from temp],
    'comfort_index': [computed from mood + weather],
    'environmental_score': [computed from temp + humidity + AQI],
    'season': [derived from datetime.now()]
}
```

### Schema Consistency Check

✅ **All 13 features present in inference:** YES  
✅ **Feature names match training:** YES  
✅ **Column order** (doesn't matter for ColumnTransformer): Correct  
✅ **Feature types** (categorical vs numerical): Correct  

**Encoded Output (29 features after OneHotEncoding):**
- 21 categorical (5 categorical → one-hot)
- 8 numerical (unchanged)
- Total: 29 ✓ Matches metadata

---

## 5. DEPLOYMENT FAILURE POINTS

### 🔴 CRITICAL ISSUES (Will Break Deployment)

#### Issue #1: **XGBoost Missing from requirements.txt**
- **Severity:** CRITICAL
- **Current State:** V2 model uses XGBClassifier, but xgboost not in dependencies
- **Failure Mode:** On Streamlit Cloud:
  1. pip installs requirements (no xgboost)
  2. joblib.load(v2_final_model.pkl) attempts to unpickle XGBClassifier
  3. ModuleNotFoundError: No module named 'xgboost'
  4. Falls back to V1 model (correct behavior, but V2 never runs)
- **Impact:** V2 model unusable; app runs on V1 only
- **Fix Required:** Add `xgboost` to requirements.txt

#### Issue #2: **scikit-learn Version Mismatch Risk**
- **Severity:** CRITICAL
- **Current State:** Model trained with sklearn 1.5.1, but requirements says auto-resolve
- **What will Streamlit Cloud do:**
  - pip install scikit-learn (unpinned)
  - Latest version with Python 3.14.3 wheels = unknown (likely 1.6.x+)
  - If different from 1.5.1 → TreeExplainer/tree_ structure mismatch
- **Failure Mode:** Model loads but predict_proba() fails with:
  ```
  AttributeError: 'XGBClassifier' has no attribute 'monotonic_cst'
  ```
  or similar version-specific errors
- **Impact:** XGBoost predictions crash; fallback to V1
- **Fix Required:** Pin `scikit-learn==1.5.1` in requirements.txt

### 🟡 MEDIUM ISSUES (May Break Under Certain Conditions)

#### Issue #3: **numpy & pandas Version Skew**
- **Severity:** MEDIUM
- **Current State:** Trained with numpy 1.24.3, pandas 2.0.3 (unpinned)
- **Failure Mode:** If pip resolves to very different versions (e.g., numpy 2.0, pandas 2.5):
  - Array operations behave differently
  - OneHotEncoder output shape might change
  - Preprocessing input/output mismatch
- **Impact:** Preprocess could silently change feature counts
- **Risk:** Shape validation catches it, but error message is cryptic
- **Fix:** Pin or narrow-range versions (e.g., `numpy>=1.24,<2.0`)

#### Issue #4: **Preprocessor Fit/Transform Mismatch**
- **Severity:** MEDIUM (Detection: GOOD)
- **Current State:** Preprocessor fits on training data, applies OneHotEncoder
- **Failure Mode:** If a categorical value appears in inference that wasn't in training:
  - Example: weather_condition='Foggy' (not in training data)
  - OneHotEncoder(handle_unknown='ignore') drops it silently
  - Feature count stays same, but feature meaning changes
- **Detection:** Shape validation passes (29 features still)
- **Impact:** Silent feature degradation (Foggy weather becomes all-zeros)
- **Risk Level:** Moderate (edge case, but user could input unexpected values)
- **Current Mitigation:** handle_unknown='ignore' is set (reduces severity)

### 🟢 LOW ISSUES (Edge Cases)

#### Issue #5: **Model Loading at Module Level**
- **Severity:** LOW
- **Current State:** Lines 333-334 load model at app startup
- **Failure Mode:** If model file corrupted or path wrong, entire app crashes before showing error UI
- **Current Mitigation:** try/except with st.error() catches this
- **Risk:** Very low (file versioning via git should prevent this)

#### Issue #6: **Missing V1 Models on Non-Git Deployments**
- **Severity:** LOW-MEDIUM
- **Current State:** V1 fallback requires cake_model.joblib, preprocessor.joblib
- **Failure Mode:** If repo cloned without .gitignore excluding models/:
  - V1 models might be missing
  - V2 fails → fallback fails → app crashes
- **Current Status:** All models verified to exist
- **Risk:** Only if git clone is incomplete

---

## 6. ARCHITECTURE SUMMARY

### What IS Stable ✅

1. **Feature Schema:** Perfectly consistent (13 features, all names/types match)
2. **Safe Fallback Logic:** V2→V1 fallback implemented correctly
3. **Unified Model Container:** v2_final_model.pkl contains everything needed
4. **Metadata Locking:** Training env pinned in JSON
5. **Input Validation:** Shape checks in place
6. **V1 Fallback Models:** All present and accessible

### What IS NOT Stable ❌

1. **Missing XGBoost Dependency** (CRITICAL)
2. **Unpinned Scikit-learn** (CRITICAL)
3. **Unpinned NumPy/Pandas** (MEDIUM)
4. **Categorical Edge Cases** (LOW-MEDIUM, with mitigation)

---

## 7. REQUIRED FIXES (STRUCTURAL ONLY)

### MUST DO (For Deployment Success)

**Fix #1: Add xgboost to requirements.txt**
```
Current:
streamlit
pandas
numpy
scikit-learn
joblib
...

New:
streamlit
pandas
numpy
scikit-learn==1.5.1
xgboost
joblib
...
```
**Why:** XGBoost model unpickling will fail without xgboost installed  
**Urgency:** BEFORE DEPLOYMENT

**Fix #2: Pin scikit-learn==1.5.1**
```
Current: scikit-learn
New:     scikit-learn==1.5.1
```
**Why:** Model trained with 1.5.1, auto-resolve will cause version mismatch  
**Urgency:** BEFORE DEPLOYMENT

### SHOULD DO (Risk Reduction)

**Fix #3: Pin numpy and pandas with ranges**
```
numpy>=1.24,<2.0
pandas>=2.0,<2.5
```
**Why:** Prevent silent feature count changes from major version jumps  
**Urgency:** BEFORE DEPLOYMENT (optional but highly recommended)

---

## 8. DEPLOY SAFE CHECKLIST

```
✅ Feature schema consistent (training vs inference)
✅ Safe fallback logic implemented
✅ Model container unified
✅ Metadata locked in JSON
✅ V1 fallback models exist
✅ Input validation in place
❌ XGBoost in dependencies
❌ scikit-learn pinned
⚠️ NumPy/Pandas pinned

OVERALL STATUS: NOT PRODUCTION READY
BLOCKER: XGBoost missing + scikit-learn unpinned
```

---

## 9. SUMMARY FOR NEXT STEPS

**Current State:** V2 model built perfectly, but dependency specification incomplete.

**Result if deployed AS-IS:**
- XGBoost import fails silently during model loading
- App falls back to V1 RandomForest
- App runs on V1 only (working, but V2 never executes)
- OR scikit-learn version mismatch causes runtime crash

**Result if fixes applied:**
- XGBoost and scikit-learn 1.5.1 installed
- V2 model loads and runs successfully
- Full 78.58% accuracy available
- Robust deployment

**Time to Fix:** ~5 minutes (2 lines to requirements.txt)

---

**Generated:** March 22, 2026 (Post-V2 Retrain Audit)
