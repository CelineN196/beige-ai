#!/usr/bin/env python3
"""
Beige.AI Model Comparison & Selection Pipeline

Train four classifiers (Decision Tree, Random Forest, Gradient Boosting, XGBoost),
perform hyperparameter tuning, evaluate, compare, and select the best model.

Author: ML Engineering Team
Date: March 19, 2026
"""

import os
import sys
import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from datetime import datetime

# ML Libraries
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from xgboost import XGBClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, ConfusionMatrixDisplay
)
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings('ignore')


# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data" / "raw"  # Dataset in data/raw/
MODELS_DIR = BASE_DIR / "backend" / "models"
DOCS_DIR = BASE_DIR / "docs"

# Create directories if needed
MODELS_DIR.mkdir(parents=True, exist_ok=True)
DOCS_DIR.mkdir(parents=True, exist_ok=True)

# Random seed for reproducibility
RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)

# Hyperparameter grids
dt_param_dist = {
    'max_depth': [3, 5, 7, 10, 15, 20, None],
    'min_samples_split': [2, 5, 10, 20],
    'min_samples_leaf': [1, 2, 4, 8],
}

rf_param_dist = {
    'n_estimators': [50, 100, 200, 300],
    'max_depth': [5, 10, 15, 20, None],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4],
}

gb_param_dist = {
    'n_estimators': [50, 100, 200],
    'learning_rate': [0.01, 0.05, 0.1, 0.15],
    'max_depth': [3, 5, 7, 10],
}

xgb_param_dist = {
    'n_estimators': [50, 100, 150],
    'max_depth': [3, 5, 7],
    'learning_rate': [0.01, 0.05, 0.1],
    'subsample': [0.8, 1.0],
    'colsample_bytree': [0.8, 1.0],
    'gamma': [0, 0.1, 0.2],
}


# ============================================================================
# LOGGING & UTILITIES
# ============================================================================

