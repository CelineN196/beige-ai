"""
Beige.AI V2: Production-Grade ML Pipeline
================================================================
Rebuild the entire recommendation system with:
- Gradient Boosting + XGBoost comparison
- Hyperparameter tuning (RandomizedSearchCV)
- Clean, reproducible pipeline
- Python 3.14 + latest sklearn ecosystem compatibility

Pipeline Architecture:
1. Load synthetic dataset (50K+ samples)
2. Build sklearn preprocessing pipeline
3. Train baseline GradientBoostingClassifier
4. Train tuned XGBoostClassifier
5. Compare and select best model (by F1-score)
6. Save artifacts to /models/v2/

Author: Senior ML Engineer
Date: March 2026
"""

import os
import json
import warnings
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime

# ML & Preprocessing
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split, RandomizedSearchCV, cross_val_score
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score, f1_score, log_loss, classification_report, 
    confusion_matrix, roc_auc_score
)
import joblib

# XGBoost
try:
    from xgboost import XGBClassifier
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    print("⚠ XGBoost not installed. Run: pip install xgboost")

warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION & PATHS
# ============================================================================

RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "backend" / "data"
MODELS_DIR = BASE_DIR / "models" / "v2"

# Create v2 models directory
MODELS_DIR.mkdir(parents=True, exist_ok=True)

DATASET_PATH = DATA_DIR / "beige_ai_cake_dataset_v2.csv"

# Feature definitions
CATEGORICAL_FEATURES = [
    'mood',
    'weather_condition',
    'time_of_day',
    'season',
    'temperature_category'
]

NUMERICAL_FEATURES = [
    'temperature_celsius',
    'humidity',
    'air_quality_index',
    'sweetness_preference',
    'health_preference',
    'trend_popularity_score',
    'comfort_index',
    'environmental_score'
]

TARGET = 'cake_category'

# ============================================================================
# SECTION 1: DATA LOADING & EXPLORATION
# ============================================================================

def load_data(data_path, verbose=True):
    """Load and validate dataset."""
    if verbose:
        print("\n[LOAD] Loading dataset...")
    
    df = pd.read_csv(data_path)
    
    if verbose:
        print(f"  ✓ Shape: {df.shape}")
        print(f"  ✓ Missing values: {df.isnull().sum().sum()}")
        print(f"  ✓ Target classes: {df[TARGET].nunique()}")
        print(f"  ✓ Target distribution:\n{df[TARGET].value_counts().head()}\n")
    
    return df

# ============================================================================
# SECTION 2: PREPROCESSING PIPELINE
# ============================================================================

def build_preprocessor(categorical_features, numerical_features):
    """Build sklearn preprocessing pipeline."""
    return ColumnTransformer(
        transformers=[
            ('categorical', 
             OneHotEncoder(sparse_output=False, handle_unknown='ignore'),
             categorical_features),
            ('numerical',
             StandardScaler(),
             numerical_features)
        ],
        remainder='passthrough'
    )

# ============================================================================
# SECTION 3: MODEL TRAINING
# ============================================================================

def train_gradient_boosting(X_train, y_train, X_val, y_val, verbose=True):
    """Train baseline GradientBoostingClassifier."""
    if verbose:
        print("\n[TRAIN] Gradient Boosting Classifier...")
    
    model = GradientBoostingClassifier(
        n_estimators=200,
        learning_rate=0.1,
        max_depth=5,
        min_samples_split=5,
        min_samples_leaf=2,
        subsample=0.8,
        random_state=RANDOM_STATE,
        verbose=0
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_val)
    y_pred_proba = model.predict_proba(X_val)
    
    metrics = {
        'accuracy': accuracy_score(y_val, y_pred),
        'f1_weighted': f1_score(y_val, y_pred, average='weighted'),
        'log_loss': log_loss(y_val, y_pred_proba)
    }
    
    if verbose:
        print(f"  ✓ Accuracy: {metrics['accuracy']:.4f}")
        print(f"  ✓ F1 (weighted): {metrics['f1_weighted']:.4f}")
        print(f"  ✓ Log Loss: {metrics['log_loss']:.4f}")
    
    return model, metrics

