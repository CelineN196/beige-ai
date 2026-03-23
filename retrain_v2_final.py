#!/usr/bin/env python3
"""
RETRAINING V2 MODEL FOR EXACT DEPLOYMENT ENV COMPATIBILITY
================================================================
Purpose: Rebuild V2 model using the EXACT installed package versions
         that match Streamlit Cloud deployment environment.

Key Rule: Training must happen with same versions as inference.
         No version mismatches allowed.

Versions for this training:
- scikit-learn: 1.5.1
- numpy: 1.24.3
- xgboost: 2.0.3
- pandas: 2.0.3
- joblib: 1.3.2

Output: models/v2_final_model.pkl
"""

import os
import sys
import json
import warnings
import numpy as np
import pandas as pd
from pathlib import Path

# Check installed versions
import sklearn
import numpy
import xgboost
import joblib

print("\n" + "="*70)
print("V2 MODEL RETRAINING - EXACT ENV COMPATIBILITY")
print("="*70)

print("\n[VERSIONS] Installed packages:")
print(f"  scikit-learn: {sklearn.__version__}")
print(f"  numpy: {numpy.__version__}")
print(f"  xgboost: {xgboost.__version__}")
print(f"  pandas: {pd.__version__}")
print(f"  joblib: {joblib.__version__}")

# ML imports
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, log_loss
from xgboost import XGBClassifier

warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================

RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "backend" / "data"  # Dataset is in backend/data
MODELS_DIR = BASE_DIR / "models"

# Create models directory
MODELS_DIR.mkdir(parents=True, exist_ok=True)

DATASET_PATH = DATA_DIR / "beige_ai_cake_dataset_v2.csv"

# ✅ EXPLICIT FAILURE CHECK
if not DATASET_PATH.exists():
    raise FileNotFoundError(
        f"❌ CRITICAL: Dataset not found at {DATASET_PATH}\n"
        f"   Expected: {DATASET_PATH}\n"
        f"   Please verify the data file exists in the correct location."
    )

CATEGORICAL_FEATURES = [
    'mood', 'weather_condition', 'time_of_day', 'season', 'temperature_category'
]

NUMERICAL_FEATURES = [
    'temperature_celsius', 'humidity', 'air_quality_index',
    'sweetness_preference', 'health_preference', 'trend_popularity_score',
    'comfort_index', 'environmental_score'
]

TARGET = 'cake_category'

# ============================================================================
# DATA LOADING
# ============================================================================

print(f"\n[LOAD] Loading dataset from {DATASET_PATH}...")
df = pd.read_csv(DATASET_PATH)
print(f"  ✓ Shape: {df.shape}")
print(f"  ✓ Missing values: {df.isnull().sum().sum()}")
print(f"  ✓ Target classes: {df[TARGET].nunique()}")

# ============================================================================
# PREPROCESSING
# ============================================================================

print(f"\n[PREPROCESS] Building preprocessing pipeline...")

X = df[CATEGORICAL_FEATURES + NUMERICAL_FEATURES]
y = df[TARGET]

# Encode target
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

print(f"  ✓ Classes: {list(label_encoder.classes_)}")
print(f"  ✓ Encoded mapping: {dict(zip(range(len(label_encoder.classes_)), label_encoder.classes_))}")

# Build preprocessor
preprocessor = ColumnTransformer(
    transformers=[
        ('categorical', 
         OneHotEncoder(sparse_output=False, handle_unknown='ignore'),
         CATEGORICAL_FEATURES),
        ('numerical',
         StandardScaler(),
         NUMERICAL_FEATURES)
    ],
    remainder='passthrough'
)

# Train/val/test split
X_temp, X_test, y_temp, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=RANDOM_STATE, stratify=y_encoded
)
X_train, X_val, y_train, y_val = train_test_split(
    X_temp, y_temp, test_size=0.25, random_state=RANDOM_STATE, stratify=y_temp
)

