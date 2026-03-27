#!/usr/bin/env python3
"""
Beige.AI Model Diagnostics & Analysis Tool
================================================================
Standalone analysis script for inspecting model behavior.

Features:
1. Load dataset with same feature pipeline as training
2. Feature validation (shape, NaN, ranges)
3. Model performance metrics
4. Feature importance analysis
5. Sample predictions with confidence
6. Cluster analysis with elbow curve (optional)
7. Data distribution analysis

Usage:
    python analysis/model_diagnostics.py [--plot] [--kmeans]

    --plot    : Generate matplotlib visualizations
    --kmeans  : Include KMeans elbow curve analysis

Author: Data Science Team
Date: March 2026
"""

import sys
import os
import argparse
import warnings
import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from typing import Tuple, Dict, Any, Optional
import collections

warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION & PATHS
# ============================================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "raw"  # Dataset in data/raw/
MODELS_DIR = BASE_DIR / "models"

DATASET_PATH = DATA_DIR / "beige_ai_cake_dataset_v2.csv"
MODEL_PATH = MODELS_DIR / "v2_final_model.pkl"

# Feature definitions (must match training pipeline)
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
# SECTION 1: DATA VALIDATION
# ============================================================================

def validate_features(X: np.ndarray, feature_names: list = None) -> Dict[str, Any]:
    """Validate feature array for quality issues.
    
    Args:
        X: Feature array
        feature_names: Optional list of feature names for mapping
    
    Returns:
        Dictionary with validation stats
    """
    print("\n" + "="*70)
    print("📊 FEATURE VALIDATION")
    print("="*70)
    
    # Shape
    print(f"\n✓ Shape: {X.shape}")
    print(f"  - Samples: {X.shape[0]:,}")
    print(f"  - Features: {X.shape[1]}")
    
    # NaN checks
    nan_count = np.isnan(X).sum()
    print(f"\n✓ Missing Values: {nan_count} total")
    if nan_count > 0:
        nan_per_feature = np.isnan(X).sum(axis=0)
        print(f"  ⚠️ Features with NaNs: {np.sum(nan_per_feature > 0)}")
        print(f"  ⚠️ Max NaNs in single feature: {nan_per_feature.max()}")
    else:
        print(f"  ✅ No NaN values detected")
    
    # Infinite values
    inf_count = np.isinf(X).sum()
    print(f"\n✓ Infinite Values: {inf_count} total")
    if inf_count > 0:
        print(f"  ⚠️ WARNING: Found infinite values")
    else:
        print(f"  ✅ No infinite values")
    
    # Range statistics
    print(f"\n✓ Value Ranges:")
    print(f"  - Global Min: {np.nanmin(X):.4f}")
    print(f"  - Global Max: {np.nanmax(X):.4f}")
    print(f"  - Global Mean: {np.nanmean(X):.4f}")
    print(f"  - Global Std: {np.nanstd(X):.4f}")
    
    # Per-feature ranges (for numerical features, post-preprocessing these are standardized)
    print(f"\n✓ Per-Feature Statistics (first 10 features):")
    for i in range(min(10, X.shape[1])):
        print(f"  [{i:2d}] Min: {np.nanmin(X[:, i]):8.4f} | Max: {np.nanmax(X[:, i]):8.4f} | "
              f"Mean: {np.nanmean(X[:, i]):8.4f} | Std: {np.nanstd(X[:, i]):8.4f}")
    
    return {
        'shape': X.shape,
        'nan_count': nan_count,
        'inf_count': inf_count,
        'min': np.nanmin(X),
        'max': np.nanmax(X),
        'mean': np.nanmean(X),
        'std': np.nanstd(X)
    }

# ============================================================================
# SECTION 2: MODEL PERFORMANCE ANALYSIS
# ============================================================================