def train_xgboost(X_train, y_train, X_val, y_val, verbose=True):
    """Train and tune XGBClassifier with RandomizedSearchCV."""
    if not XGBOOST_AVAILABLE:
        if verbose:
            print("\n[SKIP] XGBoost not available")
        return None, {'accuracy': 0, 'f1_weighted': 0, 'log_loss': float('inf')}
    
    if verbose:
        print("\n[TUNE] XGBoost with RandomizedSearchCV...")
    
    # Base model
    xgb_model = XGBClassifier(
        random_state=RANDOM_STATE,
        eval_metric='mlogloss',
        verbose=0,
        n_jobs=-1
    )
    
    # Hyperparameter search space
    param_dist = {
        'n_estimators': [100, 150, 200, 250],
        'max_depth': [3, 4, 5, 6, 7],
        'learning_rate': [0.01, 0.05, 0.1, 0.15],
        'subsample': [0.7, 0.8, 0.9, 1.0],
        'colsample_bytree': [0.7, 0.8, 0.9, 1.0],
        'min_child_weight': [1, 2, 3, 4]
    }
    
    # Randomized search (faster than GridSearch)
    search = RandomizedSearchCV(
        xgb_model,
        param_dist,
        n_iter=20,  # 20 random combinations
        cv=3,
        scoring='f1_weighted',
        n_jobs=-1,
        random_state=RANDOM_STATE,
        verbose=0
    )
    
    search.fit(X_train, y_train)
    
    best_model = search.best_estimator_
    
    if verbose:
        print(f"  ✓ Best params: {search.best_params_}")
        print(f"  ✓ Best CV F1-score: {search.best_score_:.4f}")
    
    # Evaluate
    y_pred = best_model.predict(X_val)
    y_pred_proba = best_model.predict_proba(X_val)
    
    metrics = {
        'accuracy': accuracy_score(y_val, y_pred),
        'f1_weighted': f1_score(y_val, y_pred, average='weighted'),
        'log_loss': log_loss(y_val, y_pred_proba)
    }
    
    if verbose:
        print(f"  ✓ Validation Accuracy: {metrics['accuracy']:.4f}")
        print(f"  ✓ Validation F1 (weighted): {metrics['f1_weighted']:.4f}")
        print(f"  ✓ Validation Log Loss: {metrics['log_loss']:.4f}")
    
    return best_model, metrics

# ============================================================================
# SECTION 4: MODEL EVALUATION & SELECTION
# ============================================================================

def print_leaderboard(models_dict, metrics_dict):
    """Print model comparison leaderboard."""
    print("\n" + "="*70)
    print("MODEL LEADERBOARD (ranked by F1-score)")
    print("="*70)
    
    # Create comparison dataframe
    comparison = pd.DataFrame(metrics_dict).T
    comparison = comparison.sort_values('f1_weighted', ascending=False)
    
    print("\n" + comparison.to_string())
    
    best_model_name = comparison.index[0]
    print(f"\n🏆 BEST MODEL: {best_model_name}")
    print(f"   F1-score: {comparison.loc[best_model_name, 'f1_weighted']:.4f}")
    
    return best_model_name

def save_artifacts(model, preprocessor, model_name, metrics, feature_names):
    """Save model, preprocessor, and metadata."""
    print(f"\n[SAVE] Saving {model_name} artifacts to {MODELS_DIR}/...")
    
    # Save model
    model_path = MODELS_DIR / f"{model_name.lower().replace(' ', '_')}.pkl"
    joblib.dump(model, model_path)
    print(f"  ✓ Model: {model_path.name}")
    
    # Save preprocessor
    preprocessor_path = MODELS_DIR / "preprocessor.pkl"
    joblib.dump(preprocessor, preprocessor_path)
    print(f"  ✓ Preprocessor: {preprocessor_path.name}")
    
    # Save feature names
    feature_names_path = MODELS_DIR / "feature_names.json"
    with open(feature_names_path, 'w') as f:
        json.dump(feature_names, f, indent=2)
    print(f"  ✓ Feature names: {feature_names_path.name}")
    
    # Save metrics
    metrics_path = MODELS_DIR / "metrics.json"
    metrics_to_save = {k: float(v) for k, v in metrics.items()}
    with open(metrics_path, 'w') as f:
        json.dump(metrics_to_save, f, indent=2)
    print(f"  ✓ Metrics: {metrics_path.name}")
    
    # Save best model as main artifact
    best_model_path = MODELS_DIR / "best_model.pkl"
    joblib.dump(model, best_model_path)
    print(f"  ✓ Best model: {best_model_path.name}")