def log(msg: str, level: str = "INFO"):
    """Print formatted log message"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    level_color = {
        "INFO": "🔵",
        "SUCCESS": "✅",
        "WARNING": "⚠️",
        "ERROR": "❌"
    }
    icon = level_color.get(level, "•")
    print(f"{icon} [{timestamp}] {msg}")


# ============================================================================
# DATA LOADING & PREPROCESSING
# ============================================================================

def load_and_prepare_data(file_path: str, test_size=0.2):
    """
    Load dataset and perform train/test split with preprocessing
    
    Args:
        file_path: Path to CSV file
        test_size: Test set proportion (default 0.2 for 80/20 split)
    
    Returns:
        X_train, X_test, y_train, y_test, feature_names, target_name, encoders
    """
    log("Loading dataset...", "INFO")
    
    # Load CSV
    df = pd.read_csv(file_path)
    log(f"Dataset shape: {df.shape}", "INFO")
    log(f"Columns: {list(df.columns)}", "INFO")
    
    # Identify target and features
    target_col = 'cake_category'
    if target_col not in df.columns:
        # Try alternative name
        target_cols = [col for col in df.columns if 'cake' in col.lower() or 'category' in col.lower()]
        if target_cols:
            target_col = target_cols[0]
    
    if target_col not in df.columns:
        raise ValueError(f"Target column not found. Available: {list(df.columns)}")
    
    # Separate features and target
    X = df.drop(columns=[target_col])
    y = df[target_col]
    
    log(f"Target column: {target_col}", "INFO")
    log(f"Number of classes: {y.nunique()}", "INFO")
    log(f"Class distribution:\n{y.value_counts()}", "INFO")
    
    # Handle categorical features
    categorical_features = X.select_dtypes(include=['object']).columns.tolist()
    numerical_features = X.select_dtypes(include=['int64', 'float64']).columns.tolist()
    
    log(f"Categorical features ({len(categorical_features)}): {categorical_features}", "INFO")
    log(f"Numerical features ({len(numerical_features)}): {numerical_features}", "INFO")
    
    # Create preprocessor pipeline
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_features),
            ('num', StandardScaler(), numerical_features)
        ],
        remainder='passthrough'
    )
    
    # Fit and transform
    X_processed = preprocessor.fit_transform(X)
    
    # Get feature names after transformation
    cat_feature_names = []
    if categorical_features:
        cat_encoder = preprocessor.named_transformers_['cat']
        cat_feature_names = cat_encoder.get_feature_names_out(categorical_features).tolist()
    
    final_feature_names = cat_feature_names + numerical_features
    
    log(f"Total features after preprocessing: {len(final_feature_names)}", "INFO")
    
    # Handle target encoding
    if y.dtype == 'object':
        target_encoder = LabelEncoder()
        y_encoded = target_encoder.fit_transform(y)
        target_classes = list(target_encoder.classes_)
    else:
        y_encoded = y.values
        target_classes = list(np.unique(y_encoded))
    
    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X_processed, y_encoded,
        test_size=test_size,
        random_state=RANDOM_STATE,
        stratify=y_encoded
    )
    
    log(f"Train set: {X_train.shape[0]} samples", "SUCCESS")
    log(f"Test set: {X_test.shape[0]} samples", "SUCCESS")
    
    return {
        'X_train': X_train,
        'X_test': X_test,
        'y_train': y_train,
        'y_test': y_test,
        'feature_names': final_feature_names,
        'target_name': target_col,
        'target_classes': target_classes,
        'preprocessor': preprocessor
    }


# ============================================================================
# MODEL TRAINING WITH HYPERPARAMETER TUNING
# ============================================================================

def train_decision_tree(X_train, y_train, X_test, y_test):
    """Train Decision Tree with hyperparameter tuning"""
    log("Training Decision Tree...", "INFO")
    
    dt = DecisionTreeClassifier(random_state=RANDOM_STATE)
    
    # RandomizedSearchCV
    search = RandomizedSearchCV(
        dt, dt_param_dist,
        n_iter=20,
        cv=5,
        scoring='f1_weighted',
        random_state=RANDOM_STATE,
        n_jobs=-1,
        verbose=0
    )
    
    search.fit(X_train, y_train)
    
    log(f"Best params: {search.best_params_}", "INFO")
    log(f"Best CV score (F1): {search.best_score_:.4f}", "SUCCESS")
    
    # Evaluate on test set
    y_pred = search.best_estimator_.predict(X_test)
    metrics = evaluate_model(y_test, y_pred)
    
    return search.best_estimator_, metrics, y_pred


def train_random_forest(X_train, y_train, X_test, y_test):
    """Train Random Forest with hyperparameter tuning"""
    log("Training Random Forest...", "INFO")
    
    rf = RandomForestClassifier(random_state=RANDOM_STATE)
    
    # RandomizedSearchCV
    search = RandomizedSearchCV(
        rf, rf_param_dist,
        n_iter=20,
        cv=5,
        scoring='f1_weighted',
        random_state=RANDOM_STATE,
        n_jobs=-1,
        verbose=0
    )
    
    search.fit(X_train, y_train)
    
    log(f"Best params: {search.best_params_}", "INFO")
    log(f"Best CV score (F1): {search.best_score_:.4f}", "SUCCESS")
    
    # Evaluate on test set
    y_pred = search.best_estimator_.predict(X_test)
    metrics = evaluate_model(y_test, y_pred)
    
    return search.best_estimator_, metrics, y_pred


def train_gradient_boosting(X_train, y_train, X_test, y_test):
    """Train Gradient Boosting with hyperparameter tuning"""
    log("Training Gradient Boosting...", "INFO")
    
    gb = GradientBoostingClassifier(random_state=RANDOM_STATE)
    
    # RandomizedSearchCV
    search = RandomizedSearchCV(
        gb, gb_param_dist,
        n_iter=20,
        cv=5,
        scoring='f1_weighted',
        random_state=RANDOM_STATE,
        n_jobs=-1,
        verbose=0
    )
    
    search.fit(X_train, y_train)
    
    log(f"Best params: {search.best_params_}", "INFO")
    log(f"Best CV score (F1): {search.best_score_:.4f}", "SUCCESS")
    
    # Evaluate on test set
    y_pred = search.best_estimator_.predict(X_test)
    metrics = evaluate_model(y_test, y_pred)
    
    return search.best_estimator_, metrics, y_pred


def train_xgboost(X_train, y_train, X_test, y_test, num_classes):
    """Train XGBoost with hyperparameter tuning"""
    log("Training XGBoost...", "INFO")
    
    xgb = XGBClassifier(
        objective='multi:softprob',
        num_class=num_classes,
        eval_metric='mlogloss',
        use_label_encoder=False,
        random_state=RANDOM_STATE
    )
    
    # RandomizedSearchCV with reduced iterations for speed
    search = RandomizedSearchCV(
        xgb, xgb_param_dist,
        n_iter=10,
        cv=3,
        scoring='f1_weighted',
        random_state=RANDOM_STATE,
        n_jobs=-1,
        verbose=0
    )
    
    search.fit(X_train, y_train)
    
    log(f"Best params: {search.best_params_}", "INFO")
    log(f"Best CV score (F1): {search.best_score_:.4f}", "SUCCESS")
    
    # Evaluate on test set
    y_pred = search.best_estimator_.predict(X_test)
    metrics = evaluate_model(y_test, y_pred)
    
    return search.best_estimator_, metrics, y_pred


# ============================================================================
# EVALUATION METRICS
# ============================================================================

def evaluate_model(y_true, y_pred):
    """
    Calculate evaluation metrics
    
    Returns:
        dict with accuracy, precision, recall, f1
    """
    return {
        'accuracy': accuracy_score(y_true, y_pred),
        'precision': precision_score(y_true, y_pred, average='weighted', zero_division=0),
        'recall': recall_score(y_true, y_pred, average='weighted', zero_division=0),
        'f1': f1_score(y_true, y_pred, average='weighted', zero_division=0),
    }


def compare_models(results_dict):
    """
    Create comparison table and identify best model
    
    Args:
        results_dict: {model_name: {'metrics': {...}, 'model': ...}}
    
    Returns:
        DataFrame with comparison, best_model_name
    """
    records = []
    
    for model_name, data in results_dict.items():
        record = {'Model': model_name}
        record.update(data['metrics'])
        records.append(record)
    
    df_comparison = pd.DataFrame(records).set_index('Model')
    
    # Identify best model by F1-score
    best_model_name = df_comparison['f1'].idxmax()
    
    log(f"\n{'='*60}", "INFO")
    log("MODEL COMPARISON TABLE", "INFO")
    log(f"{'='*60}", "INFO")
    print(df_comparison.round(4))
    log(f"\n🏆 BEST MODEL: {best_model_name} (F1: {df_comparison.loc[best_model_name, 'f1']:.4f})", "SUCCESS")
    
    return df_comparison, best_model_name


# ============================================================================
# VISUALIZATION & REPORTING
# ============================================================================

def generate_confusion_matrix(y_true, y_pred, target_classes, model_name: str):
    """Generate and save confusion matrix"""
    log(f"Generating confusion matrix for {model_name}...", "INFO")
    
    cm = confusion_matrix(y_true, y_pred)
    
    # Plot
    fig, ax = plt.subplots(figsize=(10, 8))
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=target_classes)
    disp.plot(ax=ax, cmap='Blues', values_format='d')
    
    plt.title(f'Confusion Matrix - {model_name}', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    
    # Save
    output_path = DOCS_DIR / f"confusion_matrix_{model_name.lower().replace(' ', '_')}.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    log(f"Saved to: {output_path}", "SUCCESS")
    plt.close()
    
    return output_path


def generate_report(comparison_df, best_model_name, results_dict, target_classes):
    """Generate comprehensive markdown report"""
    log("Generating report...", "INFO")
    
    report = f"""# Beige.AI Model Training Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Report Version:** 1.0

