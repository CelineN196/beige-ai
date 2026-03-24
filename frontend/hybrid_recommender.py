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
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib

warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================

DATA_PATH = Path(__file__).resolve().parent.parent / "backend" / "data"
MODELS_DIR = Path(__file__).resolve().parent.parent / "models"

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
    "Dark Chocolate Sea Salt Cake": 2,    # Low health score
    "Matcha Zen Cake": 8,                 # High health
    "Citrus Cloud Cake": 7,               # Medium-high
    "Berry Garden Cake": 8,               # High
    "Silk Cheesecake": 3,                 # Low
    "Earthy Wellness Cake": 9,            # Very high
    "Café Tiramisu": 5,                   # Medium
    "Korean Sesame Mini Bread": 6,        # Medium-high
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
        self.is_fitted = False
    
    def fit(self, df):
        """Train KMeans on input features."""
        X = df[INPUT_FEATURES].copy()
        # Encode categorical features
        X = self._encode_categorical(X)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Fit KMeans
        self.kmeans.fit(X_scaled)
        self.is_fitted = True
        
        print(f"✅ KMeans fitted with {self.n_clusters} clusters")
        
        # Add cluster assignments to dataframe
        df['cluster_id'] = self.kmeans.labels_
        
        return df
    
    def predict(self, df):
        """Assign cluster IDs to new data."""
        if not self.is_fitted:
            raise ValueError("BehavioralSegmentation not fitted. Call fit() first.")
        
        X = df[INPUT_FEATURES].copy()
        X = self._encode_categorical(X)
        X_scaled = self.scaler.transform(X)
        
        cluster_ids = self.kmeans.predict(X_scaled)
        return cluster_ids
    
    @staticmethod
    def _encode_categorical(X):
        """Simple one-hot or label encoding for categorical features."""
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
                X[col] = X[col].astype(str).map(
                    {cat: idx for idx, cat in enumerate(categories)}
                )
        
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
        self.is_fitted = False
        self.n_classes = 0
        self.classes_ = None
    
    def fit(self, df):
        """Train classifier on full feature set including cluster_id."""
        # Ensure cluster_id is present
        if 'cluster_id' not in df.columns:
            raise ValueError("cluster_id must be in dataframe. Run BehavioralSegmentation first.")
        
        # Prepare features
        feature_cols = INPUT_FEATURES + ['cluster_id']
        X = df[feature_cols].copy()
        X = self._encode_features(X)
        X_scaled = self.feature_scaler.fit_transform(X)
        
        # Encode target
        y = df[TARGET].copy()
        y_encoded = self.label_encoder.fit_transform(y)
        
        # Train classifier
        self.classifier.fit(X_scaled, y_encoded)
        self.n_classes = len(self.label_encoder.classes_)
        self.classes_ = self.label_encoder.classes_
        self.is_fitted = True
        
        print(f"✅ Classifier fitted on {len(feature_cols)} features")
        print(f"   Predicting {self.n_classes} cake classes")
        
        return self
    
    def predict_proba(self, df):
        """Return probability distribution over all cakes."""
        if not self.is_fitted:
            raise ValueError("Classifier not fitted. Call fit() first.")
        
        feature_cols = INPUT_FEATURES + ['cluster_id']
        X = df[feature_cols].copy()
        X = self._encode_features(X)
        X_scaled = self.feature_scaler.transform(X)
        
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
    def _encode_features(X):
        """Encode categorical features in input."""
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
                X[col] = X[col].astype(str).map(
                    {cat: idx for idx, cat in enumerate(categories)}
                )
        
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
        
        print(f"[TRAINING] Loading dataset from {csv_path}")
        df = pd.read_csv(csv_path)
        print(f"[TRAINING] Loaded {len(df)} samples, {len(df.columns)} features")
        
        # Layer 1: K-Means Segmentation
        print("\n[LAYER 1] Training behavioral segmentation (K-Means)...")
        df = self.segmentation.fit(df)
        
        # Layer 2: Classifier
        print("[LAYER 2] Training cake prediction classifier (Random Forest)...")
        self.classifier.fit(df)
        
        # Layer 3: Ranking
        print("[LAYER 3] Learning cluster-cake statistics for ranking...")
        self.ranker.fit_cluster_stats(df)
        
        self.is_trained = True
        print("\n✅ All 3 layers trained successfully!")
        
        return self
    
    def infer(self, user_input: dict):
        """
        Complete inference pipeline.
        
        Args:
            user_input: Dict with keys matching INPUT_FEATURES
                       Must also include 'trend_popularity_score' and 'health_preference'
        
        Returns:
            List of top-5 recommendations with scores and explanations
        """
        if not self.is_trained:
            raise ValueError("System not trained. Call train() first.")
        
        # Create single-row dataframe for inference
        input_df = pd.DataFrame([user_input])
        
        # Step 1: Assign cluster
        cluster_id = self.segmentation.predict(input_df)[0]
        input_df['cluster_id'] = cluster_id
        
        # Step 2: Get ML probabilities
        ml_probs_list = self.classifier.predict_proba(input_df)
        ml_probs = ml_probs_list[0]
        
        # Step 3: Rank using personalization layer
        ranked_cakes = self.ranker.rank_cakes(
            ml_probs=ml_probs,
            trend_popularity=user_input.get('trend_popularity_score', 0.5),
            health_preference=user_input.get('health_preference', 5),
            cluster_id=int(cluster_id)
        )
        
        # Step 4: Format results
        results = {}
        for idx, cake_result in enumerate(ranked_cakes[:5]):  # Top 5
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
        
        return results, int(cluster_id)
    
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
        """Save all trained models."""
        if models_dir is None:
            models_dir = MODELS_DIR
        
        models_dir.mkdir(parents=True, exist_ok=True)
        
        joblib.dump(self.segmentation.kmeans, models_dir / "kmeans_model.pkl")
        joblib.dump(self.segmentation.scaler, models_dir / "kmeans_scaler.pkl")
        
        joblib.dump(self.classifier.classifier, models_dir / "classifier_model.pkl")
        joblib.dump(self.classifier.label_encoder, models_dir / "classifier_encoder.pkl")
        joblib.dump(self.classifier.feature_scaler, models_dir / "classifier_scaler.pkl")
        
        joblib.dump(self.ranker.cluster_cake_stats, models_dir / "cluster_stats.pkl")
        
        print(f"✅ All models saved to {models_dir}")
        
        return self
    
    def load(self, models_dir=None):
        """Load all trained models."""
        if models_dir is None:
            models_dir = MODELS_DIR
        
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
        
        print(f"✅ All models loaded from {models_dir}")
        
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
        system.train()
        system.save()
    else:
        raise ValueError("Models not found and train_if_missing=False")
    
    return system
