"""
Beige.AI Phase 1: Synthetic Dataset Generation
================================================================
This script generates a comprehensive synthetic dataset of 50,000 rows 
that simulates realistic cake purchasing behavior influenced by emotional 
state, weather conditions, environmental factors, and personal preferences.

The dataset applies probabilistic weighting logic based on domain 
knowledge rules to create non-random, behavioral cake selections.

Author: Senior Data Scientist
Date: March 2026
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
from menu_config import CAKE_MENU

warnings.filterwarnings('ignore')

# Set random seed for reproducibility
np.random.seed(42)

print("="*70)
print("BEIGE.AI SYNTHETIC DATA GENERATION")
print("="*70)

# ============================================================================
# SECTION 1: DATA GENERATION
# ============================================================================

print("\n[1/5] Generating base features...")

n_rows = 50000

# Define feature distributions
moods = ['Happy', 'Stressed', 'Tired', 'Lonely', 'Celebratory']
weather_conditions = ['Sunny', 'Rainy', 'Cloudy', 'Snowy', 'Stormy']
seasons = ['Spring', 'Summer', 'Autumn', 'Winter']
times_of_day = ['Morning', 'Afternoon', 'Evening', 'Night']

# Import cake menu from centralized configuration
cake_categories_menu = CAKE_MENU

# Generate DataFrame with base features
df = pd.DataFrame({
    'mood': np.random.choice(moods, n_rows, p=[0.25, 0.20, 0.20, 0.15, 0.20]),
    'weather_condition': np.random.choice(weather_conditions, n_rows, p=[0.28, 0.24, 0.24, 0.16, 0.08]),
    'temperature_celsius': np.random.uniform(-10, 40, n_rows),
    'humidity': np.random.uniform(20, 95, n_rows),
    'season': np.random.choice(seasons, n_rows, p=[0.25, 0.25, 0.25, 0.25]),
    'air_quality_index': np.random.uniform(0, 300, n_rows),
    'time_of_day': np.random.choice(times_of_day, n_rows, p=[0.25, 0.30, 0.25, 0.20]),
    'sweetness_preference': np.random.randint(1, 11, n_rows),
    'health_preference': np.random.randint(1, 11, n_rows),
    'trend_popularity_score': np.random.uniform(0.0, 1.0, n_rows)
})

print(f"✓ Generated {n_rows} rows with 10 base features")

# ============================================================================
# SECTION 2: RULE-BASED TARGET VARIABLE (cake_category)
# ============================================================================

print("\n[2/5] Creating rule-based cake category labels...")

def assign_cake_category(row):
    """
    Rule-based labeling function for cake category using probabilistic weighting.
    
    Applies domain knowledge rules that simulate realistic bakery buying behavior:
    1. Caffeine Morning Rule
    2. Stormy Comfort Rule
    3. Summer Refreshment Rule
    4. Health Conscious Filter
    5. Bakery Specialty Rule (Bread Behavior)
    6. Evening Indulgence Rule
    """
    # Initialize scores for each cake category
    scores = {cake: 1.0 for cake in cake_categories_menu}
    
    # RULE 1: Caffeine Morning Rule
    # If time_of_day = Morning OR mood = Tired
    # → Increase Matcha Zen Cake, Café Tiramisu by +60%
    if row['time_of_day'] == 'Morning' or row['mood'] == 'Tired':
        scores['Matcha Zen Cake'] *= 1.6
        scores['Café Tiramisu'] *= 1.6
    
    # RULE 2: Stormy Comfort Rule
    # If weather is Rainy, Stormy, or Snowy OR mood is Stressed or Lonely
    # → Increase Dark Chocolate Sea Salt Cake by +70%
    if row['weather_condition'] in ['Rainy', 'Stormy', 'Snowy'] or \
       row['mood'] in ['Stressed', 'Lonely']:
        scores['Dark Chocolate Sea Salt Cake'] *= 1.7
    
    # RULE 3: Summer Refreshment Rule
    # If temperature_celsius > 28 AND weather_condition = Sunny
    # → Increase Citrus Cloud Cake, Berry Garden Cake by +80%
    if row['temperature_celsius'] > 28 and row['weather_condition'] == 'Sunny':
        scores['Citrus Cloud Cake'] *= 1.8
        scores['Berry Garden Cake'] *= 1.8
    
    # RULE 4: Health Conscious Filter
    # If health_preference > 7
    # → Reduce Silk Cheesecake, Dark Chocolate by -30%
    # → Increase Earthy Wellness Cake, Matcha Zen Cake by +40%
    if row['health_preference'] > 7:
        scores['Silk Cheesecake'] *= 0.7
        scores['Dark Chocolate Sea Salt Cake'] *= 0.7
        scores['Earthy Wellness Cake'] *= 1.4
        scores['Matcha Zen Cake'] *= 1.4
    
    # RULE 5: Bakery Specialty Rule (Bread Behavior)
    # If time_of_day = Morning or Afternoon AND sweetness_preference ≤ 5
    # → Increase Korean Sesame Mini Bread by +100%
    if row['time_of_day'] in ['Morning', 'Afternoon'] and \
       row['sweetness_preference'] <= 5:
        scores['Korean Sesame Mini Bread'] *= 2.0
    
    # RULE 6: Evening Indulgence Rule
    # If time_of_day = Evening OR Night
    # → Increase Dark Chocolate, Silk Cheesecake, Café Tiramisu by +50%
    if row['time_of_day'] in ['Evening', 'Night']:
        scores['Dark Chocolate Sea Salt Cake'] *= 1.5
        scores['Silk Cheesecake'] *= 1.5
        scores['Café Tiramisu'] *= 1.5
    
    # Add small random noise to prevent deterministic patterns
    for cake in scores:
        scores[cake] *= np.random.uniform(0.85, 1.15)
    
    # Select cake with highest weighted score
    selected_cake = max(scores, key=scores.get)
    
    # Store the modified sweetness preference if evening/night rule applied
    # (This will be stored separately)
    return selected_cake

# Apply rule-based labeling
df['cake_category'] = df.apply(assign_cake_category, axis=1)

# Apply Evening Indulgence Rule: increase sweetness_preference by +2 (capped at 10) for evening/night
evening_night_mask = df['time_of_day'].isin(['Evening', 'Night'])
df.loc[evening_night_mask, 'sweetness_preference'] = (
    df.loc[evening_night_mask, 'sweetness_preference'] + 2
).clip(upper=10)

print("✓ Applied 6 domain knowledge rules with probabilistic weighting")
print(f"  Cake category distribution:\n{df['cake_category'].value_counts()}\n")

# ============================================================================
# SECTION 3: FEATURE ENGINEERING
# ============================================================================

print("[3/5] Engineering derived features...")

# Feature 1: temperature_category
def categorize_temperature(temp):
    if temp < 10:
        return 'cold'
    elif temp < 25:
        return 'mild'
    else:
        return 'hot'

df['temperature_category'] = df['temperature_celsius'].apply(categorize_temperature)

# Feature 2: comfort_index (combination of mood + weather)
mood_scores = {
    'Happy': 0.9,
    'Celebratory': 0.95,
    'Tired': 0.5,
    'Stressed': 0.3,
    'Lonely': 0.4
}

weather_scores = {
    'Sunny': 0.9,
    'Cloudy': 0.6,
    'Rainy': 0.4,
    'Snowy': 0.3,
    'Stormy': 0.2
}

df['mood_score'] = df['mood'].map(mood_scores)
df['weather_score'] = df['weather_condition'].map(weather_scores)
df['comfort_index'] = (df['mood_score'] * 0.6 + df['weather_score'] * 0.4).round(2)

# Feature 3: environmental_score (weighted combination of AQI, humidity, temperature)
# Normalize features first
temp_normalized = (df['temperature_celsius'] - df['temperature_celsius'].min()) / (df['temperature_celsius'].max() - df['temperature_celsius'].min())
humidity_normalized = (df['humidity'] - 20) / (95 - 20)  # Normalize to 20-95 range
aqi_normalized = df['air_quality_index'] / 300

# In-door comfort: prefer moderate temp, moderate humidity, low AQI
df['environmental_score'] = (
    (1 - abs(temp_normalized - 0.5) * 2) * 0.4 +  # Optimal temp around 25°C
    (1 - abs(humidity_normalized - 0.5) * 2) * 0.3 +  # Optimal humidity around 57.5%
    (1 - aqi_normalized) * 0.3  # Lower AQI is better
).round(2)

print("✓ Created 3 engineered features:")
print("  - temperature_category")
print("  - comfort_index")
print("  - environmental_score")

# ============================================================================
# SECTION 4: EXPLORATORY DATA ANALYSIS (EDA)
# ============================================================================

print("\n[4/5] Generating visualizations...")

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (16, 12)

fig = plt.figure(figsize=(16, 12))

# Visualization 1: Cake Category Distribution
ax1 = plt.subplot(2, 3, 1)
cake_counts = df['cake_category'].value_counts()
colors = plt.cm.Set3(np.linspace(0, 1, len(cake_counts)))
ax1.barh(range(len(cake_counts)), cake_counts.values, color=colors)
ax1.set_yticks(range(len(cake_counts)))
ax1.set_yticklabels(cake_counts.index)
ax1.set_xlabel('Count')
ax1.set_title('Distribution of Cake Categories', fontsize=12, fontweight='bold')
ax1.grid(axis='x', alpha=0.3)

# Visualization 2: Correlation Heatmap
ax2 = plt.subplot(2, 3, 2)
numerical_cols = ['temperature_celsius', 'humidity', 'air_quality_index', 
                  'sweetness_preference', 'health_preference', 
                  'trend_popularity_score', 'comfort_index', 'environmental_score']
corr_matrix = df[numerical_cols].corr()
sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', center=0, 
            square=True, ax=ax2, cbar_kws={'shrink': 0.8}, vmin=-1, vmax=1)
ax2.set_title('Correlation Heatmap (Numerical Features)', fontsize=12, fontweight='bold')
plt.setp(ax2.get_xticklabels(), rotation=45, ha='right', fontsize=8)
plt.setp(ax2.get_yticklabels(), fontsize=8)

# Visualization 3: Mood vs Cake Category
ax3 = plt.subplot(2, 3, 3)
mood_cake = pd.crosstab(df['mood'], df['cake_category'])
mood_cake.T.plot(kind='bar', ax=ax3, width=0.8, 
                 color=plt.cm.Set2(np.linspace(0, 1, len(mood_cake.columns))))
ax3.set_xlabel('Cake Category')
ax3.set_ylabel('Count')
ax3.set_title('Mood vs Cake Category Distribution', fontsize=12, fontweight='bold')
ax3.legend(title='Mood', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
plt.setp(ax3.get_xticklabels(), rotation=45, ha='right', fontsize=9)

# Visualization 4: Temperature vs Cake Category
ax4 = plt.subplot(2, 3, 4)
for cake in df['cake_category'].unique():
    data = df[df['cake_category'] == cake]['temperature_celsius']
    ax4.scatter([cake]*len(data), data, alpha=0.3, s=10)
ax4.set_xticklabels(df['cake_category'].unique(), rotation=45, ha='right', fontsize=9)
ax4.set_ylabel('Temperature (°C)')
ax4.set_title('Temperature Distribution by Cake Category', fontsize=12, fontweight='bold')
ax4.grid(axis='y', alpha=0.3)

# Visualization 5: Comfort Index Distribution
ax5 = plt.subplot(2, 3, 5)
ax5.hist(df['comfort_index'], bins=40, color='skyblue', edgecolor='black', alpha=0.7)
ax5.set_xlabel('Comfort Index')
ax5.set_ylabel('Frequency')
ax5.set_title('Distribution of Comfort Index', fontsize=12, fontweight='bold')
ax5.grid(axis='y', alpha=0.3)

# Visualization 6: Environmental Score vs Health Preference
ax6 = plt.subplot(2, 3, 6)
scatter = ax6.scatter(df['environmental_score'], df['health_preference'], 
                     c=df['sweetness_preference'], cmap='viridis', alpha=0.5, s=20)
ax6.set_xlabel('Environmental Score')
ax6.set_ylabel('Health Preference')
ax6.set_title('Environmental Score vs Health Preference', fontsize=12, fontweight='bold')
cbar = plt.colorbar(scatter, ax=ax6)
cbar.set_label('Sweetness Preference')

plt.tight_layout()
plt.savefig('/Users/queenceline/Downloads/Beige AI/eda_analysis.png', dpi=300, bbox_inches='tight')
print("✓ Saved visualization: eda_analysis.png")
plt.close()

# ============================================================================
# SECTION 5: DATA SUMMARY AND EXPORT
# ============================================================================

print("\n[5/5] Finalizing dataset...")

# Display dataset info
print("\n" + "="*70)
print("DATASET INFORMATION")
print("="*70)
print(f"\nDataset Shape: {df.shape}")

print("\n--- Data Info ---")
print(df.info())

print("\n--- First 10 Rows ---")
print(df.head(10).to_string())

print("\n--- Statistical Summary ---")
print(df.describe().to_string())

print("\n--- Feature Engineering Results ---")
print(f"Temperature Categories: {df['temperature_category'].value_counts().to_dict()}")
print(f"\nComfort Index Stats:")
print(f"  Mean: {df['comfort_index'].mean():.3f}")
print(f"  Std:  {df['comfort_index'].std():.3f}")
print(f"  Min:  {df['comfort_index'].min():.3f}")
print(f"  Max:  {df['comfort_index'].max():.3f}")
print(f"\nEnvironmental Score Stats:")
print(f"  Mean: {df['environmental_score'].mean():.3f}")
print(f"  Std:  {df['environmental_score'].std():.3f}")
print(f"  Min:  {df['environmental_score'].min():.3f}")
print(f"  Max:  {df['environmental_score'].max():.3f}")

# Remove temporary scoring columns and keep only necessary features
df_final = df.drop(columns=['mood_score', 'weather_score'])

# Save to CSV
output_path = '/Users/queenceline/Downloads/Beige AI/beige_ai_cake_dataset_v2.csv'
df_final.to_csv(output_path, index=False)

print("\n" + "="*70)
print(f"✓ DATASET SUCCESSFULLY SAVED")
print("="*70)
print(f"Location: {output_path}")
print(f"Size: {df_final.shape[0]} rows × {df_final.shape[1]} columns")
print(f"File Size: {np.round(df_final.memory_usage(deep=True).sum() / 1024**2, 2)} MB")

print("\n--- Final Columns ---")
for i, col in enumerate(df_final.columns, 1):
    print(f"  {i:2d}. {col}")

print("\n" + "="*70)
print("PHASE 1 COMPLETE!")
print("="*70)
print(f"\nDataset Summary:")
print(f"  • 50,000 rows with realistic cake purchasing behavior")
print(f"  • 6 domain knowledge rules applied probabilistically")
print(f"  • Balanced cake category distribution")
print(f"  • Feature-engineered attributes for ML modeling")
print(f"\nNext Steps (Phase 2):")
print(f"  1. K-Means Clustering for customer segmentation")
print(f"  2. Random Forest Classifier for cake category prediction")
print(f"  3. Association Rule Mining for behavior discovery")
print(f"  4. Build hybrid recommendation engine")
print(f"  5. Gemini API integration for explanations")
print("="*70 + "\n")