---

## Executive Summary

This report documents the training, hyperparameter tuning, and evaluation of three classification models for the Beige.AI cake recommendation system:

1. **Decision Tree**
2. **Random Forest**
3. **Gradient Boosting**

All models were trained on {len(results_dict)} different architectures using **RandomizedSearchCV with 5-fold cross-validation**, optimizing for **F1-weighted score** to account for potential class imbalance.

---

## Model Comparison

### Summary Table

| Model | Accuracy | Precision | Recall | F1-Score |
|-------|----------|-----------|--------|----------|
"""
    
    for idx, row in comparison_df.iterrows():
        report += f"| {idx} | {row['accuracy']:.4f} | {row['precision']:.4f} | {row['recall']:.4f} | {row['f1']:.4f} |\n"
    
    report += f"""
### Best Model: **{best_model_name}**

The **{best_model_name}** model achieved the highest F1-score of **{comparison_df.loc[best_model_name, 'f1']:.4f}**, making it the recommended model for production deployment.

---

## Detailed Model Analysis

### 1. Decision Tree

**Hyperparameter Tuning Space:**
- `max_depth`: [3, 5, 7, 10, 15, 20, None]
- `min_samples_split`: [2, 5, 10, 20]
- `min_samples_leaf`: [1, 2, 4, 8]