print(f"\n[SPLIT] Train/val/test split:")
print(f"  ✓ Train: {X_train.shape[0]} ({100*X_train.shape[0]/len(X):.1f}%)")
print(f"  ✓ Val:   {X_val.shape[0]} ({100*X_val.shape[0]/len(X):.1f}%)")
print(f"  ✓ Test:  {X_test.shape[0]} ({100*X_test.shape[0]/len(X):.1f}%)")

# Fit preprocessor on training data
X_train_processed = preprocessor.fit_transform(X_train)
X_val_processed = preprocessor.transform(X_val)
X_test_processed = preprocessor.transform(X_test)

# Get feature names
feature_names_cat = preprocessor.named_transformers_['categorical'].get_feature_names_out(
    CATEGORICAL_FEATURES
).tolist()
all_feature_names = feature_names_cat + NUMERICAL_FEATURES

print(f"  ✓ Features after encoding: {len(all_feature_names)}")
print(f"    - Categorical: {len(feature_names_cat)}")
print(f"    - Numerical: {len(NUMERICAL_FEATURES)}")

# ============================================================================
# MODEL TRAINING
# ============================================================================

print(f"\n[TRAIN] XGBoost with exact installed version {xgboost.__version__}...")

model = XGBClassifier(
    n_estimators=200,
    max_depth=5,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=RANDOM_STATE,
    eval_metric='mlogloss',
    verbosity=0,
    n_jobs=-1
)

model.fit(
    X_train_processed, y_train,
    eval_set=[(X_val_processed, y_val)],
    verbose=False
)

# ============================================================================
# VALIDATION
# ============================================================================

print(f"\n[VALIDATE] Model predictions on validation set...")

y_val_pred = model.predict(X_val_processed)
y_val_pred_proba = model.predict_proba(X_val_processed)

val_metrics = {
    'val_accuracy': float(accuracy_score(y_val, y_val_pred)),
    'val_f1_weighted': float(f1_score(y_val, y_val_pred, average='weighted')),
    'val_log_loss': float(log_loss(y_val, y_val_pred_proba))
}

print(f"  ✓ Validation accuracy: {val_metrics['val_accuracy']:.4f}")
print(f"  ✓ Validation F1 (weighted): {val_metrics['val_f1_weighted']:.4f}")
print(f"  ✓ Validation log loss: {val_metrics['val_log_loss']:.4f}")

print(f"\n[VALIDATE] Model predictions on test set...")

y_test_pred = model.predict(X_test_processed)
y_test_pred_proba = model.predict_proba(X_test_processed)

test_metrics = {
    'test_accuracy': float(accuracy_score(y_test, y_test_pred)),
    'test_f1_weighted': float(f1_score(y_test, y_test_pred, average='weighted')),
    'test_log_loss': float(log_loss(y_test, y_test_pred_proba))
}

print(f"  ✓ Test accuracy: {test_metrics['test_accuracy']:.4f}")
print(f"  ✓ Test F1 (weighted): {test_metrics['test_f1_weighted']:.4f}")
print(f"  ✓ Test log loss: {test_metrics['test_log_loss']:.4f}")

# Verify predict_proba works
print(f"\n[VALIDATE] Testing predict_proba output...")
test_sample = X_val_processed[:1]
proba = model.predict_proba(test_sample)
print(f"  ✓ Proba shape: {proba.shape}")
print(f"  ✓ Proba sum across classes: {proba[0].sum():.4f} (should be ~1.0)")
print(f"  ✓ Sample probabilities: {proba[0][:3]}")

# ============================================================================
# SAVE ARTIFACTS
# ============================================================================

print(f"\n[SAVE] Saving all artifacts...")

