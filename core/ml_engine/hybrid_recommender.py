"""
3-Layer Hybrid Recommendation System for Beige AI
================================================================
Architecture:
1. K-Means Behavioral Segmentation
2. Supervised Classifier (Random Forest)
3. Ranking Layer (ML scores + personalization)

This module trains the complete system and provides
inference functionality for production deployment.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import pickle
import warnings
import logging
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib

warnings.filterwarnings('ignore')

# ============================================================================
# LOGGING SETUP
# ============================================================================
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================
# Path resolution:
# This file: core/ml_engine/hybrid_recommender.py
# Go up 3 levels to project root

_FILE_PATH = Path(__file__).resolve()
_PROJECT_ROOT = _FILE_PATH.parent.parent.parent  # Up to project root
DATA_PATH = _PROJECT_ROOT / "data" / "raw"  # Dataset in data/raw/
MODELS_DIR = _PROJECT_ROOT / "models"
PRODUCTION_MODELS_DIR = MODELS_DIR / "production"

# ============================================================================
# REQUIRED PRODUCTION MODEL FILES
# ============================================================================
# These are the ONLY models used in production
# Fail-fast if any are missing
REQUIRED_PRODUCTION_FILES = [
    "kmeans_model.pkl",
    "kmeans_scaler.pkl",
    "classifier_model.pkl",
    "classifier_encoder.pkl",
    "classifier_scaler.pkl",
    "cluster_stats.pkl",
]

def validate_production_models():
    """
    CRITICAL: Validate that all required production models exist.
    Fail-fast if any are missing.
    
    Raises:
        RuntimeError: If any required production file is missing
    """
    missing_files = []
    
    for filename in REQUIRED_PRODUCTION_FILES:
        model_path = PRODUCTION_MODELS_DIR / filename
        if not model_path.exists():
            missing_files.append(f"  ❌ {filename} not found at {model_path}")
    
    if missing_files:
        error_msg = "CRITICAL: Missing required production model files:\n"
        error_msg += "\n".join(missing_files)
        error_msg += f"\n\nAll models must be in: {PRODUCTION_MODELS_DIR}"
        raise RuntimeError(error_msg)

# Features used for training (13 input features, excluding cake_category target)
INPUT_FEATURES = [
    'mood', 'weather_condition', 'temperature_celsius', 'humidity',
    'season', 'air_quality_index', 'time_of_day', 'sweetness_preference',
    'health_preference', 'trend_popularity_score', 'temperature_category',
    'comfort_index', 'environmental_score'
]

TARGET = 'cake_category'
N_CLUSTERS = 5

# Health profile for cakes (to compute health_alignment_score)
CAKE_HEALTH_PROFILES = {
    # Core 8 trained cakes (from ML training data)
    "Dark Chocolate Sea Salt Cake": 2,    # Low health score
    "Matcha Zen Cake": 8,                 # High health
    "Citrus Cloud Cake": 7,               # Medium-high
    "Berry Garden Cake": 8,               # High
    "Silk Cheesecake": 3,                 # Low
    "Earthy Wellness Cake": 9,            # Very high
    "Café Tiramisu": 5,                   # Medium
    "Korean Sesame Mini Bread": 6,        # Medium-high
    # Extended 8 cakes (recommended in future expansions)
    "Chocolate Cake": 2,                  # Low health
    "Vanilla Cake": 5,                    # Medium
    "Lemon Cake": 7,                      # Medium-high
    "Strawberry Cheesecake": 4,           # Low-medium
    "Carrot Cake": 8,                     # High
    "Black Forest Cake": 2,               # Low
    "Tiramisu Cake": 5,                   # Medium
    "Red Velvet Cake": 3,                 # Low
}

# ============================================================================
# LAYER 1: K-MEANS SEGMENTATION
# ============================================================================

class BehavioralSegmentation:
    """
    K-Means segmentation to identify behavioral clusters.
    Clusters represent user states based on mood, weather, environment.
    """
    
    def __init__(self, n_clusters=5):
        self.n_clusters = n_clusters
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        self.scaler = StandardScaler()
        self.imputer = SimpleImputer(strategy='mean')
        self.is_fitted = False
    
    def fit(self, df):
        """Train KMeans on input features."""
        X = df[INPUT_FEATURES].copy()
        # Encode categorical features
        X = self._encode_categorical(X)
        # Validate and clean data
        X = self._validate_and_clean(X, stage='fit')
        # Impute any remaining NaNs
        X_imputed = self.imputer.fit_transform(X)
        # Scale features
        X_scaled = self.scaler.fit_transform(X_imputed)
        
        # Fit KMeans
        self.kmeans.fit(X_scaled)
        self.is_fitted = True
        
        # Add cluster assignments to dataframe
        df['cluster_id'] = self.kmeans.labels_
        
        return df
    
    def predict(self, df):
        """Assign cluster IDs to new data."""
        if not self.is_fitted:
            raise ValueError("BehavioralSegmentation not fitted. Call fit() first.")
        
        X = df[INPUT_FEATURES].copy()
        X = self._encode_categorical(X)
        # Validate and clean data
        X = self._validate_and_clean(X, stage='predict')
        # Impute any remaining NaNs
        X_imputed = self.imputer.transform(X)
        X_scaled = self.scaler.transform(X_imputed)
        
        # Final safety check
        assert not np.isnan(X_scaled).any(), "NaN values detected in scaled features before KMeans.predict()"
        
        cluster_ids = self.kmeans.predict(X_scaled)
        return cluster_ids
    
    @staticmethod
    def _validate_and_clean(X, stage='predict'):
        """
        Validate input data and clean NaN values.
        
        Args:
            X: DataFrame with features
            stage: 'fit' or 'predict' for logging
            
        Returns:
            Cleaned DataFrame
        """
        X = X.copy()
        
        # Log NaN summary before cleaning (silent mode - no prints)
        nan_summary = X.isna().sum()
        
        # Fill NaNs in categorical columns with mode (most common value)
        categorical_cols = ['mood', 'weather_condition', 'season', 'time_of_day', 'temperature_category']
        for col in categorical_cols:
            if col in X.columns and X[col].isna().any():
                mode_val = X[col].mode()[0] if len(X[col].mode()) > 0 else 'Happy'
                X[col].fillna(mode_val, inplace=True)
        
        # Fill NaNs in numeric columns with 0 (safe for environmental scores)
        numeric_cols = [col for col in X.columns if X[col].dtype in ['float64', 'int64']]
        for col in numeric_cols:
            if X[col].isna().any():
                X[col].fillna(0, inplace=True)
        
        return X
    
    @staticmethod
    def _encode_categorical(X):
        """
        Safely encode categorical features with NaN handling.
        Unmapped values are set to 0 (safe default).
        """
        X = X.copy()
        
        categorical_cols = {
            'mood': ['Happy', 'Stressed', 'Tired', 'Lonely', 'Celebratory'],
            'weather_condition': ['Sunny', 'Rainy', 'Cloudy', 'Snowy', 'Stormy'],
            'season': ['Spring', 'Summer', 'Autumn', 'Winter'],
            'time_of_day': ['Morning', 'Afternoon', 'Evening', 'Night'],
            'temperature_category': ['cold', 'mild', 'warm', 'hot']
        }
        
        for col, categories in categorical_cols.items():
            if col in X.columns:
                # Create mapping with safe default (0)
                mapping = {cat: idx for idx, cat in enumerate(categories)}
                # Apply mapping and fill unmapped values with 0
                X[col] = X[col].astype(str).map(mapping).fillna(0).astype(int)
        
        return X


# ============================================================================
# LAYER 2: SUPERVISED CLASSIFIER
# ============================================================================

class CakePredictionClassifier:
    """
    Random Forest classifier to predict cake preference.
    Input: all features + cluster_id
    Output: probability distribution over cakes
    """
    
    def __init__(self):
        self.classifier = RandomForestClassifier(
            n_estimators=100,
            max_depth=15,
            random_state=42,
            n_jobs=-1
        )
        self.label_encoder = LabelEncoder()
        self.feature_scaler = StandardScaler()
        self.imputer = SimpleImputer(strategy='mean')
        self.is_fitted = False
        self.n_classes = 0
        self.classes_ = None
    
    def fit(self, df):
        """Train classifier on full feature set including cluster_id."""
        # Defensive validation: ensure cluster_id is present
        if 'cluster_id' not in df.columns:
            raise ValueError(
                f"cluster_id missing from dataframe. "
                f"Available columns: {df.columns.tolist()}. "
                f"BehavioralSegmentation.fit() must be called first to add cluster_id."
            )
        
        # Prepare features
        feature_cols = INPUT_FEATURES + ['cluster_id']
        X = df[feature_cols].copy()
        X = self._encode_features(X)
        # Validate and clean
        X = self._validate_and_clean(X, stage='fit')
        # Impute remaining NaNs
        X_imputed = self.imputer.fit_transform(X)
        X_scaled = self.feature_scaler.fit_transform(X_imputed)
        
        # Encode target
        y = df[TARGET].copy()
        y_encoded = self.label_encoder.fit_transform(y)
        
        # Train classifier
        self.classifier.fit(X_scaled, y_encoded)
        self.n_classes = len(self.label_encoder.classes_)
        self.classes_ = self.label_encoder.classes_
        self.is_fitted = True
        
        return self
    
    def predict_proba(self, df):
        """Return probability distribution over all cakes."""
        if not self.is_fitted:
            raise ValueError("Classifier not fitted. Call fit() first.")
        
        # Defensive validation
        if 'cluster_id' not in df.columns:
            raise ValueError(
                f"cluster_id missing from dataframe. "
                f"Available columns: {df.columns.tolist()}. "
                f"Segmentation.predict() must be called first to assign cluster_id."
            )
        
        feature_cols = INPUT_FEATURES + ['cluster_id']
        X = df[feature_cols].copy()
        X = self._encode_features(X)
        # Validate and clean
        X = self._validate_and_clean(X, stage='predict')
        # Impute remaining NaNs
        X_imputed = self.imputer.transform(X)
        X_scaled = self.feature_scaler.transform(X_imputed)
        
        # Final safety check
        assert not np.isnan(X_scaled).any(), "NaN values detected in scaled features before classifier.predict_proba()"
        
        proba = self.classifier.predict_proba(X_scaled)
        
        # Return as dict: cake -> probability
        result_list = []
        for row_idx in range(len(df)):
            cake_probs = {}
            for cake_idx, cake_name in enumerate(self.classes_):
                cake_probs[cake_name] = proba[row_idx, cake_idx]
            result_list.append(cake_probs)
        
        return result_list
    
    @staticmethod
    def _validate_and_clean(X, stage='predict'):
        """Validate input data and clean NaN values."""
        X = X.copy()
        
        # Log NaN summary
        nan_summary = X.isna().sum()
        
        # Fill categorical NaNs with mode
        categorical_cols = ['mood', 'weather_condition', 'season', 'time_of_day', 'temperature_category']
        for col in categorical_cols:
            if col in X.columns and X[col].isna().any():
                mode_val = X[col].mode()[0] if len(X[col].mode()) > 0 else 0
                X[col].fillna(mode_val, inplace=True)
        
        # Fill numeric NaNs with 0
        numeric_cols = [col for col in X.columns if X[col].dtype in ['float64', 'int64']]
        for col in numeric_cols:
            if X[col].isna().any():
                X[col].fillna(0, inplace=True)
        
        return X
    
    @staticmethod
    def _encode_features(X):
        """Safely encode categorical features with NaN handling."""
        X = X.copy()
        
        categorical_cols = {
            'mood': ['Happy', 'Stressed', 'Tired', 'Lonely', 'Celebratory'],
            'weather_condition': ['Sunny', 'Rainy', 'Cloudy', 'Snowy', 'Stormy'],
            'season': ['Spring', 'Summer', 'Autumn', 'Winter'],
            'time_of_day': ['Morning', 'Afternoon', 'Evening', 'Night'],
            'temperature_category': ['cold', 'mild', 'warm', 'hot']
        }
        
        for col, categories in categorical_cols.items():
            if col in X.columns:
                mapping = {cat: idx for idx, cat in enumerate(categories)}
                # Safe mapping: unmapped values become 0 instead of NaN
                X[col] = X[col].astype(str).map(mapping).fillna(0).astype(int)
        
        return X


# ============================================================================
# LAYER 3: RANKING & PERSONALIZATION
# ============================================================================

class RankingLayer:
    """
    Combines ML classifier output with personalization factors:
    - trend_popularity_score (20%)
    - health alignment (20%)
    - cluster affinity (10%)
    - ML probability (50%)
    """
    
    def __init__(self):
        self.cluster_cake_stats = None
    
    def fit_cluster_stats(self, df):
        """Learn which cakes are popular in each cluster."""
        stats = {}
        for cluster_id in df['cluster_id'].unique():
            cluster_data = df[df['cluster_id'] == cluster_id]
            cake_counts = cluster_data[TARGET].value_counts(normalize=True)
            stats[cluster_id] = cake_counts.to_dict()
        
        self.cluster_cake_stats = stats
        return self
    
    def rank_cakes(
        self,
        ml_probs: dict,
        trend_popularity: float,
        health_preference: int,
        cluster_id: int
    ):
        """
        Compute final ranking scores using weighted combination of:
        - ML probability (0.5)
        - Trend popularity (0.2)
        - Health alignment (0.2)
        - Cluster affinity (0.1)
        
        Returns: list of (cake_name, final_score, components)
        """
        final_scores = []
        
        for cake_name, ml_prob in ml_probs.items():
            # Component 1: ML Probability (weight: 0.5)
            ml_score = ml_prob * 0.5
            
            # Component 2: Trend Popularity (weight: 0.2)
            # Normalize trend_popularity (0-1) if not already
            trend_score = (trend_popularity / 1.0) * 0.2 if trend_popularity <= 1 else 0.2
            
            # Component 3: Health Alignment (weight: 0.2)
            cake_health = CAKE_HEALTH_PROFILES.get(cake_name, 5)
            health_alignment = 1.0 - abs(cake_health - health_preference) / 10.0
            health_score = max(0, health_alignment) * 0.2
            
            # Component 4: Cluster Affinity Bonus (weight: 0.1)
            cluster_affinity = 0.0
            if self.cluster_cake_stats and cluster_id in self.cluster_cake_stats:
                cluster_prefs = self.cluster_cake_stats[cluster_id]
                cluster_affinity = cluster_prefs.get(cake_name, 0.0) * 0.1
            
            # Final composite score
            final_score = ml_score + trend_score + health_score + cluster_affinity
            
            final_scores.append({
                'cake_name': cake_name,
                'final_score': final_score,
                'ml_prob': ml_prob,
                'trend_score': trend_score,
                'health_score': health_score,
                'cluster_affinity': cluster_affinity,
                'health_alignment': health_alignment
            })
        
        # Sort by final_score descending
        final_scores.sort(key=lambda x: x['final_score'], reverse=True)
        
        return final_scores


# ============================================================================
# COMPLETE HYBRID PIPELINE
# ============================================================================

class HybridRecommendationSystem:
    """
    Complete 3-layer hybrid system combining:
    1. Behavioral segmentation (KMeans)
    2. Cake prediction classifier
    3. Personalized ranking
    """
    
    def __init__(self):
        self.segmentation = BehavioralSegmentation(n_clusters=N_CLUSTERS)
        self.classifier = CakePredictionClassifier()
        self.ranker = RankingLayer()
        self.is_trained = False
    
    def train(self, csv_path=None):
        """Train all 3 layers on dataset."""
        if csv_path is None:
            csv_path = DATA_PATH / "beige_ai_cake_dataset_v2.csv"
        
        df = pd.read_csv(csv_path)
        
        # Layer 1: K-Means Segmentation
        df = self.segmentation.fit(df)
        
        # Layer 2: Classifier
        self.classifier.fit(df)
        # Layer 3: Ranking
        self.ranker.fit_cluster_stats(df)
        
        # Mark system as trained
        self.is_trained = True
        
        return self
    
    def predict(self, user_input):
        """
        Complete inference pipeline.
        
        Args:
            user_input: Dict with keys matching INPUT_FEATURES
                       Must also include 'trend_popularity_score' and 'health_preference'
        
        Returns:
            List of top-5 recommendations with scores and explanations
        """
        logger.info("=" * 80)
        logger.info("STARTING 3-LAYER HYBRID INFERENCE PIPELINE")
        logger.info("=" * 80)
        
        if not self.is_trained:
            logger.error("System not trained. Call train() first.")
            raise ValueError("System not trained. Call train() first.")
        
        try:
            # Create single-row dataframe for inference
            input_df = pd.DataFrame([user_input])
            logger.debug(f"Input dataframe created: shape {input_df.shape}")
            
            # ==================================================================
            # LAYER 1: K-MEANS BEHAVIORAL SEGMENTATION
            # ==================================================================
            logger.info("LAYER 1: Running K-Means Behavioral Segmentation...")
            try:
                cluster_id = self.segmentation.predict(input_df)[0]
                input_df['cluster_id'] = cluster_id
                logger.info(f"✓ Segmentation complete: Assigned to cluster {cluster_id}")
                logger.debug(f"  Cluster ID type: {type(cluster_id)}, value: {cluster_id}")
            except Exception as e:
                logger.error(f"✗ Segmentation failed: {str(e)}", exc_info=True)
                raise
            
            # ==================================================================
            # LAYER 2: ML CLASSIFICATION (Random Forest)
            # ==================================================================
            logger.info("LAYER 2: Running ML Classification (Random Forest)...")
            try:
                ml_probs_list = self.classifier.predict_proba(input_df)
                ml_probs = ml_probs_list[0]
                logger.info(f"✓ Classification complete: Generated {len(ml_probs)} probability scores")
                logger.debug(f"  Top 3 class probabilities: {sorted(ml_probs, reverse=True)[:3]}")
            except Exception as e:
                logger.error(f"✗ Classification failed: {str(e)}", exc_info=True)
                raise
            
            # ==================================================================
            # LAYER 3: RANKING & PERSONALIZATION
            # ==================================================================
            logger.info("LAYER 3: Running Ranking & Personalization Layer...")
            try:
                ranked_cakes = self.ranker.rank_cakes(
                    ml_probs=ml_probs,
                    trend_popularity=user_input.get('trend_popularity_score', 0.5),
                    health_preference=user_input.get('health_preference', 5),
                    cluster_id=int(cluster_id)
                )
                logger.info(f"✓ Ranking complete: Generated {len(ranked_cakes)} ranked recommendations")
                logger.debug(f"  Top 3: {[r['cake_name'] for r in ranked_cakes[:3]]}")
            except Exception as e:
                logger.error(f"✗ Ranking failed: {str(e)}", exc_info=True)
                raise
            
            # Process results (silent mode)
            results = {}
            for idx, cake_result in enumerate(ranked_cakes):
                results[cake_result['cake_name']] = {
                    'rank': idx + 1,
                    'final_score': cake_result['final_score'],
                    'ml_probability': cake_result['ml_prob'],
                    'health_alignment': cake_result['health_alignment'],
                    'cluster_affinity': cake_result['cluster_affinity'],
                    'cluster_id': int(cluster_id),
                    'explanation': self._generate_explanation(
                        cake_result,
                        user_input,
                        cluster_id
                    )
                }
            
            logger.info("=" * 80)
            logger.info("✓ 3-LAYER HYBRID INFERENCE PIPELINE COMPLETE")
            logger.info("=" * 80)
            return results, int(cluster_id)
        
        except Exception as e:
            logger.error(f"✗ Entire prediction pipeline failed: {str(e)}", exc_info=True)
            raise
    
    @staticmethod
    def _generate_explanation(cake_result, user_input, cluster_id):
        """Generate human-readable explanation."""
        mood = user_input.get('mood', 'Unknown')
        weather = user_input.get('weather_condition', 'Unknown')
        health = user_input.get('health_preference', 5)
        health_alignment = cake_result.get('health_alignment', 0)
        ml_prob = cake_result.get('ml_prob', 0)
        
        explanation = f"Recommended for your {mood.lower()} mood in {weather.lower()} weather. "
        
        if health_alignment > 0.6:
            explanation += f"Strong health alignment with your preference (score: {health_alignment:.1f}). "
        
        if ml_prob > 0.3:
            explanation += f"High ML prediction confidence ({ml_prob*100:.0f}%). "
        else:
            explanation += f"Balanced recommendation ({ml_prob*100:.0f}% model confidence). "
        
        explanation += f"Cluster preference group validates this choice."
        
        return explanation
    
    def save(self, models_dir=None):
        """Save all trained models to production directory."""
        # ENFORCE: Always save to production directory, never allow custom paths
        models_dir = PRODUCTION_MODELS_DIR
        models_dir.mkdir(parents=True, exist_ok=True)
        
        joblib.dump(self.segmentation.kmeans, models_dir / "kmeans_model.pkl")
        joblib.dump(self.segmentation.scaler, models_dir / "kmeans_scaler.pkl")
        
        joblib.dump(self.classifier.classifier, models_dir / "classifier_model.pkl")
        joblib.dump(self.classifier.label_encoder, models_dir / "classifier_encoder.pkl")
        joblib.dump(self.classifier.feature_scaler, models_dir / "classifier_scaler.pkl")
        
        joblib.dump(self.ranker.cluster_cake_stats, models_dir / "cluster_stats.pkl")
        
        # Validate that all required files were saved
        validate_production_models()
        return self
    
    def load(self, models_dir=None):
        """
        Load all trained models from production directory.
        
        CRITICAL: Only loads from models/production/
        Fails immediately if any file is missing.
        """
        # ENFORCE: Always load from production directory
        models_dir = PRODUCTION_MODELS_DIR
        
        # Validate before attempting to load
        validate_production_models()
        
        # Load all required models
        self.segmentation.kmeans = joblib.load(models_dir / "kmeans_model.pkl")
        self.segmentation.scaler = joblib.load(models_dir / "kmeans_scaler.pkl")
        self.segmentation.is_fitted = True
        
        self.classifier.classifier = joblib.load(models_dir / "classifier_model.pkl")
        self.classifier.label_encoder = joblib.load(models_dir / "classifier_encoder.pkl")
        self.classifier.feature_scaler = joblib.load(models_dir / "classifier_scaler.pkl")
        self.classifier.n_classes = len(self.classifier.label_encoder.classes_)
        self.classifier.classes_ = self.classifier.label_encoder.classes_
        self.classifier.is_fitted = True
        
        self.ranker.cluster_cake_stats = joblib.load(models_dir / "cluster_stats.pkl")
        
        self.is_trained = True
        
        return self

# ============================================================================
# CONVENIENCE FUNCTION FOR STREAMLIT
# ============================================================================

def create_or_load_system(train_if_missing=True):
    """
    Create system and load pretrained models if available.
    If not available and train_if_missing=True, train from scratch.
    """
    system = HybridRecommendationSystem()
    
    models_dir = MODELS_DIR
    model_files = [
        "kmeans_model.pkl",
        "kmeans_scaler.pkl",
        "classifier_model.pkl",
        "classifier_encoder.pkl",
        "classifier_scaler.pkl",
        "cluster_stats.pkl"
    ]
    
    models_exist = all((models_dir / f).exists() for f in model_files)
    
    if models_exist:
        print("[INIT] Loading pretrained hybrid system...")
        system.load()
    elif train_if_missing:
        print("[INIT] Training new hybrid system...")
        system.save()
    else:
        pass
    
    return system