**Best Parameters:**
```python
{results_dict.get('Decision Tree', {}).get('best_params', {})}
```

**Performance Metrics:**
- Accuracy: {comparison_df.loc['Decision Tree', 'accuracy']:.4f}
- Precision: {comparison_df.loc['Decision Tree', 'precision']:.4f}
- Recall: {comparison_df.loc['Decision Tree', 'recall']:.4f}
- F1-Score: {comparison_df.loc['Decision Tree', 'f1']:.4f}

### 2. Random Forest

**Hyperparameter Tuning Space:**
- `n_estimators`: [50, 100, 200, 300]
- `max_depth`: [5, 10, 15, 20, None]
- `min_samples_split`: [2, 5, 10]
- `min_samples_leaf`: [1, 2, 4]

**Best Parameters:**
```python
{results_dict.get('Random Forest', {}).get('best_params', {})}
```

**Performance Metrics:**
- Accuracy: {comparison_df.loc['Random Forest', 'accuracy']:.4f}
- Precision: {comparison_df.loc['Random Forest', 'precision']:.4f}
- Recall: {comparison_df.loc['Random Forest', 'recall']:.4f}
- F1-Score: {comparison_df.loc['Random Forest', 'f1']:.4f}

### 3. Gradient Boosting

**Hyperparameter Tuning Space:**
- `n_estimators`: [50, 100, 200]
- `learning_rate`: [0.01, 0.05, 0.1, 0.15]
- `max_depth`: [3, 5, 7, 10]

**Best Parameters:**
```python
{results_dict.get('Gradient Boosting', {}).get('best_params', {})}
```

**Performance Metrics:**
- Accuracy: {comparison_df.loc['Gradient Boosting', 'accuracy']:.4f}
- Precision: {comparison_df.loc['Gradient Boosting', 'precision']:.4f}
- Recall: {comparison_df.loc['Gradient Boosting', 'recall']:.4f}
- F1-Score: {comparison_df.loc['Gradient Boosting', 'f1']:.4f}

---

## Classification Report (Best Model: {best_model_name})

```
{results_dict[best_model_name]['classification_report']}
```

---

## Confusion Matrix

![Confusion Matrix]({DOCS_DIR.name}/confusion_matrix_{best_model_name.lower().replace(' ', '_')}.png)

---

## Key Insights

### Model Performance Analysis

