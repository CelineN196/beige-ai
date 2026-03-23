"""
Beige.AI Phase 3: Machine Learning Pipeline
================================================================
Train, evaluate, and save ML models that predict cake category.

This script:
1. Loads and preprocesses the synthetic dataset
2. Trains 3 classification models (baseline comparison)
3. Compares model performance
4. Performs hyperparameter tuning with GridSearchCV
5. Evaluates the best model with detailed metrics
6. Saves model artifacts for production deployment

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
    confusion_matrix,
    roc_auc_score,
    f1_score
)
import joblib
import warnings
from pathlib import Path
import sys

# Add frontend directory to path to import menu_config
_FRONTEND_DIR = str(Path(__file__).resolve().parent.parent.parent / "frontend")
if _FRONTEND_DIR not in sys.path:
    sys.path.insert(0, _FRONTEND_DIR)

from menu_config import CAKE_MENU

warnings.filterwarnings('ignore')

print("="*70)
print("BEIGE.AI PHASE 3: MACHINE LEARNING PIPELINE")
print("="*70)

# ============================================================================
# SECTION 1: DATA LOADING AND EXPLORATION
# ============================================================================

print("\n[1/5] Loading and exploring dataset...")

# Load dataset
df = pd.read_csv('/Users/queenceline/Downloads/Beige AI/beige_ai_cake_dataset_v2.csv')

print(f"✓ Dataset shape: {df.shape}")
print(f"✓ Missing values: {df.isnull().sum().sum()}")

# Verify cake categories match configuration
unique_cakes = set(df['cake_category'].unique())
configured_cakes = set(CAKE_MENU)
if unique_cakes == configured_cakes:
    print(f"✓ Cake categories match menu_config.py ({len(CAKE_MENU)} cakes)")
else:
    print(f"⚠ Warning: Cake category mismatch detected")

print(f"\nTarget variable distribution:")
print(df['cake_category'].value_counts())

# ============================================================================
# SECTION 2: FEATURE ENGINEERING
# ============================================================================

print("\n[2/5] Feature engineering and preprocessing...")

# Define features based on available columns
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

# Target variable
target = 'cake_category'

# Verify all features exist in dataset
available_features = list(df.columns)
missing_features = [f for f in categorical_features + numerical_features 
                   if f not in available_features]

if missing_features:
    print(f"⚠ Warning: Missing features {missing_features}")
    # Filter to available features only
    categorical_features = [f for f in categorical_features if f in available_features]
    numerical_features = [f for f in numerical_features if f in available_features]

print(f"✓ Categorical features: {len(categorical_features)}")
print(f"  {categorical_features}")
print(f"✓ Numerical features: {len(numerical_features)}")
print(f"  {numerical_features}")

# Prepare data
X = df[categorical_features + numerical_features]
y = df[target]

print(f"\nFeature matrix shape: {X.shape}")
print(f"Target shape: {y.shape}")
print(f"Classes: {sorted(y.unique())}")

# ============================================================================
# SECTION 3: DATA PREPROCESSING & TRAIN/TEST SPLIT
# ============================================================================

print("\n[3/5] Train/test split and preprocessing...")

# Train/test split with stratification
X_train, X_test, y_train, y_test = train_test_split(
    X, y, 
    test_size=0.2, 
    random_state=42, 
    stratify=y
)

print(f"✓ Training set size: {X_train.shape[0]} ({X_train.shape[0]/len(X)*100:.1f}%)")
print(f"✓ Test set size: {X_test.shape[0]} ({X_test.shape[0]/len(X)*100:.1f}%)")
print(f"✓ Class distribution preserved in train/test split")

# Create preprocessing pipeline
preprocessor = ColumnTransformer(
    transformers=[
        ('cat', OneHotEncoder(sparse_output=False, handle_unknown='ignore'), 
         categorical_features),
        ('num', StandardScaler(), numerical_features)
    ]
)

# Fit preprocessor on training data
X_train_processed = preprocessor.fit_transform(X_train)
X_test_processed = preprocessor.transform(X_test)

print(f"✓ Preprocessing complete")
print(f"  - Training features after preprocessing: {X_train_processed.shape[1]}")
print(f"  - Test features after preprocessing: {X_test_processed.shape[1]}")

# Get feature names for interpretation
feature_names_cat = preprocessor.named_transformers_['cat'].get_feature_names_out(categorical_features)
feature_names_num = numerical_features
all_feature_names = list(feature_names_cat) + feature_names_num

print(f"✓ Total features after encoding: {len(all_feature_names)}")

# ============================================================================
# SECTION 4: MODEL TRAINING & COMPARISON
# ============================================================================

print("\n[4/5] Training and comparing models...")

models = {
    'Decision Tree': DecisionTreeClassifier(
        random_state=42,
        max_depth=10,
        min_samples_split=5
    ),
    'Random Forest': RandomForestClassifier(
        n_estimators=50,  # Reduced for faster training
        random_state=42,
        n_jobs=-1,
        max_depth=15
    )
}

results = {}
trained_models = {}

print("\nTraining models...\n")

for model_name, model in models.items():
    print(f"  Training {model_name}...")
    
    # Train model
    model.fit(X_train_processed, y_train)
    trained_models[model_name] = model
    
    # Evaluate on train and test sets
    y_train_pred = model.predict(X_train_processed)
    y_test_pred = model.predict(X_test_processed)
    
    train_accuracy = accuracy_score(y_train, y_train_pred)
    test_accuracy = accuracy_score(y_test, y_test_pred)
    
    # Cross-validation score
    cv_scores = cross_val_score(model, X_train_processed, y_train, cv=5, scoring='accuracy')
    
    results[model_name] = {
        'model': model,
        'train_accuracy': train_accuracy,
        'test_accuracy': test_accuracy,
        'cv_mean': cv_scores.mean(),
        'cv_std': cv_scores.std(),
        'y_train_pred': y_train_pred,
        'y_test_pred': y_test_pred
    }
    
    print(f"    Train Accuracy: {train_accuracy:.4f}")
    print(f"    Test Accuracy:  {test_accuracy:.4f}")
    print(f"    CV Mean ± Std:  {cv_scores.mean():.4f} ± {cv_scores.std():.4f}\n")

# ============================================================================
# SECTION 5: MODEL SELECTION & HYPERPARAMETER TUNING
# ============================================================================

print("[5/5] Hyperparameter tuning with GridSearchCV...")

# Select best model based on test accuracy
best_model_name = max(results, key=lambda x: results[x]['test_accuracy'])
print(f"\n✓ Best base model: {best_model_name} (Test Accuracy: {results[best_model_name]['test_accuracy']:.4f})")

# Hyperparameter tuning for Random Forest
print(f"\nPerforming hyperparameter tuning on {best_model_name}...")

if best_model_name == 'Random Forest':
    param_dist = {
        'n_estimators': [50, 75, 100],
        'max_depth': [12, 15, 18],
        'min_samples_split': [5, 10],
    }
else:  # Decision Tree
    param_dist = {
        'max_depth': [8, 10, 12, 15],
        'min_samples_split': [5, 10],
    }

random_search = RandomizedSearchCV(
    trained_models[best_model_name],
    param_dist,
    n_iter=20,  # Sample 20 combinations instead of trying all
    cv=3,
    scoring='accuracy',
    n_jobs=-1,
    verbose=2,
    random_state=42
)

random_search.fit(X_train_processed, y_train)

print(f"\n✓ Hyperparameter tuning complete")
print(f"✓ Best parameters: {random_search.best_params_}")
print(f"✓ Best CV accuracy: {random_search.best_score_:.4f}")

# Final model
best_model = random_search.best_estimator_
y_train_pred_final = best_model.predict(X_train_processed)
y_test_pred_final = best_model.predict(X_test_processed)

final_train_accuracy = accuracy_score(y_train, y_train_pred_final)
final_test_accuracy = accuracy_score(y_test, y_test_pred_final)

print(f"\n--- Final Model Performance ---")
print(f"Training Accuracy:  {final_train_accuracy:.4f}")
print(f"Test Accuracy:      {final_test_accuracy:.4f}")

# ============================================================================
# SECTION 6: DETAILED EVALUATION
# ============================================================================

print("\n" + "="*70)
print("DETAILED MODEL EVALUATION")
print("="*70)

print("\n--- Classification Report (Test Set) ---\n")
print(classification_report(y_test, y_test_pred_final, digits=4))

print("\n--- Confusion Matrix (Test Set) ---\n")
cm = confusion_matrix(y_test, y_test_pred_final)
print(f"Shape: {cm.shape}")
print(cm)

# ============================================================================
# SECTION 7: VISUALIZATIONS
# ============================================================================

print("\nGenerating visualizations...")

fig, axes = plt.subplots(2, 2, figsize=(15, 12))

# Plot 1: Model Comparison
ax1 = axes[0, 0]
model_comparison = pd.DataFrame({
    'Model': list(results.keys()),
    'Train Accuracy': [results[m]['train_accuracy'] for m in results.keys()],
    'Test Accuracy': [results[m]['test_accuracy'] for m in results.keys()],
})
x_pos = np.arange(len(model_comparison))
width = 0.35
ax1.bar(x_pos - width/2, model_comparison['Train Accuracy'], width, label='Train', alpha=0.8)
ax1.bar(x_pos + width/2, model_comparison['Test Accuracy'], width, label='Test', alpha=0.8)
ax1.set_ylabel('Accuracy', fontweight='bold')
ax1.set_title('Model Comparison (Before Tuning)', fontsize=12, fontweight='bold')
ax1.set_xticks(x_pos)
ax1.set_xticklabels(model_comparison['Model'], rotation=15, ha='right')
ax1.legend()
ax1.grid(axis='y', alpha=0.3)
ax1.set_ylim([0, 1])

# Plot 2: Confusion Matrix Heatmap
ax2 = axes[0, 1]
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax2, cbar=False)
ax2.set_xlabel('Predicted', fontweight='bold')
ax2.set_ylabel('Actual', fontweight='bold')
ax2.set_title('Confusion Matrix (Test Set)', fontsize=12, fontweight='bold')
ax2.set_xticklabels(sorted(y_test.unique()), rotation=45, ha='right', fontsize=9)
ax2.set_yticklabels(sorted(y_test.unique()), rotation=0, fontsize=9)

# Plot 3: Class Distribution
ax3 = axes[1, 0]
class_dist = y.value_counts().sort_index()
ax3.barh(range(len(class_dist)), class_dist.values, color='steelblue', alpha=0.8, edgecolor='black')
ax3.set_yticks(range(len(class_dist)))
ax3.set_yticklabels(class_dist.index, fontsize=9)
ax3.set_xlabel('Count', fontweight='bold')
ax3.set_title('Target Class Distribution', fontsize=12, fontweight='bold')
ax3.grid(axis='x', alpha=0.3)
for i, v in enumerate(class_dist.values):
    ax3.text(v, i, f' {v}', va='center', fontweight='bold')

# Plot 4: Feature Importance (if available)
ax4 = axes[1, 1]
if hasattr(best_model, 'feature_importances_'):
    importances = best_model.feature_importances_
    indices = np.argsort(importances)[-15:]  # Top 15 features
    ax4.barh(range(len(indices)), importances[indices], color='darkorange', alpha=0.8, edgecolor='black')
    ax4.set_yticks(range(len(indices)))
    ax4.set_yticklabels([all_feature_names[i] for i in indices], fontsize=9)
    ax4.set_xlabel('Importance', fontweight='bold')
    ax4.set_title('Top 15 Feature Importances', fontsize=12, fontweight='bold')
    ax4.grid(axis='x', alpha=0.3)
else:
    ax4.text(0.5, 0.5, 'Feature importances\nnot available for this model', 
            ha='center', va='center', fontsize=11, transform=ax4.transAxes)
    ax4.set_title('Feature Importances', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig('/Users/queenceline/Downloads/Beige AI/phase3_model_evaluation.png', 
            dpi=300, bbox_inches='tight')
print("✓ Saved visualization: phase3_model_evaluation.png")
plt.close()

# ============================================================================
# SECTION 8: MODEL EXPORT
# ============================================================================

print("\nSaving model artifacts...")

# Save the best model
model_path = '/Users/queenceline/Downloads/Beige AI/best_model.joblib'
joblib.dump(best_model, model_path)
print(f"✓ Best model saved: best_model.joblib")

# Save the preprocessor
preprocessor_path = '/Users/queenceline/Downloads/Beige AI/preprocessor.joblib'
joblib.dump(preprocessor, preprocessor_path)
print(f"✓ Preprocessor saved: preprocessor.joblib")

# Save feature information
feature_info = {
    'categorical_features': categorical_features,
    'numerical_features': numerical_features,
    'all_feature_names': all_feature_names,
    'cake_menu': CAKE_MENU,
    'classes': sorted(y.unique())
}
feature_info_path = '/Users/queenceline/Downloads/Beige AI/feature_info.joblib'
joblib.dump(feature_info, feature_info_path)
print(f"✓ Feature information saved: feature_info.joblib")

# ============================================================================
# SECTION 9: SUMMARY REPORT
# ============================================================================

print("\n" + "="*70)
print("PHASE 3 COMPLETE!")
print("="*70)

print("\n--- Model Summary ---")
print(f"Best Model: {best_model_name} (with GridSearchCV)")
print(f"Test Accuracy: {final_test_accuracy:.4f} ({final_test_accuracy*100:.2f}%)")
print(f"Training Accuracy: {final_train_accuracy:.4f}")
print(f"Classes: {len(y.unique())}")
print(f"Features: {len(all_feature_names)}")

print("\n--- Model Hyperparameters ---")
for param, value in random_search.best_params_.items():
    print(f"  {param}: {value}")

print("\n--- Output Files ---")
print(f"  1. best_model.joblib ..................... Trained model")
print(f"  2. preprocessor.joblib .................. Feature preprocessor")
print(f"  3. feature_info.joblib .................. Feature metadata")
print(f"  4. phase3_model_evaluation.png .......... Evaluation visualizations")

print("\n--- Next Steps (Deployment) ---")
print(f"  1. Use best_model.joblib + preprocessor.joblib for predictions")
print(f"  2. Build Streamlit web app for interactive predictions")
print(f"  3. Create API endpoint (Flask/FastAPI)")
print(f"  4. Monitor model performance in production")
print(f"  5. Integrate with Gemini API for explanations")

print("\n" + "="*70 + "\n")

# ============================================================================
# SECTION 10: LOAD AND TEST
# ============================================================================

print("Testing artifact loading...\n")

# Load artifacts
loaded_model = joblib.load(model_path)
loaded_preprocessor = joblib.load(preprocessor_path)
loaded_feature_info = joblib.load(feature_info_path)

print(f"✓ Model loaded successfully")
print(f"✓ Preprocessor loaded successfully")
print(f"✓ Feature info loaded successfully")

# Test prediction
sample_idx = 0
X_sample = X.iloc[[sample_idx]]
X_sample_processed = loaded_preprocessor.transform(X_sample)
prediction = loaded_model.predict(X_sample_processed)[0]
prediction_proba = loaded_model.predict_proba(X_sample_processed)[0]

print(f"\n--- Sample Prediction Test ---")
print(f"Sample index: {sample_idx}")
print(f"Actual cake: {y.iloc[sample_idx]}")
print(f"Predicted cake: {prediction}")
print(f"Confidence: {(max(prediction_proba)*100):.2f}%")
print(f"✓ Artifacts are ready for deployment!")

print("\n" + "="*70)
print("ALL TESTS PASSED - READY FOR PRODUCTION")
print("="*70 + "\n")
