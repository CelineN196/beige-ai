"""
Beige.AI Phase 2: Customer Segmentation & Pattern Mining
================================================================
Analyze the dataset to discover behavioral patterns behind cake 
selection and build customer segments using unsupervised learning 
and association rule mining.

This script performs:
1. Data loading & preprocessing
2. K-Means customer segmentation with elbow method
3. Detailed cluster profiling
4. Association rule mining (Apriori)
5. PCA visualization and heatmap analysis

Author: Senior Data Scientist
Date: March 2026
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.pipeline import Pipeline
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, association_rules
import warnings
from pathlib import Path
import sys

# Add frontend directory to path to import menu_config
_FRONTEND_DIR = str(Path(__file__).resolve().parent.parent.parent / "frontend")
if _FRONTEND_DIR not in sys.path:
    sys.path.insert(0, _FRONTEND_DIR)

from menu_config import CAKE_MENU

warnings.filterwarnings('ignore')

# Set style for visualizations
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)

print("="*70)
print("BEIGE.AI PHASE 2: CUSTOMER SEGMENTATION & PATTERN MINING")
print("="*70)

# ============================================================================
# SECTION 1: LOAD AND INSPECT DATA
# ============================================================================

print("\n[1/5] Loading and inspecting dataset...")

# Load dataset
df = pd.read_csv('/Users/queenceline/Downloads/Beige AI/beige_ai_cake_dataset_v2.csv')

# Validate that cake categories match the configured menu
unique_cakes_in_data = set(df['cake_category'].unique())
configured_cakes = set(CAKE_MENU)
if unique_cakes_in_data == configured_cakes:
    print("✓ Cake categories match configuration (menu_config.py)")
else:
    missing_in_config = unique_cakes_in_data - configured_cakes
    extra_in_config = configured_cakes - unique_cakes_in_data
    if missing_in_config:
        print(f"⚠ Cakes in data missing from config: {missing_in_config}")
    if extra_in_config:
        print(f"⚠ Cakes in config missing from data: {extra_in_config}")

print(f"\n--- Dataset Overview ---")
print(f"Shape: {df.shape}")
print(f"\nMissing values:\n{df.isnull().sum()}")
print(f"\nData types:\n{df.dtypes}")
print(f"\nFirst 5 rows:\n{df.head()}")

# ============================================================================
# SECTION 2: DATA PREPROCESSING
# ============================================================================

print("\n\n[2/5] Preprocessing data...")

# Define feature columns
numerical_features = ['sweetness_preference', 'health_preference']
categorical_features = ['mood', 'weather_condition', 'time_of_day']
target_feature = 'cake_category'

# Create preprocessing pipeline
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numerical_features),
        ('cat', OneHotEncoder(sparse_output=False, handle_unknown='ignore'), 
         categorical_features)
    ]
)

# Fit and transform
X_preprocessed = preprocessor.fit_transform(df[numerical_features + categorical_features])

# Get feature names for later use
feature_names = (
    numerical_features + 
    preprocessor.named_transformers_['cat'].get_feature_names_out(categorical_features).tolist()
)

print(f"✓ Preprocessed {X_preprocessed.shape[0]} samples")
print(f"✓ Feature dimensions: {X_preprocessed.shape[1]}")
print(f"  - Numerical features: {len(numerical_features)}")
print(f"  - Categorical features (one-hot encoded): {X_preprocessed.shape[1] - len(numerical_features)}")

# ============================================================================
# SECTION 3: K-MEANS CUSTOMER SEGMENTATION
# ============================================================================

print("\n[3/5] K-Means customer segmentation...")

# Elbow Method to determine optimal K
inertias = []
silhouette_scores = []
K_range = range(2, 11)

for k in K_range:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(X_preprocessed)
    inertias.append(kmeans.inertia_)

# Plot elbow curve
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

ax1.plot(K_range, inertias, 'bo-', linewidth=2, markersize=8)
ax1.set_xlabel('Number of Clusters (K)', fontsize=11, fontweight='bold')
ax1.set_ylabel('Inertia (Within-cluster sum of squares)', fontsize=11, fontweight='bold')
ax1.set_title('Elbow Method for Optimal K', fontsize=12, fontweight='bold')
ax1.grid(True, alpha=0.3)
ax1.set_xticks(K_range)

# Calculate optimal K using elbow heuristic (steepest change)
diffs = np.diff(inertias)
second_diffs = np.diff(diffs)
optimal_k_idx = np.argmax(second_diffs) + 2  # +2 because we start from k=2
optimal_k = list(K_range)[optimal_k_idx]

# If optimal K is outside reasonable range, default to 4
if optimal_k < 3 or optimal_k > 6:
    optimal_k = 4

ax1.axvline(x=optimal_k, color='red', linestyle='--', linewidth=2, label=f'Optimal K = {optimal_k}')
ax1.legend(fontsize=10)

print(f"✓ Elbow method analysis complete")
print(f"✓ Optimal number of clusters: {optimal_k}")

# Train final KMeans model
kmeans_final = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
cluster_labels = kmeans_final.fit_predict(X_preprocessed)

df['cluster'] = cluster_labels

print(f"✓ Cluster distribution:\n{df['cluster'].value_counts().sort_index()}\n")

# ============================================================================
# SECTION 3B: CLUSTER PROFILING
# ============================================================================

print("--- Cluster Profiles ---")

cluster_profiles = []

for cluster_id in sorted(df['cluster'].unique()):
    cluster_data = df[df['cluster'] == cluster_id]
    
    # Calculate statistics
    mean_sweetness = cluster_data['sweetness_preference'].mean()
    mean_health = cluster_data['health_preference'].mean()
    most_frequent_mood = cluster_data['mood'].mode()[0]
    most_frequent_cake = cluster_data['cake_category'].mode()[0]
    most_frequent_time = cluster_data['time_of_day'].mode()[0]
    most_frequent_weather = cluster_data['weather_condition'].mode()[0]
    size = len(cluster_data)
    
    # Create readable cluster name based on characteristics
    if mean_health > 7:
        profile_type = "Health-Conscious"
    elif mean_sweetness > 7:
        profile_type = "Indulgent"
    elif mean_sweetness < 4:
        profile_type = "Light & Savory"
    else:
        profile_type = "Balanced"
    
    if most_frequent_time in ['Morning', 'Afternoon']:
        time_segment = "Daytime"
    else:
        time_segment = "Evening"
    
    cluster_name = f"{profile_type} {time_segment} Customers"
    
    # Store profile
    profile = {
        'cluster_id': cluster_id,
        'name': cluster_name,
        'size': size,
        'percent': (size / len(df) * 100),
        'mean_sweetness': mean_sweetness,
        'mean_health': mean_health,
        'top_mood': most_frequent_mood,
        'top_cake': most_frequent_cake,
        'top_time': most_frequent_time,
        'top_weather': most_frequent_weather
    }
    
    cluster_profiles.append(profile)
    
    # Print detailed profile
    print(f"\nCluster {cluster_id}: {cluster_name}")
    print(f"  Size: {size:,} customers ({profile['percent']:.1f}%)")
    print(f"  Sweetness Preference: {mean_sweetness:.2f}/10")
    print(f"  Health Preference: {mean_health:.2f}/10")
    print(f"  Most Frequent Mood: {most_frequent_mood}")
    print(f"  Most Frequent Cake: {most_frequent_cake}")
    print(f"  Preferred Time: {most_frequent_time}")
    print(f"  Preferred Weather: {most_frequent_weather}")

# ============================================================================
# SECTION 4: ASSOCIATION RULE MINING (APRIORI)
# ============================================================================

print("\n\n[4/5] Association rule mining...")

# Prepare data for market basket analysis
# Create transactions: each row is a transaction with categorical features
categorical_data = df[['mood', 'weather_condition', 'time_of_day', 'cake_category']].copy()

# Convert to transaction format (add prefix to feature names for clarity)
transactions = []
for idx, row in categorical_data.iterrows():
    transaction = [
        f"mood:{row['mood']}",
        f"weather:{row['weather_condition']}",
        f"time:{row['time_of_day']}",
        f"cake:{row['cake_category']}"
    ]
    transactions.append(transaction)

# Convert to transaction matrix
te = TransactionEncoder()
te_ary = te.fit(transactions).transform(transactions)
transaction_df = pd.DataFrame(te_ary, columns=te.columns_)

print(f"✓ Transaction matrix created: {transaction_df.shape}")

# Run Apriori algorithm
frequent_itemsets = apriori(transaction_df, min_support=0.05, use_colnames=True)
print(f"✓ Found {len(frequent_itemsets)} frequent itemsets (min_support=0.05)")

# Generate association rules
if len(frequent_itemsets) > 1:
    rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1.2)
    
    # Sort by lift
    rules_sorted = rules.sort_values('lift', ascending=False)
    
    print(f"✓ Generated {len(rules_sorted)} association rules (lift >= 1.2)")
    
    # Display top 10 rules
    print("\n--- Top 10 Association Rules by Lift ---")
    for idx, (_, rule) in enumerate(rules_sorted.head(10).iterrows(), 1):
        antecedents = ', '.join(list(rule['antecedents']))
        consequents = ', '.join(list(rule['consequents']))
        support = rule['support']
        confidence = rule['confidence']
        lift = rule['lift']
        
        print(f"\n{idx}. {{{antecedents}}} → {{{consequents}}}")
        print(f"   Support: {support:.4f} | Confidence: {confidence:.4f} | Lift: {lift:.4f}")
else:
    print("⚠ Not enough frequent itemsets to generate association rules")
    rules_sorted = pd.DataFrame()

# ============================================================================
# SECTION 5: VISUALIZATIONS
# ============================================================================

print("\n\n[5/5] Creating visualizations...")

# Create a large figure with multiple subplots
fig = plt.figure(figsize=(16, 12))

# --------- Visualization 1: PCA Cluster Visualization ---------
ax1 = plt.subplot(2, 3, 1)

pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_preprocessed)

scatter = ax1.scatter(X_pca[:, 0], X_pca[:, 1], c=cluster_labels, cmap='viridis', 
                      alpha=0.6, s=20, edgecolors='black', linewidth=0.5)

# Plot cluster centers
centers_pca = pca.transform(kmeans_final.cluster_centers_)
ax1.scatter(centers_pca[:, 0], centers_pca[:, 1], c='red', marker='X', s=300, 
           edgecolors='black', linewidth=2, label='Cluster Centers')

ax1.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%})', fontweight='bold')
ax1.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%})', fontweight='bold')
ax1.set_title('Customer Clusters (PCA Visualization)', fontsize=12, fontweight='bold')
ax1.legend()
ax1.grid(True, alpha=0.3)
cbar = plt.colorbar(scatter, ax=ax1)
cbar.set_label('Cluster ID', fontweight='bold')

# --------- Visualization 2: Cluster Size Distribution ---------
ax2 = plt.subplot(2, 3, 2)

cluster_sizes = df['cluster'].value_counts().sort_index()
colors_bar = plt.cm.viridis(np.linspace(0, 1, len(cluster_sizes)))
bars = ax2.bar(cluster_sizes.index, cluster_sizes.values, color=colors_bar, 
               edgecolor='black', linewidth=1.5)

# Add percentage labels on bars
for i, (idx, size) in enumerate(cluster_sizes.items()):
    percentage = size / len(df) * 100
    ax2.text(idx, size, f'{percentage:.1f}%', ha='center', va='bottom', fontweight='bold')

ax2.set_xlabel('Cluster ID', fontweight='bold')
ax2.set_ylabel('Number of Customers', fontweight='bold')
ax2.set_title('Cluster Size Distribution', fontsize=12, fontweight='bold')
ax2.grid(axis='y', alpha=0.3)

# --------- Visualization 3: Cluster vs Cake Category Heatmap ---------
ax3 = plt.subplot(2, 3, 3)

# Create crosstab
cluster_cake_crosstab = pd.crosstab(df['cluster'], df['cake_category'], normalize='index') * 100

sns.heatmap(cluster_cake_crosstab, annot=True, fmt='.1f', cmap='YlOrRd', ax=ax3, 
            cbar_kws={'label': 'Percentage (%)'}, linewidths=0.5, linecolor='gray')
ax3.set_xlabel('Cake Category', fontweight='bold')
ax3.set_ylabel('Cluster ID', fontweight='bold')
ax3.set_title('Cake Preferences by Cluster (%)', fontsize=12, fontweight='bold')
plt.setp(ax3.get_xticklabels(), rotation=45, ha='right', fontsize=9)

# --------- Visualization 4: Sweetness vs Health Preference by Cluster ---------
ax4 = plt.subplot(2, 3, 4)

for cluster_id in sorted(df['cluster'].unique()):
    cluster_data = df[df['cluster'] == cluster_id]
    ax4.scatter(cluster_data['sweetness_preference'], 
               cluster_data['health_preference'],
               label=f'Cluster {cluster_id}', alpha=0.5, s=30)

ax4.set_xlabel('Sweetness Preference', fontweight='bold')
ax4.set_ylabel('Health Preference', fontweight='bold')
ax4.set_title('Preference Profile by Cluster', fontsize=12, fontweight='bold')
ax4.legend(loc='best')
ax4.grid(True, alpha=0.3)

# --------- Visualization 5: Mood Distribution by Cluster ---------
ax5 = plt.subplot(2, 3, 5)

mood_cluster = pd.crosstab(df['mood'], df['cluster'], normalize='columns') * 100
mood_cluster.T.plot(kind='bar', ax=ax5, width=0.8, colormap='Set2')

ax5.set_xlabel('Cluster ID', fontweight='bold')
ax5.set_ylabel('Percentage (%)', fontweight='bold')
ax5.set_title('Mood Distribution by Cluster', fontsize=12, fontweight='bold')
ax5.legend(title='Mood', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
plt.setp(ax5.get_xticklabels(), rotation=0)
ax5.grid(axis='y', alpha=0.3)

# --------- Visualization 6: Time of Day Distribution by Cluster ---------
ax6 = plt.subplot(2, 3, 6)

time_cluster = pd.crosstab(df['time_of_day'], df['cluster'], normalize='columns') * 100
time_cluster.T.plot(kind='bar', ax=ax6, width=0.8, colormap='Set3')

ax6.set_xlabel('Cluster ID', fontweight='bold')
ax6.set_ylabel('Percentage (%)', fontweight='bold')
ax6.set_title('Time of Day Distribution by Cluster', fontsize=12, fontweight='bold')
ax6.legend(title='Time', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
plt.setp(ax6.get_xticklabels(), rotation=0)
ax6.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('/Users/queenceline/Downloads/Beige AI/phase2_analytics_visualizations.png', 
            dpi=300, bbox_inches='tight')
print("✓ Saved visualization: phase2_analytics_visualizations.png")
plt.close()

# ============================================================================
# SECTION 6: SAVE RESULTS
# ============================================================================

print("\n[5/5] Saving results...")

# Save dataset with cluster assignments
df_with_clusters = df.copy()
df_with_clusters.to_csv('/Users/queenceline/Downloads/Beige AI/beige_customer_clusters.csv', 
                        index=False)
print(f"✓ Saved clustered dataset: beige_customer_clusters.csv")

# Save cluster profiles to CSV
profiles_df = pd.DataFrame(cluster_profiles)
profiles_df.to_csv('/Users/queenceline/Downloads/Beige AI/cluster_profiles.csv', index=False)
print(f"✓ Saved cluster profiles: cluster_profiles.csv")

# Save association rules to CSV
if len(rules_sorted) > 0:
    rules_export = rules_sorted.copy()
    rules_export['antecedents'] = rules_export['antecedents'].apply(lambda x: ', '.join(list(x)))
    rules_export['consequents'] = rules_export['consequents'].apply(lambda x: ', '.join(list(x)))
    rules_export.to_csv('/Users/queenceline/Downloads/Beige AI/association_rules.csv', index=False)
    print(f"✓ Saved association rules: association_rules.csv ({len(rules_export)} rules)")

# ============================================================================
# FINAL SUMMARY
# ============================================================================

print("\n" + "="*70)
print("PHASE 2 COMPLETE!")
print("="*70)

print("\n--- Summary Statistics ---")
print(f"Total Customers: {len(df):,}")
print(f"Number of Clusters: {optimal_k}")
print(f"PCA Variance Explained: {pca.explained_variance_ratio_.sum():.1%}")
print(f"Association Rules Generated: {len(rules_sorted)}")

print("\n--- Output Files ---")
print(f"  1. beige_customer_clusters.csv ({len(df_with_clusters)} rows)")
print(f"  2. cluster_profiles.csv ({len(profiles_df)} clusters)")
if len(rules_sorted) > 0:
    print(f"  3. association_rules.csv ({len(rules_export)} rules)")
print(f"  4. phase2_analytics_visualizations.png")

print("\n--- Next Steps (Phase 3) ---")
print("  1. Train Random Forest classifier on cake_category")
print("  2. Feature importance analysis")
print("  3. Cross-validation and model evaluation")
print("  4. Build hybrid recommendation engine")
print("  5. Integrate Gemini API for natural language explanations")

print("\n" + "="*70 + "\n")