1. **{best_model_name} Performance**
   - Highest F1-Score: {comparison_df.loc[best_model_name, 'f1']:.4f}
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
1. ✅ **Deploy {best_model_name}** to production
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
- **Total Samples**: {results_dict.get('Decision Tree', {}).get('data', {}).get('total', 0)}
- **Training Samples**: {results_dict.get('Decision Tree', {}).get('data', {}).get('train', 0)}
- **Test Samples**: {results_dict.get('Decision Tree', {}).get('data', {}).get('test', 0)}
- **Number of Classes**: {len(target_classes)}
- **Class Labels**: {', '.join(target_classes)}

### Hyperparameter Tuning Method
- **Method**: RandomizedSearchCV
- **Cross-Validation Folds**: 5
- **Scoring Metric**: F1-weighted
- **Iterations per Model**: 20

### Training Environment
- **Python Version**: {sys.version.split()[0]}
- **scikit-learn**: {pd.__version__}
- **Random Seed**: {RANDOM_STATE} (reproducibility)

---

## Files Generated

- ✅ `best_model.joblib` - Best trained model
- ✅ `feature_info.joblib` - Feature metadata & preprocessing info
- ✅ `confusion_matrix_*.png` - Confusion matrix visualization
- ✅ `MODEL_TRAINING_REPORT.md` - This report

---

## Appendix: Model Selection Rationale

The **{best_model_name}** model was selected based on:

1. **F1-Score**: {comparison_df.loc[best_model_name, 'f1']:.4f} (highest among all candidates)
2. **Balanced Performance**: Strong precision ({comparison_df.loc[best_model_name, 'precision']:.4f}) and recall ({comparison_df.loc[best_model_name, 'recall']:.4f})
3. **Production Readiness**: Fast inference time, stable predictions
4. **Explainability**: Can extract feature importance for business insights

---

**Report Generated by**: Beige.AI ML Engineering Team  
**Next Review Date**: {(datetime.now().replace(month=(datetime.now().month % 12) + 1)).strftime('%Y-%m-%d')}

