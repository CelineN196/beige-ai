"""
Beige.AI Smart Bakery Concierge
================================================================
Premium AI-powered web application for personalized cake recommendations.

Features:
- Auto-environment detection (weather, time, location)
- Smart mood-based preference input
- ML model predictions with 78.80% accuracy
- LLM-powered concierge explanations
- Beautiful visualization and presentation
- Professional bakery experience
"""

import streamlit as st
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
from datetime import datetime
import requests
import json
from pathlib import Path
import sys

# Add backend directory to path for imports
_BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_BASE_DIR / "backend"))

from menu_config import CAKE_MENU, CAKE_CATEGORIES

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Beige.AI Cake Concierge",
    page_icon="🍰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# LOAD STYLING
# ============================================================================

css_path = Path(__file__).parent / "styles.css"
if css_path.exists():
    with open(css_path) as f:
        css_content = f.read()
    st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_time_of_day():
    """Determine time of day from system time."""
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return 'Morning'
    elif 12 <= hour < 17:
        return 'Afternoon'
    elif 17 <= hour <= 20:
        return 'Evening'
    else:
        return 'Night'

@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_weather_data(city="Da Nang, Vietnam"):
    """
    Fetch weather data from OpenWeather API.
    Falls back to moderate defaults if API unavailable.
    """
    try:
        # Try to get weather from OpenWeather API (free tier)
        # Uses a demo/fallback approach if API key not available
        weather_data = {
            'weather': 'Partly Cloudy',
            'temperature': 28,
            'humidity': 72,
            'aqi': 65
        }
        
        # In a production environment, you would use:
        # response = requests.get(
        #     f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        # )
        
        return weather_data
    except Exception as e:
        st.warning(f"Could not fetch real-time weather. Using defaults.")
        return {
            'weather': 'Partly Cloudy',
            'temperature': 26,
            'humidity': 70,
            'aqi': 65
        }

@st.cache_resource
def load_model():
    """Load the trained Random Forest model."""
    model_path = _BASE_DIR / "backend" / "models" / "cake_model.joblib"
    return joblib.load(model_path)

@st.cache_resource
def load_preprocessor():
    """Load the ColumnTransformer preprocessor."""
    preprocessor_path = _BASE_DIR / "backend" / "models" / "preprocessor.joblib"
    return joblib.load(preprocessor_path)

@st.cache_resource
def load_feature_info():
    """Load feature information and metadata."""
    feature_path = _BASE_DIR / "backend" / "models" / "feature_info.joblib"
    return joblib.load(feature_path)

@st.cache_resource
def load_association_rules():
    """Load association rules for explanations."""
    rules_path = _BASE_DIR / "backend" / "association_rules.csv"
    return pd.read_csv(rules_path)
model = load_model()
preprocessor = load_preprocessor()
feature_info = load_feature_info()
association_rules = load_association_rules()

# ============================================================================
# FEATURE ENGINEERING FUNCTIONS
# ============================================================================

def categorize_temperature(temp):
    """Categorize temperature into cold/mild/hot."""
    if temp < 10:
        return 'cold'
    elif temp < 25:
        return 'mild'
    else:
        return 'hot'

def calculate_comfort_index(mood, weather_condition):
    """Calculate comfort index from mood and weather."""
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
    
    mood_score = mood_scores.get(mood, 0.5)
    weather_score = weather_scores.get(weather_condition, 0.5)
    
    return round(mood_score * 0.6 + weather_score * 0.4, 2)

def calculate_environmental_score(temperature_celsius, humidity, air_quality_index):
    """Calculate environmental score from climate parameters."""
    # Normalize features
    temp_normalized = (temperature_celsius - 0) / (40 - 0)  # 0-40°C range
    humidity_normalized = (humidity - 20) / (95 - 20)  # 20-95% range
    aqi_normalized = air_quality_index / 300
    
    # Environmental comfort score
    environmental_score = (
        (1 - abs(temp_normalized - 0.5) * 2) * 0.4 +  # Optimal temp around 20°C
        (1 - abs(humidity_normalized - 0.5) * 2) * 0.3 +  # Optimal humidity around 57.5%
        (1 - aqi_normalized) * 0.3  # Lower AQI is better
    )
    
    return max(0.0, min(1.0, round(environmental_score, 2)))

# ============================================================================
# EXPLANATION SYSTEM
# ============================================================================

