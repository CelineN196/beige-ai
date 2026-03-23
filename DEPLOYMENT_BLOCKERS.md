## DEPLOYMENT AUDIT - CRITICAL FINDINGS

**Status:** ⚠️ NOT PRODUCTION READY (2 Critical Blockers)

---

## BLOCKERS FOUND

### 1. 🔴 XGBoost Missing from requirements.txt
**Impact:** V2 model will NOT load on Streamlit Cloud  
**Why:** joblib.load() tries to unpickle XGBClassifier → ModuleNotFoundError  
**Current:** requirements.txt has NO xgboost  
**Fix:** Add `xgboost` to requirements.txt  

### 2. 🔴 scikit-learn Unpinned (Version Mismatch)
**Impact:** V2 model may crash at prediction time  
**Why:** Trained with 1.5.1, but requirements.txt auto-resolves to latest  
**Risk:** Tree structure incompatibility if Streamlit Cloud installs 1.6+  
**Fix:** Pin `scikit-learn==1.5.1` in requirements.txt  

---

## WHAT'S WORKING ✅

| Component | Status | Notes |
|-----------|--------|-------|
| Feature Schema | ✅ Perfect | 13 features consistent (training vs inference) |
| Safe Fallback | ✅ Implemented | V2→V1 fallback works correctly |
| Model Container | ✅ Unified | v2_final_model.pkl includes all components |
| Metadata Locking | ✅ Yes | Training env pinned (sklearn 1.5.1, xgboost 2.0.3, etc.) |
| Input Validation | ✅ Yes | Shape checks in place |
| V1 Fallback Models | ✅ Present | All files exist |

---

## WHAT'S BROKEN ❌

| Issue | Severity | Detection | Consequence |
|-------|----------|-----------|-------------|
| XGBoost dependency | CRITICAL | Import error | Model unpickle fails |
| scikit-learn pin | CRITICAL | Runtime crash | predict_proba() AttributeError |
| NumPy/Pandas versions | MEDIUM | Silent degradation | Feature shape skew (mitigated) |

---

## RISK ASSESSMENT

**If deployed WITHOUT fixes:**
```
Streamlit Cloud installs requirements
→ No xgboost package
→ joblib.load() fails on line 328 of app
→ Try fallback to V1 model
→ App runs on V1 only (78.58% accuracy lost)

OR (if xgboost somehow installed):

→ scikit-learn 1.6+ installed (not 1.5.1)
→ V2 model loads
→ predict_proba() crashes: AttributeError: monotonic_cst
→ Fallback to V1
→ App runs on V1 only
```

**If deployed WITH fixes:**
```
Streamlit Cloud installs requirements WITH xgboost + sklearn 1.5.1
→ V2 model loads successfully
→ V2 predictions run (78.58% accuracy)
→ Full system works as designed
```

---

## REQUIRED ACTIONS

### MUST DO (Before Deployment)

**Update requirements.txt:**

Add these two lines:
```diff
  streamlit
  pandas
  numpy
+ scikit-learn==1.5.1
+ xgboost
  joblib
  pillow
  matplotlib
  google-generativeai
```

**Then:**
```bash
git add requirements.txt
git commit -m "Add xgboost + pin scikit-learn 1.5.1 for V2 model deployment"
git push
```

### SHOULD DO (Risk Reduction)

**Optional: Pin NumPy & Pandas ranges**
```diff
- pandas
- numpy
+ pandas>=2.0,<2.5
+ numpy>=1.24,<2.0
```

---

## DEPLOYMENT READINESS

**Before Fixes:**
```
Feature Schema:        ✅
Safe Fallback:         ✅
Model Container:       ✅
Dependencies:          ❌ BLOCKING
Version Locks:         ❌ BLOCKING
Overall:               🔴 NOT READY
```

**After Fixes:**
```
Feature Schema:        ✅
Safe Fallback:         ✅
Model Container:       ✅
Dependencies:          ✅
Version Locks:         ✅
Overall:               🟢 READY FOR DEPLOYMENT
```

---

## ROOT CAUSE

When scikit-learn==1.3.2 was removed (commit 3f66069) to fix Python 3.14.3 wheel issues, the requirement became unpinned. Then V2 was retrained with sklearn 1.5.1. But requirements.txt wasn't re-locked, so there's now a mismatch.

Additionally, xgboost was never added to requirements, creating a missing-dependency bug.

---

**Audit Date:** March 22, 2026  
**Audit Type:** Structural (NO code changes, deployment hardening only)  
**Severity:** BLOCKING (must fix before Streamlit Cloud deployment)