# Save unified final model to standardized location
model_path = MODELS_DIR / "model.pkl"
joblib.dump({
    'model': model,
    'preprocessor': preprocessor,
    'label_encoder': label_encoder,
    'feature_names': all_feature_names,
    'categorical_features': CATEGORICAL_FEATURES,
    'numerical_features': NUMERICAL_FEATURES,
    'metrics': {**val_metrics, **test_metrics},
    'training_env': {
        'sklearn_version': sklearn.__version__,
        'xgboost_version': xgboost.__version__,
        'numpy_version': numpy.__version__,
        'pandas_version': pd.__version__,
        'joblib_version': joblib.__version__
    }
}, model_path)

print(f"  ✓ Model saved: {model_path}")
print(f"    Size: {model_path.stat().st_size / 1024 / 1024:.2f} MB")

# Also save individual artifacts for debugging (optional)
joblib.dump(model, MODELS_DIR / "v2_xgboost_model.pkl")
joblib.dump(preprocessor, MODELS_DIR / "v2_preprocessor.pkl")
joblib.dump(label_encoder, MODELS_DIR / "v2_label_encoder.pkl")

# Save metadata
with open(MODELS_DIR / "v2_metadata.json", 'w') as f:
    json.dump({
        'feature_names': all_feature_names,
        'categorical_features': CATEGORICAL_FEATURES,
        'numerical_features': NUMERICAL_FEATURES,
        'metrics': {**val_metrics, **test_metrics},
        'training_env': {
            'sklearn_version': sklearn.__version__,
            'xgboost_version': xgboost.__version__,
            'numpy_version': numpy.__version__,
            'pandas_version': pd.__version__,
            'joblib_version': joblib.__version__
        }
    }, f, indent=2)

# ============================================================================
# LOAD & VERIFY
# ============================================================================

print(f"\n[VERIFY] Loading saved model to verify compatibility...")

try:
    loaded = joblib.load(model_path)
    loaded_model = loaded['model']
    loaded_preprocessor = loaded['preprocessor']
    loaded_encoder = loaded['label_encoder']

    # Test with same validation sample
    test_val = X_val_processed[:5]
    predictions = loaded_model.predict(test_val)
    probas = loaded_model.predict_proba(test_val)

    print(f"  ✓ Model loaded successfully from {model_path}")
    print(f"  ✓ Predictions shape: {predictions.shape}")
    print(f"  ✓ Probabilities shape: {probas.shape}")
    print(f"  ✓ Sample predictions: {predictions[:3]}")
    print(f"  ✓ Training env from disk:")
    print(f"    - sklearn: {loaded['training_env']['sklearn_version']}")
    print(f"    - xgboost: {loaded['training_env']['xgboost_version']}")
    print(f"    - numpy: {loaded['training_env']['numpy_version']}")
    print(f"\n✅ MODEL SAVED AND VERIFIED SUCCESSFULLY")
except Exception as e:
    print(f"  ❌ CRITICAL: Model load verification failed!")
    print(f"     Error: {str(e)}")
    raise

# ============================================================================
# FINAL SUMMARY
# ============================================================================

print("\n" + "="*70)
print("✅ V2 MODEL RETRAINING COMPLETE")
print("="*70)

print(f"\n📊 FINAL PERFORMANCE METRICS:")
print(f"  Validation Accuracy: {val_metrics['val_accuracy']:.4f}")
print(f"  Test Accuracy:       {test_metrics['test_accuracy']:.4f}")
print(f"  Test F1 (weighted):  {test_metrics['test_f1_weighted']:.4f}")

print(f"\n📦 PRODUCTION MODEL SAVED TO:")
print(f"  → {model_path}")

print(f"\n🔒 ENVIRONMENT LOCKED IN:")
print(f"  scikit-learn: {sklearn.__version__}")
print(f"  xgboost: {xgboost.__version__}")
print(f"  numpy: {numpy.__version__}")
print(f"  pandas: {pd.__version__}")
print(f"  joblib: {joblib.__version__}")

print(f"\n✨ Model is DEPLOYMENT READY for Streamlit Cloud\n")