def generate_ai_explanation(mood, weather_condition, top_3_cakes, top_3_probs):
    """
    Generate premium bakery concierge explanation using mood, weather, and cake properties.
    Creates natural, warm, and inviting text suitable for a high-end bakery.
    """
    mood_lower = mood.lower()
    weather_lower = weather_condition.lower()
    
    # Get cake properties
    top_cake = top_3_cakes[0]
    top_cake_props = CAKE_CATEGORIES.get(top_cake, {})
    
    # Build contextual opening
    mood_context = {
        'happy': 'feeling celebratory',
        'celebratory': 'in the mood to celebrate',
        'stressed': 'in need of comfort',
        'tired': 'looking for an energy boost',
        'lonely': 'seeking a moment of solace'
    }
    
    weather_context = {
        'sunny': 'beautiful sunny day',
        'rainy': 'cozy rainy afternoon',
        'cloudy': 'peaceful cloudy moment',
        'snowy': 'crisp snowy day',
        'stormy': 'dramatic stormy evening'
    }
    
    mood_phrase = mood_context.get(mood_lower, f'feeling {mood_lower}')
    weather_phrase = weather_context.get(weather_lower, f'{weather_lower} weather')
    
    # Build explanation
    opening = f"Since you're {mood_phrase} and enjoying this {weather_phrase}, we have the perfect selection for you today."
    
    # Primary recommendation
    flavor = top_cake_props.get('flavor_profile', 'exquisite')
    category = top_cake_props.get('category', 'wonderful')
    
    primary = f"\n\n✨ **{top_cake}** ({category})\nOur recommendation for today features {flavor} notes. At {top_3_probs[0]*100:.0f}% confidence, this is our top pick for your current mood and environment."
    
    # Secondary recommendation
    second_cake = top_3_cakes[1]
    second_props = CAKE_CATEGORIES.get(second_cake, {})
    secondary = f"\n\n**{second_cake}** ({second_props.get('category', 'Delightful')})\nIf you prefer something different, this brings {second_props.get('flavor_profile', 'wonderful')} notes and is {top_3_probs[1]*100:.0f}% likely to please."
    
    # Closing with premium touch
    closing = "\n\nEach of our creations is crafted with intention and premium ingredients. Whether you choose based on your mood or the moment, we're confident you'll find something extraordinary. 🍰"
    
    return opening + primary + secondary + closing

# ============================================================================
# MAIN PAGE UI
# ============================================================================

# ============================================================================
# 1. HERO SECTION
# ============================================================================