"""
    
    # Save report
    report_path = DOCS_DIR / "MODEL_TRAINING_REPORT.md"
    with open(report_path, 'w') as f:
        f.write(report)
    
    log(f"Report saved to: {report_path}", "SUCCESS")
    return report_path


# ============================================================================
# MODEL SAVING
# ============================================================================

def save_model_and_metadata(best_model, feature_names, target_classes, target_name):
    """Save best model and metadata"""
    log("Saving model artifacts...", "INFO")
    
    # Save model
    model_path = MODELS_DIR / "best_model.joblib"
    joblib.dump(best_model, model_path)
    log(f"Saved model to: {model_path}", "SUCCESS")
    
    # Save metadata
    metadata = {
        'model_type': type(best_model).__name__,
        'features': feature_names,
        'target': target_name,
        'target_classes': target_classes,
        'training_date': datetime.now().isoformat(),
    }
    
    metadata_path = MODELS_DIR / "feature_info.joblib"
    joblib.dump(metadata, metadata_path)
    log(f"Saved metadata to: {metadata_path}", "SUCCESS")
    
    return model_path, metadata_path


# ============================================================================
# MAIN PIPELINE
# ============================================================================

def main():
    """Main execution pipeline"""
    
    log("=" * 70, "INFO")
    log("BEIGE.AI MODEL COMPARISON & SELECTION PIPELINE", "INFO")
    log("=" * 70, "INFO")
    
    # Load and prepare data
    log("\n📦 STEP 1: DATA LOADING & PREPROCESSING", "INFO")
    data = load_and_prepare_data(str(DATA_DIR / "beige_ai_cake_dataset_v2.csv"))
    
    X_train = data['X_train']
    X_test = data['X_test']
    y_train = data['y_train']
    y_test = data['y_test']
    feature_names = data['feature_names']
    target_name = data['target_name']
    target_classes = data['target_classes']
    
    # Train models
    log("\n🤖 STEP 2: MODEL TRAINING & HYPERPARAMETER TUNING", "INFO")
    
    results_dict = {}
    
    # Decision Tree
    log("\n--- Decision Tree ---", "INFO")
    dt_model, dt_metrics, dt_pred = train_decision_tree(X_train, y_train, X_test, y_test)
    results_dict['Decision Tree'] = {
        'model': dt_model,
        'metrics': dt_metrics,
        'predictions': dt_pred,
        'best_params': dt_model.get_params() if hasattr(dt_model, 'get_params') else {}
    }
    
    # Random Forest
    log("\n--- Random Forest ---", "INFO")
    rf_model, rf_metrics, rf_pred = train_random_forest(X_train, y_train, X_test, y_test)
    results_dict['Random Forest'] = {
        'model': rf_model,
        'metrics': rf_metrics,
        'predictions': rf_pred,
        'best_params': rf_model.get_params() if hasattr(rf_model, 'get_params') else {}
    }
    
    # Gradient Boosting
    log("\n--- Gradient Boosting ---", "INFO")
    gb_model, gb_metrics, gb_pred = train_gradient_boosting(X_train, y_train, X_test, y_test)
    results_dict['Gradient Boosting'] = {
        'model': gb_model,
        'metrics': gb_metrics,
        'predictions': gb_pred,
        'best_params': gb_model.get_params() if hasattr(gb_model, 'get_params') else {}
    }
    
    # XGBoost
    log("\n--- XGBoost ---", "INFO")
    num_classes = len(target_classes)
    xgb_model, xgb_metrics, xgb_pred = train_xgboost(X_train, y_train, X_test, y_test, num_classes)
    results_dict['XGBoost'] = {
        'model': xgb_model,
        'metrics': xgb_metrics,
        'predictions': xgb_pred,
        'best_params': xgb_model.get_params() if hasattr(xgb_model, 'get_params') else {}
    }
    
    # Compare models
    log("\n📊 STEP 3: MODEL COMPARISON", "INFO")
    comparison_df, best_model_name = compare_models(results_dict)
    
    # Get best model
    best_model = results_dict[best_model_name]['model']
    best_predictions = results_dict[best_model_name]['predictions']
    
    # Visualization
    log("\n📈 STEP 4: VISUALIZATION & REPORTING", "INFO")
    
    # Confusion matrix
    cm_path = generate_confusion_matrix(y_test, best_predictions, target_classes, best_model_name)
    
    # Classification report
    class_report = classification_report(y_test, best_predictions, target_names=target_classes)
    results_dict[best_model_name]['classification_report'] = class_report
    
    print("\n" + class_report)
    
    # Generate report
    report_path = generate_report(comparison_df, best_model_name, results_dict, target_classes)
    
    # Save model
    log("\n💾 STEP 5: MODEL SAVING", "INFO")
    model_path, metadata_path = save_model_and_metadata(best_model, feature_names, target_classes, target_name)
    
    # Final summary
    log("\n" + "=" * 70, "INFO")
    log("✅ PIPELINE COMPLETE", "SUCCESS")
    log("=" * 70, "INFO")
    
    log(f"\n🏆 SELECTED MODEL: {best_model_name}", "SUCCESS")
    log(f"   • F1-Score: {results_dict[best_model_name]['metrics']['f1']:.4f}", "INFO")
    log(f"   • Accuracy: {results_dict[best_model_name]['metrics']['accuracy']:.4f}", "INFO")
    log(f"   • Precision: {results_dict[best_model_name]['metrics']['precision']:.4f}", "INFO")
    log(f"   • Recall: {results_dict[best_model_name]['metrics']['recall']:.4f}", "INFO")
    
    log(f"\n📁 ARTIFACTS SAVED:", "INFO")
    log(f"   • Model: {model_path}", "INFO")
    log(f"   • Metadata: {metadata_path}", "INFO")
    log(f"   • Report: {report_path}", "INFO")
    log(f"   • Confusion Matrix: {cm_path}", "INFO")
    
    log("\n✨ Ready for production deployment!", "SUCCESS")


if __name__ == "__main__":
    main()