def analyze_model(model: Any, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
    """Analyze model performance on dataset.
    
    Args:
        model: Trained XGBoost model
        X: Feature array (preprocessed)
        y: Target labels
    
    Returns:
        Dictionary with performance metrics
    """
    print("\n" + "="*70)
    print("🎯 MODEL PERFORMANCE ANALYSIS")
    print("="*70)
    
    # Get predictions
    y_pred = model.predict(X)
    y_pred_proba = model.predict_proba(X)
    
    # Accuracy
    from sklearn.metrics import accuracy_score
    accuracy = accuracy_score(y, y_pred)
    print(f"\n✓ Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
    
    # Check if multi-class (for other metrics)
    n_classes = len(np.unique(y))
    print(f"✓ Number of Classes: {n_classes}")
    print(f"✓ Class Distribution:")
    for i, count in enumerate(np.bincount(y)):
        if count > 0:
            pct = (count / len(y)) * 100
            print(f"  - Class {i}: {count:5d} samples ({pct:5.2f}%)")
    
    # F1-score (weighted)
    from sklearn.metrics import f1_score
    f1_weighted = f1_score(y, y_pred, average='weighted')
    print(f"\n✓ F1-Score (weighted): {f1_weighted:.4f}")
    
    # Confidence stats
    max_proba = np.max(y_pred_proba, axis=1)
    print(f"\n✓ Prediction Confidence:")
    print(f"  - Min: {np.min(max_proba):.4f}")
    print(f"  - Max: {np.max(max_proba):.4f}")
    print(f"  - Mean: {np.mean(max_proba):.4f}")
    print(f"  - Std: {np.std(max_proba):.4f}")
    
    # Confidence buckets
    confidence_buckets = {
        'Very High (>0.9)': (max_proba > 0.9).sum(),
        'High (0.8-0.9)': ((max_proba >= 0.8) & (max_proba <= 0.9)).sum(),
        'Medium (0.7-0.8)': ((max_proba >= 0.7) & (max_proba < 0.8)).sum(),
        'Low (<0.7)': (max_proba < 0.7).sum(),
    }
    print(f"\n  Confidence Distribution:")
    for bucket, count in confidence_buckets.items():
        pct = (count / len(y)) * 100
        print(f"    {bucket}: {count:5d} ({pct:5.2f}%)")
    
    return {
        'accuracy': accuracy,
        'f1_weighted': f1_weighted,
        'n_classes': n_classes,
        'avg_confidence': np.mean(max_proba),
        'predictions': y_pred,
        'probabilities': y_pred_proba
    }

# ============================================================================
# SECTION 3: FEATURE IMPORTANCE
# ============================================================================

def analyze_feature_importance(model: Any, top_n: int = 20) -> None:
    """Analyze and display feature importance from XGBoost model.
    
    Args:
        model: Trained XGBoost model
        top_n: Number of top features to display
    """
    print("\n" + "="*70)
    print("⭐ FEATURE IMPORTANCE (XGBoost)")
    print("="*70)
    
    try:
        # Get feature importance
        importance = model.feature_importances_
        feature_names = list(range(len(importance)))
        
        # Sort by importance
        indices = np.argsort(importance)[::-1]
        
        print(f"\nTop {min(top_n, len(importance))} Most Important Features:")
        print(f"{'Rank':<6} {'Feature':<15} {'Importance':<15} {'Relative (%)':<12}")
        print("-" * 50)
        
        total_importance = importance.sum()
        
        for i, idx in enumerate(indices[:top_n]):
            rank = i + 1
            feat_name = f"Feature_{idx}"
            imp_value = importance[idx]
            imp_pct = (imp_value / total_importance) * 100
            
            bar_length = int(imp_pct / 2)
            bar = "█" * bar_length
            
            print(f"{rank:<6} {feat_name:<15} {imp_value:<15.6f} {imp_pct:>6.2f}% {bar}")
        
        # Summary statistics
        print(f"\n✓ Total Features: {len(importance)}")
        print(f"✓ Top {min(5, len(importance))} features account for "
              f"{(importance[indices[:5]].sum() / total_importance * 100):.2f}% of importance")
        
    except AttributeError:
        print("\n⚠️ Model does not have feature_importances_ attribute")

# ============================================================================
# SECTION 4: SAMPLE PREDICTIONS
# ============================================================================

def show_sample_predictions(
    model: Any,
    X: np.ndarray,
    y: np.ndarray,
    n_samples: int = 10
) -> None:
    """Display predictions on sample data.
    
    Args:
        model: Trained model
        X: Feature array
        y: True labels
        n_samples: Number of samples to display
    """
    print("\n" + "="*70)
    print(f"🔮 SAMPLE PREDICTIONS (first {n_samples} samples)")
    print("="*70)
    
    # Get predictions and probabilities
    y_pred = model.predict(X[:n_samples])
    y_pred_proba = model.predict_proba(X[:n_samples])
    max_proba = np.max(y_pred_proba, axis=1)
    
    print(f"\n{'Idx':<5} {'True':<8} {'Pred':<8} {'Confidence':<12} {'Match':<8}")
    print("-" * 45)
    
    matches = 0
    for i in range(min(n_samples, len(X))):
        true_label = y[i]
        pred_label = y_pred[i]
        confidence = max_proba[i]
        match = "✓" if true_label == pred_label else "✗"
        
        if true_label == pred_label:
            matches += 1
        
        print(f"{i:<5} {true_label:<8} {pred_label:<8} {confidence:<12.4f} {match:<8}")
    
    sample_accuracy = (matches / min(n_samples, len(X))) * 100
    print("-" * 45)
    print(f"Sample Accuracy: {matches}/{min(n_samples, len(X))} ({sample_accuracy:.2f}%)")

# ============================================================================
# SECTION 5: KMEANS ELBOW CURVE (Optional)
# ============================================================================

def plot_elbow_curve(
    X: np.ndarray,
    k_range: tuple = (1, 11),
    random_state: int = 42,
    show: bool = True
) -> None:
    """Generate elbow curve for KMeans clustering analysis.
    
    Args:
        X: Feature array
        k_range: Range of k values to test (start, end)
        random_state: Random seed
        show: Whether to display plot
    """
    print("\n" + "="*70)
    print("📈 KMEANS ELBOW CURVE ANALYSIS")
    print("="*70)
    
    try:
        from sklearn.cluster import KMeans
        import matplotlib.pyplot as plt
    except ImportError:
        print("\n⚠️ matplotlib or sklearn not available. Skipping elbow curve.")
        return
    
    print(f"\nTesting K values from {k_range[0]} to {k_range[1]-1}...")
    print("(This may take 1-3 minutes on 50K samples)")
    
    inertias = []
    silhouette_scores = []
    K_values = list(range(k_range[0], k_range[1]))
    
    from sklearn.metrics import silhouette_score
    
    for k in K_values:
        kmeans = KMeans(n_clusters=k, random_state=random_state, n_init=2, max_iter=100)
        kmeans.fit(X)
        inertias.append(kmeans.inertia_)
        
        if k > 1:  # Silhouette score requires at least 2 clusters
            silhouette_scores.append(silhouette_score(X, kmeans.labels_))
        else:
            silhouette_scores.append(0)
        
        print(f"  K={k:2d}: Inertia={kmeans.inertia_:12.2f}, "
              f"Silhouette={silhouette_scores[-1]:7.4f}")
    
    # Find elbow point (using second derivative)
    if len(inertias) > 2:
        second_derivative = np.diff(inertias, 2)
        elbow_k = K_values[np.argmax(second_derivative) + 1] if len(second_derivative) > 0 else 3
        print(f"\n✓ Suggested elbow point: K = {elbow_k}")
    
    # Plot
    if show:
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # Inertia plot
        axes[0].plot(K_values, inertias, marker='o', linewidth=2, markersize=8)
        axes[0].set_xlabel("Number of Clusters (K)", fontsize=11)
        axes[0].set_ylabel("Inertia", fontsize=11)
        axes[0].set_title("KMeans Elbow Curve (Inertia)", fontsize=12, fontweight='bold')
        axes[0].grid(True, alpha=0.3)
        
        # Silhouette plot
        axes[1].plot(K_values, silhouette_scores, marker='s', linewidth=2, markersize=8, color='orange')
        axes[1].set_xlabel("Number of Clusters (K)", fontsize=11)
        axes[1].set_ylabel("Silhouette Score", fontsize=11)
        axes[1].set_title("Silhouette Score by K", fontsize=12, fontweight='bold')
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(BASE_DIR / "analysis" / "elbow_curve.png", dpi=100, bbox_inches='tight')
        print(f"\n✓ Elbow curve saved to: analysis/elbow_curve.png")
        plt.show()

# ============================================================================
# SECTION 6: CLUSTER DISTRIBUTION
# ============================================================================

def analyze_cluster_distribution(
    X: np.ndarray,
    y: np.ndarray,
    k: int = 5,
    random_state: int = 42
) -> None:
    """Analyze distribution of clusters from KMeans.
    
    Args:
        X: Feature array
        y: Target labels (for comparison)
        k: Number of clusters
        random_state: Random seed
    """
    print("\n" + "="*70)
    print(f"🔄 CLUSTER DISTRIBUTION (K={k})")
    print("="*70)
    
    try:
        from sklearn.cluster import KMeans
    except ImportError:
        print("\n⚠️ sklearn not available. Skipping cluster analysis.")
        return
    
    # Fit KMeans (faster with reduced n_init on large datasets)
    print(f"\nFitting KMeans (this may take 30-60 seconds on 50K samples)...")
    kmeans = KMeans(n_clusters=k, random_state=random_state, n_init=3, max_iter=100)
    labels = kmeans.fit_predict(X)
    
    # Count clusters
    cluster_counts = collections.Counter(labels)
    
    print(f"✓ Clustering complete")
    print(f"\n✓ Cluster Distribution (K={k}):")
    print(f"{'Cluster':<10} {'Count':<10} {'Percentage':<12} {'Bar':<30}")
    print("-" * 65)
    
    total_samples = len(labels)
    for cluster_id in sorted(cluster_counts.keys()):
        count = cluster_counts[cluster_id]
        percentage = (count / total_samples) * 100
        bar_length = int(percentage / 2)
        bar = "█" * bar_length
        
        print(f"{cluster_id:<10} {count:<10} {percentage:>6.2f}%      {bar}")
    
    print("-" * 65)
    print(f"{'Total':<10} {total_samples:<10}")
    
    # Target vs cluster distribution
    print(f"\n✓ Target Classes in Dataset:")
    target_counts = collections.Counter(y)
    
    print(f"{'Class':<10} {'Count':<10} {'Percentage':<12}")
    print("-" * 35)
    
    for class_id in sorted(target_counts.keys()):
        count = target_counts[class_id]
        percentage = (count / len(y)) * 100
        print(f"{class_id:<10} {count:<10} {percentage:>6.2f}%")

# ============================================================================
# SECTION 7: DATA LOADING & PREPROCESSING
# ============================================================================

def load_data(data_path: Path) -> Tuple[np.ndarray, np.ndarray, Any, Any]:
    """Load and preprocess data matching training pipeline.
    
    Args:
        data_path: Path to CSV dataset
    
    Returns:
        Tuple of (X_transformed, y, preprocessor, label_encoder)
    """
    print("\n" + "="*70)
    print("📥 LOADING DATA & PREPROCESSING")
    print("="*70)
    
    # Load dataset
    print(f"\nLoading dataset from: {data_path}")
    df = pd.read_csv(data_path)
    print(f"✓ Loaded: {df.shape[0]:,} samples, {df.shape[1]} columns")
    
    # Create derived features if needed
    if 'temperature_category' not in df.columns:
        print("\nDeriving temperature_category...")
        df['temperature_category'] = pd.cut(
            df['temperature_celsius'],
            bins=[-float('inf'), 10, 25, float('inf')],
            labels=['cold', 'mild', 'hot']
        )
    
    if 'comfort_index' not in df.columns:
        print("Deriving comfort_index...")
        temp = df['temperature_celsius']
        humidity = df['humidity']
        air_qual = df['air_quality_index']
        df['comfort_index'] = 1.0 - (np.abs(temp - 22) / 40) * 0.4 - \
                              (humidity / 100) * 0.3 - (air_qual / 100) * 0.3
        df['comfort_index'] = df['comfort_index'].clip(0, 1)
    
    if 'environmental_score' not in df.columns:
        print("Deriving environmental_score...")
        weather_map = {'Sunny': 0.9, 'Cloudy': 0.7, 'Rainy': 0.5, 'Stormy': 0.3, 'Snowy': 0.6}
        season_map = {'Spring': 0.9, 'Summer': 0.85, 'Autumn': 0.75, 'Winter': 0.6}
        
        df['environmental_score'] = (
            df['weather_condition'].map(weather_map).fillna(0.5) * 0.5 +
            df['season'].map(season_map).fillna(0.7) * 0.3 +
            (1.0 - df['air_quality_index'] / 100) * 0.2
        )
    
    # Separate features and target
    X = df[CATEGORICAL_FEATURES + NUMERICAL_FEATURES]
    y = df[TARGET]
    
    print(f"\n✓ Features: {X.shape[1]}")
    print(f"  - Categorical: {len(CATEGORICAL_FEATURES)} ({CATEGORICAL_FEATURES})")
    print(f"  - Numerical: {len(NUMERICAL_FEATURES)}")
    
    # Encode target
    from sklearn.preprocessing import LabelEncoder
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    
    print(f"\n✓ Target classes: {len(label_encoder.classes_)}")
    for i, class_name in enumerate(label_encoder.classes_):
        count = (y_encoded == i).sum()
        print(f"  - {class_name}: {count:,} ({count/len(y)*100:.2f}%)")
    
    # Build preprocessor (same as training)
    from sklearn.preprocessing import StandardScaler, OneHotEncoder
    from sklearn.compose import ColumnTransformer
    
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
    
    X_transformed = preprocessor.fit_transform(X)
    print(f"\n✓ After preprocessing: {X_transformed.shape[1]} features")
    
    return X_transformed, y_encoded, preprocessor, label_encoder

# ============================================================================
# SECTION 8: MAIN EXECUTION
# ============================================================================

def main(args):
    """Execute diagnostics pipeline.
    
    Args:
        args: Command-line arguments
    """
    print("\n" + "="*70)
    print("🔍 BEIGE.AI MODEL DIAGNOSTICS")
    print("="*70)
    print(f"\nDataset: {DATASET_PATH}")
    print(f"Model: {MODEL_PATH}")
    
    # Check files exist
    if not DATASET_PATH.exists():
        print(f"\n❌ Dataset not found: {DATASET_PATH}")
        sys.exit(1)
    
    # Load data
    X, y, preprocessor, label_encoder = load_data(DATASET_PATH)
    
    # Validate features
    validate_features(X)
    
    # Load model with fallback paths
    model = None
    model_loaded = False
    
    # Try primary model path
    model_paths = [
        MODEL_PATH,
        MODELS_DIR / "v2_xgboost_model.pkl",
        MODELS_DIR / "best_model.joblib",
        MODELS_DIR / "v2" / "xgboost.pkl",
    ]
    
    print("\n📦 Loading trained model...")
    
    for model_path in model_paths:
        if not model_path.exists():
            continue
        
        try:
            print(f"  Trying: {model_path.name}...", end=" ")
            
            # Try loading as unified model
            try:
                unified_model = joblib.load(str(model_path))
                if isinstance(unified_model, dict) and 'model' in unified_model:
                    model = unified_model.get('model')
                    model_loaded = True
                    print("✓ Loaded")
                    break
                else:
                    model = unified_model
                    model_loaded = True
                    print("✓ Loaded")
                    break
            except (ModuleNotFoundError, ValueError) as e1:
                # If unified model fails, try direct model load
                if "numpy._core" in str(e1) or "numpy.core" in str(e1):
                    print(f"⚠️  Numpy incompatibility, skipping")
                    continue
                raise
                
        except Exception as e:
            print(f"✗ Failed ({type(e).__name__})")
            continue
    
    if not model_loaded:
        print(f"\n⚠️  Could not load model from any path:")
        for p in model_paths:
            status = "exists" if p.exists() else "missing"
            print(f"  - {p.name} ({status})")
        print("\nNote: Model file may have numpy version compatibility issues.")
        print("      This can happen when models are saved with numpy 1.24 and loaded with newer versions.")
        print("\n✓ Proceeding with data analysis only (no model predictions)")
        
        # Continue with data analysis without model
        analyze_cluster_distribution(X, y, k=5)
        
        if args.kmeans:
            plot_elbow_curve(X, k_range=(1, 11), show=args.plot)
        
        print("\n" + "="*70)
        print("✅ DATA ANALYSIS COMPLETE")
        print("="*70)
        print("\nTo fix model loading, retrain using:")
        print("  python backend/training/train_v2_pipeline.py")
        print("\n")
        return
    
    # Analyze model
    analyze_model(model, X, y)
    
    # Feature importance
    analyze_feature_importance(model, top_n=20)
    
    # Sample predictions
    show_sample_predictions(model, X, y, n_samples=15)
    
    # Cluster analysis
    analyze_cluster_distribution(X, y, k=5)
    
    # KMeans elbow curve (if requested)
    if args.kmeans:
        plot_elbow_curve(X, k_range=(1, 11), show=args.plot)
    
    # Final summary
    print("\n" + "="*70)
    print("✅ DIAGNOSTICS COMPLETE")
    print("="*70)
    print("\nNext Steps:")
    print("  1. Review feature validation for any anomalies")
    print("  2. Check model performance metrics")
    print("  3. Examine feature importance for insights")
    print("  4. Validate sample predictions match expected behavior")
    if args.plot:
        print("  5. Review generated visualizations (elbow_curve.png)")
    print("\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Beige.AI Model Diagnostics & Analysis Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python analysis/model_diagnostics.py
  python analysis/model_diagnostics.py --kmeans
  python analysis/model_diagnostics.py --plot --kmeans
        """
    )
    
    parser.add_argument(
        '--plot',
        action='store_true',
        help='Generate matplotlib visualizations'
    )
    
    parser.add_argument(
        '--kmeans',
        action='store_true',
        help='Include KMeans elbow curve analysis'
    )
    
    args = parser.parse_args()
    
    try:
        main(args)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