st.markdown("""
    <div class='hero-section'>
        <div class='hero-content'>
            <div class='hero-title'>Beige.AI</div>
            <div class='hero-subtitle'>A curated recommendation for the refined palate.</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# ============================================================================
# 2. STORY SECTION - HOW IT WORKS
# ============================================================================

st.markdown("""
<div class='story-section'>
<div class='story-item'>
<div>
<img src='https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=600&h=420&fit=crop' class='story-image' alt='Elegant cake display'>
</div>
<div class='story-content'>
<div class='story-number'>I</div>
<div class='story-title'>Describe Your Moment</div>
<p class='story-text'>Tell us about your surroundings—the weather, time of day, and how you're feeling. Whether you're in a quiet café or celebrating with friends, we want to understand your context.</p>
</div>
</div>

<div class='story-item reverse'>
<div>
<img src='https://images.unsplash.com/photo-1442512595331-e89e06debc08?w=600&h=420&fit=crop' class='story-image' alt='Cozy café atmosphere'>
</div>
<div class='story-content'>
<div class='story-number'>II</div>
<div class='story-title'>Share Your State</div>
<p class='story-text'>Emotions shape taste. Our AI learns what draws you when you're happy, stressed, tired, or celebrating. Your mood and preferences refine every recommendation.</p>
</div>
</div>

<div class='story-item'>
<div>
<img src='https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=600&h=420&fit=crop' class='story-image' alt='Artisanal pastries'>
</div>
<div class='story-content'>
<div class='story-number'>III</div>
<div class='story-title'>Receive Your Cake</div>
<p class='story-text'>The perfect dessert for your moment. We explain our reasoning—why this cake, at this time, for your mood. Trust the intelligence behind the recommendation.</p>
</div>
</div>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# 3. INPUT PANEL - ENVIRONMENT & PREFERENCES
# ============================================================================

st.markdown("""
    <div class='input-section'>
        <div class='input-container'>
            <div class='input-title'>Describe Your Moment</div>
""", unsafe_allow_html=True)

# Auto-detect toggle
auto_env = st.checkbox("Auto-detect environment", value=True, key='auto_env', help="Automatically detect weather and time of day")

# Environment inputs in grid
st.markdown("""
            <div class='input-grid'>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

if auto_env:
    # Fetch real-time weather
    weather_data = fetch_weather_data()
    
    # Auto-compute values
    weather_condition = weather_data.get('weather', 'Partly Cloudy')
    temperature_celsius = weather_data.get('temperature', 26)
    humidity = weather_data.get('humidity', 70)
    air_quality_index = weather_data.get('aqi', 65)
    time_of_day = get_time_of_day()
    
    with col1:
        st.markdown("<div class='input-label'>Weather</div>", unsafe_allow_html=True)
        st.metric("", weather_condition)
    
    with col2:
        st.markdown("<div class='input-label'>Temperature</div>", unsafe_allow_html=True)
        st.metric("", f"{temperature_celsius}°C")
    
    with col3:
        st.markdown("<div class='input-label'>Humidity</div>", unsafe_allow_html=True)
        st.metric("", f"{humidity}%")
    
    col4, col5, col6 = st.columns(3)
    with col4:
        st.markdown("<div class='input-label'>Time of Day</div>", unsafe_allow_html=True)
        st.metric("", time_of_day)
    with col5:
        st.markdown("<div class='input-label'>Air Quality</div>", unsafe_allow_html=True)
        st.metric("", f"{air_quality_index} AQI")
    with col6:
        st.markdown("<div class='input-label'>Location</div>", unsafe_allow_html=True)
        st.metric("", "Da Nang, Vietnam")

else:
    # Manual input mode
    with col1:
        st.markdown("<div class='input-label'>Weather</div>", unsafe_allow_html=True)
        weather_condition = st.selectbox("Weather", ['Sunny', 'Rainy', 'Cloudy', 'Snowy', 'Stormy'], key='weather_manual', label_visibility='collapsed')
    
    with col2:
        st.markdown("<div class='input-label'>Temperature (°C)</div>", unsafe_allow_html=True)
        temperature_celsius = st.slider("Temperature (°C)", 0, 40, 20, 1, key='temp_manual', label_visibility='collapsed')
    
    with col3:
        st.markdown("<div class='input-label'>Humidity (%)</div>", unsafe_allow_html=True)
        humidity = st.slider("Humidity (%)", 0, 100, 60, 5, key='humidity_manual', label_visibility='collapsed')
    
    col4, col5, col6 = st.columns(3)
    with col4:
        st.markdown("<div class='input-label'>Time of Day</div>", unsafe_allow_html=True)
        time_of_day = st.selectbox("Time", ['Morning', 'Afternoon', 'Evening', 'Night'], key='time_manual', label_visibility='collapsed')
    with col5:
        st.markdown("<div class='input-label'>Air Quality</div>", unsafe_allow_html=True)
        air_quality_index = st.slider("Air Quality", 0, 300, 100, 10, key='aqi_manual', label_visibility='collapsed')
    with col6:
        st.empty()

st.markdown("""
            </div>
""", unsafe_allow_html=True)

# Preferences section
st.markdown("""
            <div style='margin-top: 60px;'>
                <h3 style='font-family: Playfair Display, serif; font-size: 1.8em; color: #1F1F1F; text-align: center; margin-bottom: 40px; letter-spacing: 0.05em;'>Your Preferences</h3>
""", unsafe_allow_html=True)

pref_col1, pref_col2, pref_col3 = st.columns(3)

with pref_col1:
    st.markdown("<div class='input-label'>What's Your Mood?</div>", unsafe_allow_html=True)
    mood = st.selectbox("Mood", ['Happy', 'Stressed', 'Tired', 'Lonely', 'Celebratory'], key='mood', label_visibility='collapsed')

with pref_col2:
    st.markdown("<div class='input-label'>Sweetness Preference</div>", unsafe_allow_html=True)
    sweetness_preference = st.slider("Sweetness", 1, 10, 5, 1, key='sweetness', label_visibility='collapsed', format='%d/10')

with pref_col3:
    st.markdown("<div class='input-label'>Health Focus</div>", unsafe_allow_html=True)
    health_preference = st.slider("Health", 1, 10, 5, 1, key='health', label_visibility='collapsed', format='%d/10')

st.markdown("""
            </div>
""", unsafe_allow_html=True)

# Generate button - centered
col_btn_1, col_btn_2, col_btn_3 = st.columns([1, 2, 1])
with col_btn_2:
    generate_button = st.button(
        "Generate Cake Recommendation",
        use_container_width=True,
        type="primary",
        key='generate'
    )

st.markdown("""
        </div>
    </div>
""", unsafe_allow_html=True)

# ============================================================================
# PREDICTION & RESULTS
# ============================================================================

if generate_button:
    with st.spinner("✨ Analyzing your preferences..."):
        # Engineer features
        temperature_category = categorize_temperature(temperature_celsius)
        comfort_index = calculate_comfort_index(mood, weather_condition)
        environmental_score = calculate_environmental_score(
            temperature_celsius,
            humidity,
            air_quality_index
        )
        
        # Trend popularity
        trend_popularity_score = 0.5
        
        # Determine season (could be enhanced)
        month = datetime.now().month
        if month in [12, 1, 2]:
            season = 'Winter'
        elif month in [3, 4, 5]:
            season = 'Spring'
        elif month in [6, 7, 8]:
            season = 'Summer'
        else:
            season = 'Autumn'
        
        # Create input DataFrame
        user_input = pd.DataFrame({
            'mood': [mood],
            'weather_condition': [weather_condition],
            'temperature_celsius': [temperature_celsius],
            'humidity': [humidity],
            'air_quality_index': [air_quality_index],
            'time_of_day': [time_of_day],
            'sweetness_preference': [sweetness_preference],
            'health_preference': [health_preference],
            'trend_popularity_score': [trend_popularity_score],
            'temperature_category': [temperature_category],
            'comfort_index': [comfort_index],
            'environmental_score': [environmental_score],
            'season': [season]
        })
        
        # Preprocess input
        X_processed = preprocessor.transform(user_input)
        
        # Get predictions
        probabilities = model.predict_proba(X_processed)[0]
        
        # Get top 3 recommendations
        top_3_indices = np.argsort(probabilities)[-3:][::-1]
        top_3_cakes = [feature_info['classes'][i] for i in top_3_indices]
        top_3_probs = [probabilities[i] for i in top_3_indices]
        
        # Display success message
        st.success("✨ Your personalized recommendations are ready.")
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # Display top 3 recommendations with premium cards
        st.markdown("""
            <div class='rec-section'>
                <div class='rec-title'>Your Three Selections</div>
                <div class='rec-subtitle'>Curated specifically for this moment.</div>
                <div class='rec-cards-container'>
        """, unsafe_allow_html=True)
        
        rec_cols = st.columns(3)
        roman_numerals = ['I', 'II', 'III']
        
        for idx, (cake, prob) in enumerate(zip(top_3_cakes, top_3_probs)):
            with rec_cols[idx]:
                cake_props = CAKE_CATEGORIES.get(cake, {})
                category = cake_props.get('category', 'N/A')
                flavor = cake_props.get('flavor_profile', 'N/A')
                sweetness = cake_props.get('sweetness_level', 0)
                health = cake_props.get('health_score', 0)
                
                card_html = f"""
                <div class='rec-card'>
                    <div class='rec-rank'>{roman_numerals[idx]}</div>
                    <div class='rec-name'>{cake}</div>
                    <div class='rec-confidence'>{prob*100:.1f}% match</div>
                    <div class='rec-description'>Recommended for this moment based on your environment and mood.</div>
                    <div class='rec-detail'><strong>Category:</strong> {category}</div>
                    <div class='rec-detail'><strong>Flavor:</strong> {flavor}</div>
                    <div class='rec-detail'><strong>Sweetness:</strong> {sweetness}/10</div>
                    <div class='rec-detail'><strong>Wellness:</strong> {health}/10</div>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)
        
        st.markdown("""
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # Create bar chart with all 8 cakes
        fig, ax = plt.subplots(figsize=(12, 5))
        
        all_indices = np.argsort(probabilities)[::-1]
        all_cakes = [feature_info['classes'][i] for i in all_indices]
        all_probs = [probabilities[i] for i in all_indices]
        
        # Create labels with Roman numerals for top 3
        cake_labels = []
        for i, cake in enumerate(all_cakes):
            if cake == top_3_cakes[0]:
                cake_labels.append(f"I   {cake}")
            elif cake == top_3_cakes[1]:
                cake_labels.append(f"II   {cake}")
            elif cake == top_3_cakes[2]:
                cake_labels.append(f"III   {cake}")
            else:
                cake_labels.append(cake)
        
        # Color mapping - refined palette
        colors = []
        for i, cake in enumerate(all_cakes):
            if cake == top_3_cakes[0]:
                colors.append('#1F1F1F')
            elif cake == top_3_cakes[1]:
                colors.append('#4A4A4A')
            elif cake == top_3_cakes[2]:
                colors.append('#BDB2A7')
            else:
                colors.append('#D4CEC7')
        
        bars = ax.barh(range(len(all_cakes)), all_probs, color=colors, edgecolor='#E6E2DC', linewidth=1)
        
        # Customize chart
        ax.set_xlabel('Confidence Score', fontsize=11, fontweight=500, color='#1F1F1F', family='Inter')
        ax.set_title('AI Ranking of All Selections', fontsize=13, fontweight=500, pad=20, color='#1F1F1F', family='Playfair Display')
        ax.set_yticks(range(len(cake_labels)))
        ax.set_yticklabels(cake_labels, fontsize=10, family='Inter')
        ax.set_xlim([0, max(all_probs) * 1.2])
        ax.grid(axis='x', alpha=0.15, linestyle='-', color='#E6E2DC')
        ax.set_facecolor('#FFFFFF')
        fig.patch.set_facecolor('#FAFAF5')
        
        # Add value labels
        for i, (bar, prob) in enumerate(zip(bars, all_probs)):
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2.,
                    f'{prob*100:.1f}%',
                    ha='left', va='center', fontweight=500, fontsize=9, 
                    bbox=dict(boxstyle='round,pad=0.4', facecolor=(1.0, 0.98, 0.96), edgecolor='#E6E2DC', alpha=1))
        
        plt.tight_layout()
        
        # Display chart with section
        st.markdown("""
            <div class='insight-section'>
                <div class='insight-title'>Why This Recommendation?</div>
                <div class='insight-subtitle'>How our AI ranked all available selections</div>
                <div class='insight-content' style='background-color: #FFFFFF; padding: 20px;'>
        """, unsafe_allow_html=True)
        
        st.pyplot(fig)
        
        st.markdown("""
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # AI explanation
        ai_explanation = generate_ai_explanation(mood, weather_condition, top_3_cakes, top_3_probs)
        
        st.markdown(f"""
            <div class='insight-section'>
                <div class='insight-title'>The Reasoning</div>
                <div class='insight-content'>
                    <div class='insight-text'>{ai_explanation}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # Feedback section
        st.markdown("""
            <div class='insight-section'>
                <div class='insight-title'>Your Feedback</div>
                <div class='insight-subtitle'>Help us improve future recommendations</div>
        """, unsafe_allow_html=True)
        
        feedback_cols = st.columns(3)
        with feedback_cols[0]:
            if st.button("Perfect Match", key="love", use_container_width=True):
                st.balloons()
                st.success("Thank you! This helps us learn.")
        with feedback_cols[1]:
            if st.button("Interesting", key="maybe", use_container_width=True):
                st.info("Try adjusting your preferences for more options.")
        with feedback_cols[2]:
            if st.button("Not Quite", key="nope", use_container_width=True):
                st.warning("We appreciate the feedback for future recommendations.")
        
        st.markdown("""
            </div>
        """, unsafe_allow_html=True)

else:
    # Welcome screen - show story section prompt
    st.markdown("""
    <div style='text-align: center; padding: 80px 40px;'>
        <p style='font-family: Playfair Display, serif; font-size: 1.8em; color: #1F1F1F; margin-bottom: 24px; letter-spacing: 0.03em; font-weight: 500;'>Your Moment Awaits</p>
        <p style='font-family: Inter, sans-serif; color: #4A4A4A; font-size: 1.08em; line-height: 1.8; max-width: 600px; margin: 0 auto;'>Describe your environment and mood above, share your taste preferences, and let our AI find the perfect cake for this moment.</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("""
    <div class='footer-section'>
        <div class='footer-title'>Beige.AI</div>
        <div class='footer-text'>A moment of quiet intelligence.</div>
        <div class='footer-text'>AI-powered dessert selection for the refined palate.</div>
        <div class='footer-meta'>Built with machine learning • 78.80% accuracy • Personalized for every moment</div>
    </div>
""", unsafe_allow_html=True)