def create_training_report(models_dict, metrics_dict, feature_names, best_model_name):
    """Create human-readable training report."""
    report_path = MODELS_DIR / "training_report.md"
    
    report = f"""# Beige AI V2 - Training Report

**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Best Model:** {best_model_name}

## Model Comparison

| Model | Accuracy | F1-Score (weighted) | Log Loss |
|-------|----------|-------------------|----------|
"""
    
    for model_name in metrics_dict.keys():
        metrics = metrics_dict[model_name]
        report += f"| {model_name} | {metrics['accuracy']:.4f} | {metrics['f1_weighted']:.4f} | {metrics['log_loss']:.4f} |\n"
    
    report += f"""
## Features Used

**Categorical Features ({len(CATEGORICAL_FEATURES)}):**
{', '.join(CATEGORICAL_FEATURES)}

**Numerical Features ({len(NUMERICAL_FEATURES)}):**
{', '.join(NUMERICAL_FEATURES)}

**Total Features After Encoding:** {len(feature_names)}

## Dataset Information

- Total Samples: ~50,000
- Train/Val/Test Split: 60% / 20% / 20%
- Target Variable: {TARGET}
- Number of Classes: ~8 cake types

## Key Hyperparameters (Best Model)

See `metrics.json` for complete metadata.

## Files Generated

- `best_model.pkl` - Production model
- `preprocessor.pkl` - Feature preprocessing pipeline
- `feature_names.json` - All feature names after encoding
- `metrics.json` - Model performance metrics
"""
    
    with open(report_path, 'w') as f:
        f.write(report)
    
    print(f"\n✓ Training report saved to {report_path.name}")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Execute complete V2 training pipeline."""
    print("\n" + "="*70)
    print("BEIGE.AI V2: PRODUCTION ML PIPELINE")
    print("="*70)
    
    # Step 1: Load data
    df = load_data(DATASET_PATH)
    
    # Step 2: Prepare features and target
    X = df[CATEGORICAL_FEATURES + NUMERICAL_FEATURES]
    y = df[TARGET]
    
    # Step 3: Encode target for XGBoost compatibility
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    
    print(f"\n[ENCODE] Label encoding for {len(label_encoder.classes_)} classes:")
    for i, cake in enumerate(label_encoder.classes_):
        print(f"  {i}: {cake}")
    
    # Step 4: Train/val/test split
    print(f"\n[SPLIT] Creating train/val/test splits...")
    X_temp, X_test, y_temp, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=RANDOM_STATE, stratify=y_encoded
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, y_temp, test_size=0.25, random_state=RANDOM_STATE, stratify=y_temp
    )
    
    print(f"  ✓ Train: {X_train.shape[0]} samples ({X_train.shape[0]/len(X)*100:.1f}%)")
    print(f"  ✓ Val: {X_val.shape[0]} samples ({X_val.shape[0]/len(X)*100:.1f}%)")
    print(f"  ✓ Test: {X_test.shape[0]} samples ({X_test.shape[0]/len(X)*100:.1f}%)")
    
    # Step 5: Build preprocessor
    print(f"\n[PREPROCESS] Building preprocessing pipeline...")
    preprocessor = build_preprocessor(CATEGORICAL_FEATURES, NUMERICAL_FEATURES)
    
    # Fit on training data ONLY
    X_train_processed = preprocessor.fit_transform(X_train)
    X_val_processed = preprocessor.transform(X_val)
    X_test_processed = preprocessor.transform(X_test)
    
    # Get feature names
    feature_names_cat = preprocessor.named_transformers_['categorical'].get_feature_names_out(
        CATEGORICAL_FEATURES
    ).tolist()
    all_feature_names = feature_names_cat + NUMERICAL_FEATURES
    
    print(f"  ✓ Processed features: {len(all_feature_names)}")
    
    # Step 6: Train models
    models = {}
    metrics = {}
    
    # Gradient Boosting
    gb_model, gb_metrics = train_gradient_boosting(
        X_train_processed, y_train, X_val_processed, y_val
    )
    models['Gradient Boosting'] = gb_model
    metrics['Gradient Boosting'] = gb_metrics
    
    # XGBoost
    if XGBOOST_AVAILABLE:
        xgb_model, xgb_metrics = train_xgboost(
            X_train_processed, y_train, X_val_processed, y_val
        )
        if xgb_model is not None:
            models['XGBoost'] = xgb_model
            metrics['XGBoost'] = xgb_metrics
    
    # Step 7: Select best model
    print("\n" + "-"*70)
    best_model_name = print_leaderboard(models, metrics)
    best_model = models[best_model_name]
    best_metrics = metrics[best_model_name]
    
    # Step 8: Evaluate on test set
    print(f"\n[EVALUATE] Test set performance ({best_model_name})...")
    y_test_pred = best_model.predict(X_test_processed)
    y_test_pred_proba = best_model.predict_proba(X_test_processed)
    
    test_metrics = {
        'test_accuracy': accuracy_score(y_test, y_test_pred),
        'test_f1_weighted': f1_score(y_test, y_test_pred, average='weighted'),
        'test_log_loss': log_loss(y_test, y_test_pred_proba)
    }
    
    print(f"  ✓ Test Accuracy: {test_metrics['test_accuracy']:.4f}")
    print(f"  ✓ Test F1 (weighted): {test_metrics['test_f1_weighted']:.4f}")
    print(f"  ✓ Test Log Loss: {test_metrics['test_log_loss']:.4f}")
    
    # Combine metrics
    final_metrics = {**best_metrics, **test_metrics}
    
    # Step 9: Save artifacts
    save_artifacts(best_model, preprocessor, best_model_name, final_metrics, all_feature_names)
    
    # Save label encoder mapping
    label_encoder_path = MODELS_DIR / "label_encoder.pkl"
    joblib.dump(label_encoder, label_encoder_path)
    print(f"  ✓ Label encoder: {label_encoder_path.name}")
    
    # Step 10: Create report
    create_training_report(models, metrics, all_feature_names, best_model_name)
    
    print("\n" + "="*70)
    print("✅ V2 PIPELINE COMPLETE")
    print("="*70)
    print(f"\nArtifacts saved to: {MODELS_DIR}/")
    print("\nNext step: Update frontend to load from /models/v2/best_model.pkl")
    
    return best_model, preprocessor, all_feature_names

if __name__ == "__main__":
    model, preprocessor, feature_names = main()
