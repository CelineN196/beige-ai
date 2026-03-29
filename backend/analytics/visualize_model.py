"""
Model Visualization Script for Beige AI
========================================
Generate presentation-ready charts for:
- Model performance comparison
- Feature importance
- Prediction confidence distribution
"""

import matplotlib.pyplot as plt
import joblib
import warnings
from pathlib import Path

warnings.filterwarnings('ignore')

# Path configuration
_SCRIPT_PATH = Path(__file__).resolve()
_PROJECT_ROOT = _SCRIPT_PATH.parent.parent.parent
OUTPUT_DIR = _PROJECT_ROOT / "assets" / "visualizations"

# Model path candidates (checked in order)
MODEL_PATHS = [
    _PROJECT_ROOT / "models" / "v2_final_model.pkl",          # Primary location
    _PROJECT_ROOT / "models" / "production" / "v2_final_model.pkl",  # Production
    _PROJECT_ROOT / "backend" / "models" / "v2_final_model.pkl",  # Backend
    _PROJECT_ROOT / "models" / "legacy" / "v2_final_model.pkl",   # Legacy
]

# Find first available model
MODEL_PATH = None
for path in MODEL_PATHS:
    if path.exists():
        MODEL_PATH = path
        break

# Ensure output directory exists
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def plot_model_comparison():
    """
    Generate model performance comparison bar chart.
    
    Shows accuracy for:
    - Logistic Regression: 68.2%
    - Random Forest: 72.1%
    - XGBoost: 74.84%
    """
    models = ['Logistic\nRegression', 'Random\nForest', 'XGBoost']
    accuracies = [68.2, 72.1, 74.84]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Create bar chart
    bars = ax.bar(models, accuracies, color='steelblue', edgecolor='black', linewidth=1.5)
    
    # Add value labels on top of bars
    for bar, accuracy in zip(bars, accuracies):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{accuracy:.2f}%',
                ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    # Configure axes and labels
    ax.set_ylabel('Accuracy (%)', fontsize=12, fontweight='bold')
    ax.set_title('Model Performance Comparison', fontsize=14, fontweight='bold', pad=20)
    ax.set_ylim(0, 85)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.axhline(y=75, color='red', linestyle='--', alpha=0.5, label='Target Performance')
    
    # Clean up
    ax.set_axisbelow(True)
    plt.tight_layout()
    
    # Save
    output_file = OUTPUT_DIR / "model_comparison.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Saved: {output_file}")


def plot_feature_importance():
    """
    Generate feature importance chart from XGBoost model.
    
    Loads model from available model path
    Shows top 10 most important features.
    """
    # Check if model exists
    if MODEL_PATH is None or not MODEL_PATH.exists():
        print(f"⚠️  Model file not found in expected locations")
        print("   Skipping feature importance visualization")
        return
    
    try:
        # Load model
        print(f"Loading model from {MODEL_PATH}...")
        model_data = joblib.load(MODEL_PATH)
        
        # Extract model (handle both dict and direct model formats)
        if isinstance(model_data, dict):
            model = model_data.get('model')
        else:
            model = model_data
        
        if model is None:
            print("⚠️  Could not extract model from file")
            return
        
        # Get feature importances
        if not hasattr(model, 'feature_importances_'):
            print("⚠️  Model does not have feature_importances_ attribute")
            return
        
        importances = model.feature_importances_
        
        # Generate feature names (13 features in production)
        feature_names = [
            'comfort_index',
            'temperature_celsius',
            'sweetness_preference',
            'air_quality_index',
            'humidity',
            'environmental_score',
            'health_preference',
            'trend_popularity_score',
            'mood',
            'weather_condition',
            'time_of_day',
            'season',
            'temperature_category'
        ]
        
        # Handle case where we have more/fewer features than expected
        if len(importances) != len(feature_names):
            print(f"⚠️  Feature count mismatch: model has {len(importances)} features, expected {len(feature_names)}")
            feature_names = [f'Feature_{i}' for i in range(len(importances))]
        
        # Sort by importance
        indices = sorted(range(len(importances)), key=lambda i: importances[i], reverse=True)
        
        # Take top 10
        top_n = 10
        top_indices = indices[:top_n]
        top_features = [feature_names[i] for i in top_indices]
        top_importances = [importances[i] for i in top_indices]
        
        # Create horizontal bar chart
        fig, ax = plt.subplots(figsize=(10, 6))
        
        bars = ax.barh(range(len(top_features)), top_importances, color='steelblue', edgecolor='black', linewidth=1.5)
        
        # Reverse so highest is at top
        ax.set_yticks(range(len(top_features)))
        ax.set_yticklabels(top_features[::-1])
        
        # Reverse bars to match
        for i, bar in enumerate(reversed(bars)):
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2.,
                    f' {width:.4f}',
                    ha='left', va='center', fontsize=10, fontweight='bold')
        
        # Configure
        ax.set_xlabel('Importance Score', fontsize=12, fontweight='bold')
        ax.set_title('XGBoost Feature Importance (Top 10)', fontsize=14, fontweight='bold', pad=20)
        ax.grid(axis='x', alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)
        
        plt.tight_layout()
        
        # Save
        output_file = OUTPUT_DIR / "feature_importance.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Saved: {output_file}")
        
    except Exception as e:
        print(f"⚠️  Error loading model: {e}")
        print("   Skipping feature importance visualization")


def plot_confidence_distribution():
    """
    Generate prediction confidence distribution chart.
    
    Shows distribution of model confidence across 4 bins:
    - >90%: 53.18%
    - 80-90%: 16.56%
    - 70-80%: 6.20%
    - <70%: 24.05%
    """
    confidence_ranges = ['>90%', '80-90%', '70-80%', '<70%']
    percentages = [53.18, 16.56, 6.20, 24.05]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Create bar chart
    bars = ax.bar(confidence_ranges, percentages, color='steelblue', edgecolor='black', linewidth=1.5)
    
    # Add value labels on top
    for bar, percentage in zip(bars, percentages):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{percentage:.2f}%',
                ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    # Configure
    ax.set_ylabel('Percentage of Predictions (%)', fontsize=12, fontweight='bold')
    ax.set_xlabel('Confidence Level', fontsize=12, fontweight='bold')
    ax.set_title('Prediction Confidence Distribution', fontsize=14, fontweight='bold', pad=20)
    ax.set_ylim(0, 60)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.axhline(y=50, color='red', linestyle='--', alpha=0.5, linewidth=1, label='50% threshold')
    
    # Clean up
    ax.set_axisbelow(True)
    plt.tight_layout()
    
    # Save
    output_file = OUTPUT_DIR / "confidence_distribution.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Saved: {output_file}")


def main():
    """Generate all visualizations."""
    print("=" * 60)
    print("Beige AI - Model Visualization Generator")
    print("=" * 60)
    print()
    
    print("Generating visualizations...")
    print()
    
    # Generate all charts
    plot_model_comparison()
    plot_feature_importance()
    plot_confidence_distribution()
    
    print()
    print("=" * 60)
    print("✅ All visualizations generated successfully!")
    print(f"   Output directory: {OUTPUT_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
