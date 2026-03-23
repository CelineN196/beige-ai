"""
Beige.AI Phase 3: Machine Learning Pipeline (Simplified)
================================================================
Train, evaluate, and save ML models that predict cake category.

Simplified version focusing on Decision Tree and Random Forest.

Author: Senior Machine Learning Engineer
Date: March 2026
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split, RandomizedSearchCV, cross_val_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, 
    classification_report, 
    confusion_matrix
)
import sklearn
import joblib
import warnings
import os
import sys
from pathlib import Path

# Add frontend directory to path to import menu_config
_FRONTEND_DIR = str(Path(__file__).resolve().parent.parent.parent / "frontend")
if _FRONTEND_DIR not in sys.path:
    sys.path.insert(0, _FRONTEND_DIR)

from menu_config import CAKE_MENU

warnings.filterwarnings('ignore')

print("="*70)
print("BEIGE.AI PHASE 3: ML PIPELINE")
print("="*70)
print(f"\n[Version Info]")
print(f"  - scikit-learn: {sklearn.__version__}")
print(f"  - numpy: {np.__version__}")
print(f"  - pandas: {pd.__version__}")

# ============================================================================
# STEP 1: LOAD DATA
# ============================================================================

print("\n[1/6] Loading dataset...")
data_path = _BASE_DIR / "data" / "beige_ai_cake_dataset_v2.csv"
df = pd.read_csv(str(data_path))

print(f"✓ Shape: {df.shape}")
print(f"✓ Cakes: {len(CAKE_MENU)} (from menu_config.py)")
print(f"✓ Missing values: {df.isnull().sum().sum()}")

# ============================================================================
# STEP 2: PREPARE FEATURES
# ============================================================================

print("\n[2/6] Preparing features...")

categorical_features = [
    'mood',
    'weather_condition',
    'time_of_day',
    'season',
    'temperature_category'
]

numerical_features = [
    'temperature_celsius',
    'humidity',
    'air_quality_index',
    'sweetness_preference',
    'health_preference',
    'trend_popularity_score',
    'comfort_index',
    'environmental_score'
]

X = df[categorical_features + numerical_features]
y = df['cake_category']

print(f"✓ Features: {X.shape[1]} ({len(categorical_features)} cat, {len(numerical_features)} num)")
print(f"✓ Target: {len(y)} samples, {len(y.unique())} classes")

# ============================================================================
# STEP 3: TRAIN/TEST SPLIT & PREPROCESSING
# ============================================================================

print("\n[3/6] Train/test split and preprocessing...")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

preprocessor = ColumnTransformer(
    transformers=[
        ('cat', OneHotEncoder(sparse_output=False, handle_unknown='ignore'), 
         categorical_features),
        ('num', StandardScaler(), numerical_features)
    ]
)

X_train_processed = preprocessor.fit_transform(X_train)
X_test_processed = preprocessor.transform(X_test)

print(f"✓ Train: {X_train_processed.shape}")
print(f"✓ Test: {X_test_processed.shape}")

# ============================================================================
# STEP 4: TRAIN & COMPARE MODELS
# ============================================================================

print("\n[4/6] Training models...")

# Model 1: Decision Tree
dt = DecisionTreeClassifier(random_state=42, max_depth=10, min_samples_split=5)
dt.fit(X_train_processed, y_train)
dt_train_acc = accuracy_score(y_train, dt.predict(X_train_processed))
dt_test_acc = accuracy_score(y_test, dt.predict(X_test_processed))

print(f"\n  Decision Tree:")
print(f"    Train: {dt_train_acc:.4f} | Test: {dt_test_acc:.4f}")

# Model 2: Random Forest
rf = RandomForestClassifier(
    n_estimators=50,
    random_state=42,
    n_jobs=-1,
    max_depth=15,
    min_samples_split=5
)
rf.fit(X_train_processed, y_train)
rf_train_acc = accuracy_score(y_train, rf.predict(X_train_processed))
rf_test_acc = accuracy_score(y_test, rf.predict(X_test_processed))

print(f"  Random Forest:")
print(f"    Train: {rf_train_acc:.4f} | Test: {rf_test_acc:.4f}")

# Select best model
if rf_test_acc > dt_test_acc:
    best_model = rf
    best_model_name = "Random Forest"
    best_test_acc = rf_test_acc
else:
    best_model = dt
    best_model_name = "Decision Tree"
    best_test_acc = dt_test_acc

print(f"\n✓ Best model: {best_model_name} ({best_test_acc:.4f})")

# ============================================================================
# STEP 5: HYPERPARAMETER TUNING
# ============================================================================

print("\n[5/6] Hyperparameter tuning...")

if best_model_name == "Random Forest":
    param_dist = {
        'n_estimators': [50, 75],
        'max_depth': [12, 15],
        'min_samples_split': [5, 10],
    }
else:
    param_dist = {
        'max_depth': [10, 12, 15],
        'min_samples_split': [5, 10],
    }

rs = RandomizedSearchCV(
    best_model,
    param_dist,
    n_iter=12,
    cv=3,
    scoring='accuracy',
    n_jobs=-1,
    random_state=42,
    verbose=0
)

rs.fit(X_train_processed, y_train)

tuned_model = rs.best_estimator_
y_pred_train = tuned_model.predict(X_train_processed)
y_pred_test = tuned_model.predict(X_test_processed)

train_acc_final = accuracy_score(y_train, y_pred_train)
test_acc_final = accuracy_score(y_test, y_pred_test)

print(f"✓ Best parameters: {rs.best_params_}")
print(f"✓ CV score: {rs.best_score_:.4f}")
print(f"✓ Final test accuracy: {test_acc_final:.4f}")

# ============================================================================
# STEP 6: EVALUATION & VISUALIZATION
# ============================================================================

print("\n[6/6] Evaluation and visualization...")

print("\n--- Classification Report ---\n")
print(classification_report(y_test, y_pred_test, digits=4))

cm = confusion_matrix(y_test, y_pred_test)

# Visualization
fig, axes = plt.subplots(1, 3, figsize=(16, 5))

# Plot 1: Confusion Matrix
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[0], cbar=False)
axes[0].set_xlabel('Predicted')
axes[0].set_ylabel('Actual')
axes[0].set_title('Confusion Matrix', fontweight='bold')
axes[0].tick_params(axis='x', rotation=45)
axes[0].tick_params(axis='y', rotation=0)

# Plot 2: Class Distribution
class_dist = y.value_counts().sort_index()
axes[1].barh(range(len(class_dist)), class_dist.values, color='steelblue', alpha=0.8)
axes[1].set_yticks(range(len(class_dist)))
axes[1].set_yticklabels(class_dist.index, fontsize=9)
axes[1].set_xlabel('Count', fontweight='bold')
axes[1].set_title('Target Distribution', fontweight='bold')
axes[1].grid(axis='x', alpha=0.3)

# Plot 3: Feature Importances
if hasattr(tuned_model, 'feature_importances_'):
    importances = tuned_model.feature_importances_
    indices = np.argsort(importances)[-12:]
    feature_names = (
        list(preprocessor.named_transformers_['cat']
             .get_feature_names_out(categorical_features)) +
        numerical_features
    )
    axes[2].barh(range(len(indices)), importances[indices], color='darkorange', alpha=0.8)
    axes[2].set_yticks(range(len(indices)))
    axes[2].set_yticklabels([feature_names[i] for i in indices], fontsize=8)
    axes[2].set_xlabel('Importance', fontweight='bold')
    axes[2].set_title('Top 12 Features', fontweight='bold')
    axes[2].grid(axis='x', alpha=0.3)

plt.tight_layout()
eval_fig_path = _BASE_DIR / "phase3_model_evaluation.png"
plt.savefig(str(eval_fig_path), dpi=300, bbox_inches='tight')
print(f"✓ Saved: phase3_model_evaluation.png → {eval_fig_path}")
plt.close()

# ============================================================================
# SAVE ARTIFACTS
# ============================================================================

print("\nSaving artifacts...")

# Create models directory if it doesn't exist
models_dir = Path(__file__).resolve().parent.parent / "models"
models_dir.mkdir(parents=True, exist_ok=True)

# Prepare feature info with version metadata
feature_info = {
    'categorical_features': categorical_features,
    'numerical_features': numerical_features,
    'cake_menu': CAKE_MENU,
    'classes': sorted(y.unique()),
    'model_type': best_model_name,
    'test_accuracy': test_acc_final,
    'sklearn_version': sklearn.__version__,
    'numpy_version': np.__version__,
    'pandas_version': pd.__version__,
    'training_date': pd.Timestamp.now().isoformat()
}

# Save artifacts with error handling
try:
    model_path = models_dir / "cake_model.joblib"
    joblib.dump(tuned_model, str(model_path))
    print(f"✓ Saved: {model_path}")
    
    preprocessor_path = models_dir / "preprocessor.joblib"
    joblib.dump(preprocessor, str(preprocessor_path))
    print(f"✓ Saved: {preprocessor_path}")
    
    feature_info_path = models_dir / "feature_info.joblib"
    joblib.dump(feature_info, str(feature_info_path))
    print(f"✓ Saved: {feature_info_path}")
    
    print(f"\n[Model Metadata]")
    print(f"  - Model: {best_model_name}")
    print(f"  - Test Accuracy: {test_acc_final:.4f}")
    print(f"  - sklearn: {sklearn.__version__}")
    print(f"  - numpy: {np.__version__}")
    print(f"  - pandas: {pd.__version__}")
    
except Exception as e:
    print(f"\n❌ Error saving artifacts: {e}")
    print(f"Directory: {models_dir}")
    print(f"Ensure you have write permissions to this location.")
    raise

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "="*70)
print("PHASE 3 COMPLETE!")
print("="*70)

print(f"\nModel: {best_model_name}")
print(f"Test Accuracy: {test_acc_final:.4f} ({test_acc_final*100:.2f}%)")
print(f"Classes: {len(y.unique())}")
print(f"Features: {X_train_processed.shape[1]} (after preprocessing)")

print(f"\nBest Parameters:")
for param, value in rs.best_params_.items():
    print(f"  {param}: {value}")

print(f"\nOutput Files:")
print(f"  ✓ best_model.joblib")
print(f"  ✓ preprocessor.joblib")
print(f"  ✓ feature_info.joblib")
print(f"  ✓ phase3_model_evaluation.png")

print(f"\nReady for deployment!" )
print("="*70 + "\n")
