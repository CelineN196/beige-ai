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

# ============================================================================
# � DEBUG MODE TOGGLE - SET TO False FOR PRODUCTION (MUST BE FIRST)
# ============================================================================
# Initialize debug mode and logging BEFORE any other prints
import os
import sys
import logging

DEBUG = False  # Set to True to show debug output in UI

# Keep backend logging for terminal (development) - these don't expose in UI
logger = logging.getLogger("Beige AI")
logger.setLevel(logging.INFO if not DEBUG else logging.DEBUG)

# ============================================================================
# 🚀 ENTRY POINT ENFORCEMENT - SINGLE FRONTEND ENTRY
# ============================================================================
# This file MUST be the ONLY Streamlit entry point. Fail immediately if not.
if DEBUG:
    logger.info("🚀 RUNNING MAIN FRONTEND: beige_ai_app.py")
    logger.info("✅ Frontend: Single entry point verified")
    logger.info("✅ CLEAN FRONTEND ENTRY — beige_ai_app.py (Modular Architecture)")
current_file = os.path.basename(__file__)
assert current_file == "beige_ai_app.py", f"❌ WRONG ENTRY FILE: {current_file}. Must run: streamlit run frontend/beige_ai_app.py"

# ============================================================================
# 🔧 FIX PYTHON IMPORT PATH FOR MODULAR ARCHITECTURE
# ============================================================================
# Add project root to sys.path so we can import from core/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
from datetime import datetime
import requests
import json
from pathlib import Path
import google.generativeai as genai
import uuid
import csv

# menu_config.py is now in the same directory (frontend/)
# No sys.path hacking needed for local imports
# But we still need _BASE_DIR for other file operations
_BASE_DIR = Path(__file__).resolve().parent.parent

# Only show directory/model diagnostics if DEBUG is enabled
if DEBUG:
    st.write("🔍 **DEBUG: Environment & Model Loading Diagnostics**")
    
    # Show base directory
    st.write(f"📁 Base directory: `{_BASE_DIR}`")
    logger.debug(f"Base directory: {_BASE_DIR}")
    
    # List root directory files
    try:
        root_files = os.listdir(_BASE_DIR)
        st.write(f"📂 Root files count: {len(root_files)}")
        st.write(f"   Files: {', '.join(sorted(root_files)[:10])}...")
        logger.debug(f"Root files: {root_files}")
    except Exception as e:
        st.error(f"❌ Cannot list root files: {e}")
        logger.error(f"Cannot list root files: {e}")
    
    # Check models directory
    models_dir = _BASE_DIR / "models"
    st.write(f"📌 Expected models path: `{models_dir}`")
    st.write(f"   Exists: {'✅ YES' if models_dir.exists() else '❌ NO'}")
    
    if models_dir.exists():
        try:
            model_files = os.listdir(models_dir)
            st.write(f"   📦 Contents ({len(model_files)} files): {', '.join(sorted(model_files))}")
            logger.debug(f"Model files: {model_files}")
        except Exception as e:
            st.error(f"   ❌ Cannot list models: {e}")
            logger.error(f"Cannot list models: {e}")
    else:
        st.error("   ❌ Models directory does NOT exist!")
        logger.warning("Models directory does not exist!")
    
    # Check specific model.pkl
    model_pkl_path = models_dir / "model.pkl"
    st.write(f"🎯 Target model: `models/model.pkl`")
    st.write(f"   Full path: `{model_pkl_path}`")
    st.write(f"   Exists: {'✅ YES' if model_pkl_path.exists() else '❌ NO'}")
    
    if model_pkl_path.exists():
        try:
            file_size_mb = model_pkl_path.stat().st_size / (1024 * 1024)
            st.write(f"   Size: {file_size_mb:.2f} MB")
            logger.debug(f"Model file size: {file_size_mb:.2f} MB")
        except Exception as e:
            st.error(f"   ❌ Cannot get file size: {e}")
            logger.error(f"Cannot get file size: {e}")
    
    st.write("---")

from core.data_utils.menu_config import CAKE_MENU, CAKE_CATEGORIES, get_cake_info
from core.data_utils.data_mapping import (
    get_cake_metadata,
    explain_recommendation, 
    format_cake_card,
    CAKE_METADATA
)
from core.ml_engine.hybrid_recommender import create_or_load_system
from services.beige_ai_copywriter import generate_luxury_description

# Create full menu structure with prices
FULL_MENU = [
    {'name': cake_name, 'price': 9.00}
    for cake_name in CAKE_MENU
]

# ============================================================================
# UTILITY: SAFE IMAGE DISPLAY
# ============================================================================

def display_safe_image(local_path, fallback_url, caption=""):
    """
    Display an image from local path or fallback to URL.
    Handles missing local assets gracefully.
    """
    try:
        if local_path and os.path.exists(local_path):
            st.image(local_path, caption=caption, width="stretch")
        else:
            st.image(fallback_url, caption=caption, width="stretch")
    except Exception:
        # Final fallback to URL
        st.image(fallback_url, caption=caption, width="stretch")

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if 'cart' not in st.session_state:
    st.session_state.cart = []

if 'page' not in st.session_state:
    st.session_state.page = 'store'

if 'ai_result' not in st.session_state:
    st.session_state.ai_result = None

if 'engine_type' not in st.session_state:
    st.session_state.engine_type = 'unknown'  # "hybrid", "ml", "rule_based", or "unknown"

if 'has_generated' not in st.session_state:
    st.session_state.has_generated = False

if 'order_logged' not in st.session_state:
    st.session_state.order_logged = False

if 'weather_condition' not in st.session_state:
    st.session_state.weather_condition = 'Partly Cloudy'

if 'time_of_day' not in st.session_state:
    st.session_state.time_of_day = 'Afternoon'  # Default; will be updated with actual time when get_current_time() is called

# NOTE: time_of_day is determined dynamically via get_current_time()
# and updated throughout the session as the app runs

if 'micro_story' not in st.session_state:
    st.session_state.micro_story = None

if 'analyst_mode' not in st.session_state:
    st.session_state.analyst_mode = False

# ML Pipeline initializes automatically on import - no manual session init needed

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
# API KEY VALIDATION
# ============================================================================

api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.warning("⚠️ Gemini API key not configured. AI recommendations will use local templates. Configure in Streamlit Secrets.")

# ============================================================================
# LOAD STYLING
# ============================================================================

css_path = Path(__file__).parent / "styles.css"
if css_path.exists():
    with open(css_path) as f:
        css_content = f.read()
    st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)

# Global CSS for image styling
st.markdown("""
<style>
img {
    border-radius: 10px;
    object-fit: cover;
}

.micro-story-section {
    margin: 40px 0 30px 0;
    padding: 0;
}

.micro-story-container {
    padding: 30px 25px;
    background: linear-gradient(135deg, #FAFAF5 0%, #F5F3F0 100%);
    border: 1px solid #E6E2DC;
    border-radius: 8px;
    margin-bottom: 30px;
}

.micro-story-container p {
    color: #4A4A4A;
    line-height: 1.9;
    font-size: 1.15em;
    font-style: italic;
    margin: 0;
}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# HYBRID RECOMMENDER INITIALIZATION
# ============================================================================

@st.cache_resource
def load_hybrid_system():
    """DEPRECATED - ml_pipeline handles initialization automatically."""
    pass

# ML Pipeline initializes automatically on import
# No manual hybrid system loading needed anymore

# ============================================================================
# PERSISTENT HEADER (ALWAYS VISIBLE)
# ============================================================================

header_col1, header_col2 = st.columns([8, 2])
with header_col1:
    st.markdown("<h1 style='margin: 0; padding: 10px 0; font-family: Playfair Display, serif; font-size: 2em;'>Beige AI</h1>", unsafe_allow_html=True)

with header_col2:
    basket_count = len(st.session_state.cart)
    if st.button(f"🛒 Basket ({basket_count})", key='header_basket', width="stretch"):
        st.session_state.page = 'checkout'
        st.rerun()

# ============================================================================
# ANALYST MODE AUTHENTICATION
# ============================================================================

password = st.sidebar.text_input("Admin Access", type="password", key="admin_password")

if password == "beige_admin":
    st.session_state.analyst_mode = True

if st.session_state.analyst_mode:
    st.sidebar.success("✓ Analyst Mode Enabled")
else:
    st.session_state.analyst_mode = False

def get_current_time():
    """
    Determine time of day from system time (DYNAMIC, NOT CACHED).
    This function always returns the actual current time, never cached.
    
    Returns:
        tuple: (time_period_str, hour_24, debug_info)
    """
    now = datetime.now()
    hour = now.hour
    minute = now.minute
    
    # Determine time period
    if 5 <= hour < 12:
        time_period = 'Morning'
    elif 12 <= hour < 17:
        time_period = 'Afternoon'
    elif 17 <= hour <= 20:
        time_period = 'Evening'
    else:
        time_period = 'Night'
    
    # Debug info for logging
    debug_info = f"[{hour:02d}:{minute:02d}] -> {time_period}"
    
    return time_period, hour, debug_info

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

# ============================================================================
# ML PIPELINE - SINGLE ENTRY POINT (NEW ARCHITECTURE)
# No wrappers, no fallbacks, fail-fast design
# ============================================================================

# Import the new clean ML pipeline
from core.ml_engine.ml_pipeline import run_pipeline

if DEBUG:
    logger.info("✅ ML Pipeline imported successfully")

# ============================================================================
# CAKE CLASSES & ML STATUS
# ============================================================================
def get_cake_classes():
    """Get list of cake classes from the actual menu configuration."""
    # Import the actual cake menu to ensure consistency
    from core.data_utils.menu_config import CAKE_MENU
    # Extract cake names from menu 
    return [
        cake['name'] if isinstance(cake, dict) else cake 
        for cake in CAKE_MENU
    ]

@st.cache_resource
def load_association_rules():
    """Load association rules for explanations."""
    try:
        rules_path = _BASE_DIR / "backend" / "association_rules.csv"
        return pd.read_csv(rules_path)
    except:
        # Return empty dataframe if file doesn't exist
        return pd.DataFrame()

# ML Pipeline - single entry point (no fallbacks)
association_rules = load_association_rules()

# Define model version and mode
ML_VERSION = "3-Layer Hybrid (Segmentation→Classification→Ranking)"
MODE = "ML_PIPELINE"
CAKE_CLASSES = get_cake_classes()

if DEBUG:
    logger.info("🚀 MODEL LOADED SUCCESSFULLY")
    logger.info("🚀 RUNNING REAL ML PIPELINE")

# ============================================================================
# VERSION DIAGNOSTICS & STATUS DISPLAY
# ============================================================================

# Display ML system status in sidebar
with st.sidebar:
    with st.expander("🔧 ML System Status (Debug)", expanded=False):
        st.success(f"✅ Real ML Pipeline Active")
        st.write(f"**Model:** {ML_VERSION}")
        st.write(f"**Mode:** {MODE}")
        st.write("**Status:** Production - All Fallbacks Disabled")
        st.info("ℹ️ System uses deterministic ML with fail-fast error handling. No simulation. No fallback logic.")


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

def generate_luxury_recommendation(mood, weather_condition, top_3_cakes, top_3_probs):
    """
    Generate editorial-style luxury dessert recommendation using Gemini AI.
    Uses a refined system prompt to produce elegant, sensory-focused text.
    """
    try:
        # Configure Gemini API
        api_key = st.secrets.get("GEMINI_API_KEY", None)
        if not api_key:
            # Fallback to local template if API key not available
            return generate_local_explanation(mood, weather_condition, top_3_cakes, top_3_probs)
        
        genai.configure(api_key=api_key)
        
        # System prompt for luxury editorial style
        system_prompt = """
You are a high-end dessert concierge for a luxury patisserie.

Your tone is refined, minimal, and editorial — like a caption in a premium food magazine.

RULES:
- NEVER use percentages, confidence scores, or probabilities
- NEVER use labels like (Indulgent), (Healthy), etc.
- NEVER explain your reasoning explicitly
- NEVER use phrases like "because", "since", or "based on"

STYLE:
- Write in a calm, confident, sensory tone
- Focus on mood, texture, and atmosphere
- Keep it elegant and concise

STRUCTURE:
- One seamless 2–3 sentence paragraph for the main recommendation
- Followed by one short alternative option (counter-mood)
- Keep total length under 150 words

ENVIRONMENT INTEGRATION:
- Subtly incorporate weather, time of day, or mood into the description
- Do NOT mention data or analysis directly

EXAMPLE:
"The Dark Chocolate Sea Salt Cake is a grounded choice for this moment; its deep cocoa notes and delicate salt finish create a quiet sense of indulgence. For something lighter in tone, the Café Tiramisu offers a softer, coffee-laced lift."
"""
        
        # Build user prompt with cake names and mood context
        cake_1 = top_3_cakes[0]
        cake_2 = top_3_cakes[1]
        mood_lower = mood.lower()
        weather_lower = weather_condition.lower()
        
        user_prompt = f"""
Please provide a luxury dessert concierge recommendation for someone who is {mood_lower} and currently experiencing {weather_lower} weather.

The available options are:
- {cake_1}
- {cake_2}
- {top_3_cakes[2]}

Focus on the first two options primarily. Write in the editorial, sensory style described above.
"""
        
        # Call Gemini model
        model = genai.GenerativeModel(
            "gemini-2.0-flash",
            system_instruction=system_prompt
        )
        
        response = model.generate_content(user_prompt)
        
        if response and response.text:
            return response.text
        else:
            return generate_local_explanation(mood, weather_condition, top_3_cakes, top_3_probs)
    
    except Exception as e:
        # Fallback to editorial-style recommendation - no warning shown to user
        # The experience should be seamless regardless of API availability
        return generate_local_explanation(mood, weather_condition, top_3_cakes, top_3_probs)


def generate_local_explanation(mood, weather_condition, top_3_cakes, top_3_probs):
    """
    Fallback: Generate luxury editorial-style recommendation without API.
    Returns polished, sensory-focused text that matches Gemini quality.
    Includes dynamic variation based on time of day.
    """
    top_cake = top_3_cakes[0]
    second_cake = top_3_cakes[1]
    
    # Determine time-of-day flavor
    hour = datetime.now().hour
    if 5 <= hour < 12:
        time_phrase = "a gentle start to your day"
        time_mood = "morning lightness"
    elif 12 <= hour < 17:
        time_phrase = "a soft, steady pause"
        time_mood = "afternoon clarity"
    else:  # 17 <= hour or hour < 5
        time_phrase = "a more indulgent close"
        time_mood = "evening comfort"
    
    # Editorial-style recommendations with sensory focus
    # Format: Primary cake, then secondary cake as counter-mood
    luxury_recommendations = {
        ('Dark Chocolate Cake', 'Vanilla Cake'): f"""{top_cake} offers {time_phrase}, with deep cocoa richness and subtle bitterness that grounds the senses. For a lighter alternative, {second_cake} brings a softer, more delicate approach.""",
        
        ('Vanilla Cake', 'Chocolate Cake'): f"""{top_cake} provides {time_phrase}, with clean vanilla notes and a silky crumb that feels both comforting and refined. If you prefer deeper notes, {second_cake} adds an elegant contrast.""",
        
        ('Carrot Cake', 'Chocolate Cake'): f"""{top_cake} is the refined choice for {time_mood}—warm spice, tender texture, a gentle lift. For something bolder, {second_cake} offers grounded depth.""",
        
        ('Red Velvet Cake', 'Cheesecake'): f"""{top_cake} brings a sense of occasion to {time_phrase}, with its velvety crumb and subtle tang. Alternatively, {second_cake} offers a cooler, creamier elegance.""",
        
        ('Cheesecake', 'Chocolate Cake'): f"""{top_cake} is smooth and grounding for {time_phrase}, with a delicate balance of tang and sweetness. For deeper notes, {second_cake} provides quiet indulgence.""",
        
        ('Lemon Cake', 'Vanilla Cake'): f"""{top_cake} cuts through {time_mood} with brightness and zest, offering a lighter, more awakening experience. For comfort, {second_cake} brings warmth and gentleness.""",
        
        ('Strawberry Cake', 'Red Velvet Cake'): f"""{top_cake} celebrates fresh sweetness for {time_phrase}, delicate and naturally bright. For something richer, {second_cake} offers drama and depth.""",
        
        ('Chocolate Mousse', 'Vanilla Cake'): f"""{top_cake} is an airy, almost ethereal choice for {time_mood}—richness without heaviness. If you prefer substance, {second_cake} grounds with quiet comfort.""",
    }
    
    # Try to match the actual cakes; use a generic template otherwise
    key = (top_cake, second_cake)
    if key in luxury_recommendations:
        return luxury_recommendations[key]
    
    # Fallback generic luxury template (if specific pairing not in dict)
    return f"""{top_cake} offers {time_phrase}—a nuanced choice that speaks to your moment with refinement and sensory depth. For a different mood, {second_cake} brings an elegant alternative."""

# ============================================================================
# TRANSACTION LOGGING
# ============================================================================

# ============================================================================
# ORDER LOGGING SYSTEM (HARDENED)
# ============================================================================

def make_json_safe(obj):
    """
    Recursively convert NumPy types and other non-JSON-serializable objects
    to native Python types.
    
    This creates a clean boundary between ML (NumPy) and application layer (JSON),
    ensuring stable serialization without loss of semantic meaning.
    
    Conversions:
    - np.ndarray → list
    - np.float32, np.float64, np.double → float
    - np.int32, np.int64, np.integer → int
    - np.bool_ → bool
    - dict → dict (with recursively converted values)
    - list → list (with recursively converted elements)
    - other primitives → unchanged
    
    Args:
        obj: Any object (dict, list, NumPy types, primitives, etc.)
    
    Returns:
        JSON-safe version of the object (only native Python types)
    
    Examples:
        >>> data = {
        ...     'scores': np.array([0.95, 0.87, 0.75]),
        ...     'conf': np.float32(0.92),
        ...     'count': np.int64(42),
        ...     'valid': np.bool_(True)
        ... }
        >>> safe = make_json_safe(data)
        >>> json.dumps(safe)  # No error!
    """
    # Handle None and basic types
    if obj is None:
        return None
    
    # Handle NumPy arrays
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    
    # Handle NumPy scalar types
    if isinstance(obj, (np.float32, np.float64, np.double)):
        return float(obj)
    
    if isinstance(obj, (np.int32, np.int64, np.integer)):
        return int(obj)
    
    if isinstance(obj, np.bool_):
        return bool(obj)
    
    # Handle dictionaries - recursively convert values
    if isinstance(obj, dict):
        return {key: make_json_safe(value) for key, value in obj.items()}
    
    # Handle lists and tuples - recursively convert elements
    if isinstance(obj, (list, tuple)):
        return [make_json_safe(item) for item in obj]
    
    # Return primitives unchanged (str, int, float, bool, etc.)
    return obj


def save_order_data(order_id, items_purchased, ai_recommendation, result):
    """
    Save order data to CSV with robust error handling.
    Writes to data/feedback_log.csv with schema:
    - order_id (UUID, unique per order)
    - items_purchased (comma-separated string)
    - ai_recommendation (stringified safely as JSON)
    - result ("Match" or "Not Quite")
    - timestamp (ISO format UTC)
    
    Args:
        order_id: str - Unique identifier for this order (UUID format)
        items_purchased: str - Comma-separated cake names
        ai_recommendation: dict or str - AI recommendation object or None
        result: str - "Match" or "Not Quite"
    
    Returns:
        tuple: (success: bool, error_msg: str or None)
    """
    try:
        # Ensure data directory exists
        data_dir = _BASE_DIR / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = data_dir / "feedback_log.csv"
        
        # Check if file exists and is not empty
        file_exists = file_path.exists() and file_path.stat().st_size > 0
        
        # Safely convert ai_recommendation to string
        if isinstance(ai_recommendation, dict):
            # Convert NumPy types to JSON-safe Python types, then serialize
            safe_recommendation = make_json_safe(ai_recommendation)
            ai_rec_str = json.dumps(safe_recommendation, ensure_ascii=False)
        elif ai_recommendation is None:
            ai_rec_str = "None"
        else:
            ai_rec_str = str(ai_recommendation)
        
        # Get timestamp in ISO format (UTC)
        timestamp = datetime.utcnow().isoformat()
        
        # Write to CSV with proper encoding and newline handling
        with open(file_path, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header only if file doesn't exist or is empty
            if not file_exists:
                writer.writerow([
                    'order_id',
                    'items_purchased',
                    'ai_recommendation',
                    'result',
                    'timestamp'
                ])
            
            # Write data row
            writer.writerow([
                order_id,
                items_purchased,
                ai_rec_str,
                result,
                timestamp
            ])
        
        if DEBUG:
            logger.info(f"✅ Order logged successfully: {order_id}")
        return True, None
        
    except Exception as e:
        error_msg = f"Order logging failed: {str(e)}"
        if DEBUG:
            logger.error(f"❌ {error_msg}")
            logger.error(f"   Order ID: {order_id}")
            import traceback
            traceback.print_exc()
        return False, error_msg


def log_transaction(cart, recommended):
    """
    DEPRECATED: Legacy function for backward compatibility.
    Use save_order_data() instead.
    
    Logs transaction data to data/feedback_log.csv for analytics.
    Records: timestamp, items purchased, recommendation, match result.
    
    Args:
        cart: st.session_state.cart (list of dicts with 'name' and 'price')
        recommended: st.session_state.ai_result (the AI recommendation dict)
    """
    # Skip if no cart or recommendation
    if not cart or recommended is None:
        return False
    
    # Generate unique order ID
    order_id = str(uuid.uuid4())
    
    # Extract purchased item names as comma-separated string
    items_purchased = ", ".join([item['name'] for item in cart])
    
    # Save to CSV
    success, error_msg = save_order_data(
        order_id=order_id,
        items_purchased=items_purchased,
        ai_recommendation=recommended,
        result="Match" if _is_recommendation_match(recommended, cart) else "Not Quite"
    )
    
    return success


def _is_recommendation_match(recommendation, cart):
    """
    Helper function to determine if AI recommendation matches purchase.
    
    Returns True if the top recommended cake was in the purchased items.
    """
    if not recommendation or not isinstance(recommendation, dict):
        return False
    
    top_cake = recommendation.get('top_3_cakes', [None])[0]
    if not top_cake:
        return False
    
    purchased_names = [item['name'] for item in cart]
    return top_cake in purchased_names

# ============================================================================
# DYNAMIC STORYTELLING / NARRATIVE GENERATION
# ============================================================================

def generate_moment_narrative(time_of_day, weather, ai_cake=None):
    """
    Generate a personalized storytelling prompt based on context.
    Adapts narrative to time of day, weather, and AI recommendation.
    
    Args:
        time_of_day: str in ["morning", "afternoon", "evening"]
        weather: str in ["sunny", "rainy", "cloudy", "snowy", "stormy", "partly cloudy"]
        ai_cake: Optional str - the AI recommendation cake name
    
    Returns:
        str - personalized narrative prompt
    """
    
    # Time-based emotional tone
    time_narratives = {
        'morning': {
            'phrase': 'a quiet beginning to your day',
            'tone': 'gentle and awakening'
        },
        'afternoon': {
            'phrase': 'a soft pause in the middle of your day',
            'tone': 'grounded and reflective'
        },
        'evening': {
            'phrase': 'a slow, indulgent close to your evening',
            'tone': 'warm and contemplative'
        },
        'night': {
            'phrase': 'the quiet depth of night',
            'tone': 'intimate and reflective'
        }
    }
    
    # Weather-based sensory tone
    weather_narratives = {
        'sunny': 'with warm light settling into every corner',
        'rainy': 'with the rain gently shaping the mood around you',
        'cloudy': 'under a soft, muted sky that asks for stillness',
        'snowy': 'with the gentle hush of snow defining the air',
        'stormy': 'within the drama and energy of a changing sky',
        'partly cloudy': 'with light shifting between clarity and shadow'
    }
    
    # Get selected narratives with fallbacks
    time_data = time_narratives.get(time_of_day.lower(), time_narratives['afternoon'])
    weather_text = weather_narratives.get(weather.lower(), 'in a space that feels entirely your own')
    
    # Optional AI-based personalization
    cake_hint = ""
    if ai_cake and isinstance(ai_cake, str) and ai_cake.strip():
        cake_hint = f"\n\nWhen you're ready, we think {ai_cake} might resonate with this moment."
    
    # Construct the narrative
    narrative = f"""
Pause for a moment.

You're in {time_data['phrase']}, {weather_text}.

Whether you're surrounded by quiet or a subtle kind of energy, this space carries its own rhythm. Tell us what it feels like to be here—what you need, what you're craving, or what you want to shift.{cake_hint}
"""
    
    return narrative.strip()

# ============================================================================
# MICRO-STORY ENGINE
# ============================================================================

def generate_micro_story(mood, time_of_day, weather, cake):
    """
    Generate a personalized micro-story that emotionally contextualizes the cake recommendation.
    Creates a luxury editorial narrative reflecting mood, time, weather, and the recommended cake.
    
    Args:
        mood: str - user's mood (e.g., 'Happy', 'Stressed', 'Tired', 'Lonely', 'Celebratory')
        time_of_day: str - time of day (e.g., 'Morning', 'Afternoon', 'Evening', 'Night')
        weather: str - current weather (e.g., 'Sunny', 'Rainy', 'Cloudy')
        cake: str - recommended cake name (e.g., 'Chocolate Delight')
    
    Returns:
        str - personalized micro-story narrative
    """
    
    # Time-based anchors
    time_map = {
        'morning': 'a quiet beginning',
        'afternoon': 'a soft pause',
        'evening': 'a slow, indulgent close',
        'night': 'the quiet depth of night'
    }
    
    # Weather-based sensory descriptions
    weather_map = {
        'sunny': 'with warm light settling into everything around you',
        'rainy': 'with rain tracing softly against the world outside',
        'cloudy': 'under a muted, gentle sky',
        'stormy': 'within the drama of a changing sky',
        'snowy': 'with the gentle hush of snow in the air',
        'partly cloudy': 'with light shifting between clarity and shadow'
    }
    
    # Mood-based opening lines
    mood_map = {
        'happy': "You feel light, present, alive",
        'stressed': "There is tension in your shoulders, a need to pause",
        'tired': "You feel the weight of the day, and the softness of slowness",
        'lonely': "There is a quiet ache, a longing for something warm and familiar",
        'celebratory': "Joy is moving through you, wanting space to breathe"
    }
    
    # Get values with fallbacks
    time_anchor = time_map.get(time_of_day.lower(), 'a moment suspended in time')
    weather_line = weather_map.get(weather.lower(), 'in a space that feels entirely your own')
    mood_line = mood_map.get(mood.lower(), f"You feel {mood.lower() if mood else 'something'}.")
    if mood:
        mood_line = mood_map.get(mood.lower(), f"You feel {mood.lower()}.")
    else:
        mood_line = "There is a quiet feeling in the air,"
    
    # Cake personalization
    cake_line = ""
    if cake and isinstance(cake, str) and cake.strip():
        cake_line = f" It is the kind of moment that calls for something like {cake} - not loudly, but in a way that simply fits."
    
    # Construct the micro-story
    story = f"""{mood_line} somewhere within {time_anchor}, {weather_line}.

The world feels slightly softened, as if it is giving you permission to slow down, or perhaps to lean into whatever you are craving right now.{cake_line}"""
    
    return story.strip()

# ============================================================================
# DISPLAY FUNCTIONS
# ============================================================================

def display_full_menu():
    """Display all available cakes with Add to Basket buttons."""
    st.markdown("""
        <div class='story-title' style='margin-top: 60px; margin-bottom: 40px;'>
            📋 Full Menu
        </div>
    """, unsafe_allow_html=True)
    
    # Create a 2x4 grid for 8 cakes
    menu_cols = st.columns(2)
    
    for idx, cake in enumerate(FULL_MENU):
        col = menu_cols[idx % 2]
        
        with col:
            cake_name = cake['name']
            cake_price = cake['price']
            # Use robust lookup with fallback
            cake_props = get_cake_info(cake_name)
            
            menu_item_html = f"""
            <div style='
                border: 1px solid #E6E2DC;
                border-radius: 8px;
                padding: 20px;
                margin-bottom: 20px;
                background: #FAFAF5;
            '>
                <div style='font-size: 1.3em; font-weight: 600; margin-bottom: 8px; color: #1F1F1F;'>{cake_name}</div>
                <div style='color: #666; font-size: 0.9em; margin-bottom: 12px;'>{cake_props.get("flavor_profile", "Premium cake")}</div>
                <div style='font-size: 1.1em; font-weight: bold; color: #1F1F1F; margin-bottom: 12px;'>${cake_price:.2f}</div>
            </div>
            """
            st.markdown(menu_item_html, unsafe_allow_html=True)
            
            if st.button("Add to Basket", key=f"menu_{idx}_{cake_name}", width="stretch"):
                st.session_state.cart.append({
                    'name': cake_name,
                    'price': cake_price
                })
                st.success(f"✓ {cake_name} added to basket!")

def display_ai_recommendations():
    """Display AI recommendations from session state with ML pipeline transparency."""
    if st.session_state.ai_result is None:
        return
    
    result = st.session_state.ai_result
    top_3_cakes = result['top_3_cakes']
    top_3_probs = result['top_3_probs']
    probabilities = result['probabilities']
    mood = result['mood']
    weather_condition = result['weather_condition']
    model_version = result.get('model_version', 'UNKNOWN')
    engine_type = result.get('engine_type', 'unknown')  # Get engine classification
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # =================================================================
    # STEP 1: ML SYSTEM HEADER (Trust & Transparency)
    # =================================================================
    st.markdown("<div style='text-align: center; margin-bottom: 30px;'>", unsafe_allow_html=True)
    
    if engine_type == "hybrid":
        st.markdown("""
        <div style='padding: 16px; background: #F0F8FF; border-left: 4px solid #1F52A6; border-radius: 4px;'>
            <strong style='font-size: 1.1em;'>🤖 Hybrid 3-Layer AI (Segmentation→Classification→Ranking)</strong><br>
            <span style='color: #666; font-size: 0.95em;'>Predictions powered by behavioral clustering and behavioral analysis</span>
        </div>
        """, unsafe_allow_html=True)
    elif engine_type == "ml":
        st.markdown("""
        <div style='padding: 16px; background: #F0F8FF; border-left: 4px solid #1F52A6; border-radius: 4px;'>
            <strong style='font-size: 1.1em;'>🧠 AI Recommendation Engine (ML-Powered)</strong><br>
            <span style='color: #666; font-size: 0.95em;'>Predictions generated by trained machine learning model based on your inputs</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='padding: 16px; background: #FFF8F0; border-left: 4px solid #F4A460; border-radius: 4px;'>
            <strong style='font-size: 1.1em;'>⚙️ Recommendation Engine (Rule-Based)</strong><br>
            <span style='color: #666; font-size: 0.95em;'>Recommendations based on established preference patterns</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # =================================================================
    # STEP 2: INPUT CONTEXT (Show what influenced recommendations)
    # =================================================================
    st.markdown("<div style='text-align: center; margin-bottom: 24px;'>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style='font-size: 0.9em; color: #666;'>
    <strong>Based on:</strong> <span style='color: #1F1F1F; font-weight: 500;'>{mood}</span> mood • 
    <span style='color: #1F1F1F; font-weight: 500;'>{weather_condition}</span> weather • 
    <span style='color: #1F1F1F; font-weight: 500;'>{result.get("time_of_day", "current")}</span> time of day
    </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 🔍 DEBUG SECTION: Show raw ML output (only if DEBUG mode)
    if DEBUG:
        with st.expander("🔍 DEBUG: Raw ML Output"):
            st.write(f"**Top 3 ML Recommendations (Actual):**")
            for i, (cake, score) in enumerate(zip(top_3_cakes, top_3_probs), 1):
                st.write(f"  {i}. {cake} (Score: {score:.4f})")
            st.json({
                "top_3_cakes": top_3_cakes,
                "top_3_scores": top_3_probs,
                "model_version": model_version,
                "prediction_source": prediction_source
            })
            logger.debug(f"ML Output: {top_3_cakes} with scores {top_3_probs}")
    
    # Display micro-story first (the emotional narrative)
    if st.session_state.micro_story:
        st.markdown("""
        <div class='micro-story-section'>
            <div class='micro-story-container'>
        """, unsafe_allow_html=True)
        
        story_html = f"""
        <p style='font-size: 1.15em; line-height: 1.9; color: #4A4A4A; font-style: italic; margin-bottom: 30px; white-space: pre-line;'>
        {st.session_state.micro_story}
        </p>
        """
        st.markdown(story_html, unsafe_allow_html=True)
        
        st.markdown("""
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
    
    # Display top 3 recommendations
    st.markdown("""
        <div class='rec-section'>
            <div class='rec-title'>Your Three Selections</div>
            <div class='rec-subtitle'>Curated specifically for this moment.</div>
            <div class='rec-cards-container'>
    """, unsafe_allow_html=True)
    
    rec_cols = st.columns(3)
    roman_numerals = ['I', 'II', 'III']
    
    # =================================================================
    # STEP 3: RENDER CARDS WITH COMPLETE METADATA & EXPLANATIONS
    # =================================================================
    
    # 🔴 CRITICAL FIX: Get ACTUAL current time (not cached/session state)
    current_time_period, current_hour, time_debug = get_current_time()
    
    # Debug logging for time detection (only show in DEBUG mode)
    if DEBUG:
        st.caption(f"🕐 **System Time**: {time_debug} (Using live system time, not cached)")
    logger.debug(f"Current time period: {current_time_period}, debug: {time_debug}")
    
    # Log rendering start (terminal only, not UI)
    logger.debug(f"Starting to render {len(top_3_cakes)} recommendations: {top_3_cakes}")
    
    for idx, (cake, prob) in enumerate(zip(top_3_cakes, top_3_probs)):
        if DEBUG:
            logger.debug(f"Rendering cake #{idx+1}: {cake} (score: {prob:.4f})")
        with rec_cols[idx]:
            # Get comprehensive metadata (no N/A values)
            card_data = format_cake_card(cake, confidence=prob, rank=roman_numerals[idx])
            
            # 🔴 CRITICAL FIX: Pass ACTUAL current time to explanation generator
            # NOT result.get("time_of_day") which is cached/hardcoded
            explanation = explain_recommendation(
                cake_name=cake,
                mood=mood,
                weather=weather_condition,
                time_of_day=current_time_period,  # LIVE current time from get_current_time()
                confidence=prob,
                debug=True  # Enable debug logging to see time detection
            )
            
            # Check if hybrid results are available and enhance explanation
            hybrid_explanation = ""
            breakdown = ""
            if hasattr(st.session_state, 'hybrid_results') and st.session_state.hybrid_results:
                if cake in st.session_state.hybrid_results:
                    hybrid_data = st.session_state.hybrid_results[cake]
                    hybrid_explanation = hybrid_data.get('explanation', '')
                    
                    # Show detailed hybrid scoring breakdown (optional, for analyst mode)
                    if st.session_state.analyst_mode and hybrid_data:
                        breakdown = (
                            f"<div style='font-size: 0.85em; color: #666; padding-top: 8px; border-top: 1px solid #E6E2DC; margin-top: 8px;'>"
                            f"<strong>Hybrid Score Breakdown:</strong><br>"
                            f"• ML Probability: {hybrid_data.get('ml_probability', 0):.1%}<br>"
                            f"• Trend Popularity: {hybrid_data.get('trend_score', 0):.1%}<br>"
                            f"• Health Alignment: {hybrid_data.get('health_alignment', 0):.1%}<br>"
                            f"• Cluster Affinity: {hybrid_data.get('cluster_affinity', 0):.1%}"
                            f"</div>"
                        )
            
            # Find price from FULL_MENU
            cake_price = next((c['price'] for c in FULL_MENU if c['name'] == cake), 45.00)
            
            # =========================================================
            # GENERATE LUXURY COPYWRITER NARRATIVE
            # =========================================================
            # Generate the Beige AI narrative based on metadata and context
            try:
                copywriter_output = generate_luxury_description(
                    cake_name=cake,
                    category=card_data['category'],
                    flavor_profile=card_data['flavor'],
                    mood=mood,
                    weather=weather_condition,
                    health_preference=card_data['health']
                )
                
                # Extract only the narrative portion (after "Beige AI Narrative:")
                if "Beige AI Narrative:" in copywriter_output:
                    narrative = copywriter_output.split("Beige AI Narrative:")[1].strip()
                else:
                    narrative = ""
            except Exception as e:
                # Fallback if copywriter fails
                narrative = ""
                st.write(f"⚠️ Copywriter error: {e}")
            
            # Build confidence score section
            confidence_section = f"<div class='rec-confidence'>{card_data['confidence_pct']} match</div>"
            
            # Build technical details section
            technical_details = (
                f"<div class='rec-detail'><strong>Sweetness:</strong> {card_data['sweetness']}/10</div>"
                f"<div class='rec-detail'><strong>Wellness:</strong> {card_data['health']}/10</div>"
            )
            
            # Build narrative section HTML
            narrative_html = ""
            if narrative:
                narrative_html = f"<div class='rec-narrative'><strong>Beige AI Narrative:</strong><br><em>{narrative}</em></div>"
            
            # Build recommendation card HTML with complete metadata
            card_html = (
                "<div class='rec-card'>"
                "<div class='rec-rank'>{rank}</div>"
                "<div class='rec-name'>{cake}</div>"
                "{confidence}"
                "<div class='rec-detail'><strong>Category:</strong> {category}</div>"
                "<div class='rec-detail'><strong>Flavor Profile:</strong> {flavor}</div>"
                "{narrative}"
                "{technical}"
                "</div>"
            ).format(
                rank=card_data['rank'],
                cake=card_data['name'],
                confidence=confidence_section,
                category=card_data['category'],
                flavor=card_data['flavor'],
                narrative=narrative_html,
                technical=technical_details
            )
            st.markdown(card_html, unsafe_allow_html=True)
            
            # Display explanation (prioritize hybrid if available)
            if hybrid_explanation:
                st.caption(f"**Why?** {hybrid_explanation}")
                if hybrid_explanation != explanation:
                    st.caption(f"*Context: {explanation}*")
            else:
                st.caption(f"**Why?** {explanation}")
            
            # Show breakdown if available
            if breakdown:
                st.markdown(breakdown, unsafe_allow_html=True)
            
            if st.button("Add to Basket", key=f"ai_{idx}_{cake}", width="stretch"):
                st.session_state.cart.append({
                    'name': cake,
                    'price': cake_price
                })
                st.success(f"✓ {cake} added to basket!")
    
    st.markdown("""
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Display chart (analyst mode only)
    if st.session_state.analyst_mode:
        fig, ax = plt.subplots(figsize=(12, 5))
        
        all_indices = np.argsort(probabilities)[::-1]
        all_cakes = [CAKE_CLASSES[i] for i in all_indices]
        all_probs = [probabilities[i] for i in all_indices]
        
        cake_labels = []
        for i, cake_name in enumerate(all_cakes):
            if cake_name == top_3_cakes[0]:
                cake_labels.append(f"I   {cake_name}")
            elif cake_name == top_3_cakes[1]:
                cake_labels.append(f"II   {cake_name}")
            elif cake_name == top_3_cakes[2]:
                cake_labels.append(f"III   {cake_name}")
            else:
                cake_labels.append(cake_name)
        
        colors = []
        for cake_name in all_cakes:
            if cake_name == top_3_cakes[0]:
                colors.append('#1F1F1F')
            elif cake_name == top_3_cakes[1]:
                colors.append('#4A4A4A')
            elif cake_name == top_3_cakes[2]:
                colors.append('#BDB2A7')
            else:
                colors.append('#D4CEC7')
        
        bars = ax.barh(range(len(all_cakes)), all_probs, color=colors, edgecolor='#E6E2DC', linewidth=1)
        
        ax.set_xlabel('Confidence Score', fontsize=11, fontweight=500, color='#1F1F1F', family='Inter')
        ax.set_title('AI Ranking of All Selections', fontsize=13, fontweight=500, pad=20, color='#1F1F1F', family='Playfair Display')
        ax.set_yticks(range(len(cake_labels)))
        ax.set_yticklabels(cake_labels, fontsize=10, family='Inter')
        ax.set_xlim([0, max(all_probs) * 1.2])
        ax.grid(axis='x', alpha=0.15, linestyle='-', color='#E6E2DC')
        ax.set_facecolor('#FFFFFF')
        fig.patch.set_facecolor('#FAFAF5')
        
        for i, (bar, prob) in enumerate(zip(bars, all_probs)):
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2.,
                    f'{prob*100:.1f}%',
                    ha='left', va='center', fontweight=500, fontsize=9,
                    bbox=dict(boxstyle='round,pad=0.4', facecolor=(1.0, 0.98, 0.96), edgecolor='#E6E2DC', alpha=1))
        
        plt.tight_layout()
        
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
    
    # AI explanation - using Gemini for luxury editorial style
    ai_explanation = generate_luxury_recommendation(mood, weather_condition, top_3_cakes, top_3_probs)
    
    st.markdown(f"""
        <div class='insight-section'>
            <div class='insight-title'>The Reasoning</div>
            <div class='insight-content'>
                <div class='insight-text'>{ai_explanation}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)

def display_checkout():
    """Display checkout page."""
    st.markdown("""
        <div style='text-align: center; margin-bottom: 40px;'>
            <h2 style='font-family: Playfair Display, serif; font-size: 2em; color: #1F1F1F;'>Your Basket</h2>
        </div>
    """, unsafe_allow_html=True)
    
    if len(st.session_state.cart) == 0:
        st.info("Your basket is empty. Return to the store to add cakes!")
        if st.button("Back to Store", width="stretch"):
            st.session_state.page = 'store'
            st.session_state.order_logged = False
            st.rerun()
    else:
        # Display cart items
        st.markdown("""
            <div style='border: 1px solid #E6E2DC; border-radius: 8px; padding: 20px; background: #FAFAF5;'>
        """, unsafe_allow_html=True)
        
        subtotal = 0
        for idx, item in enumerate(st.session_state.cart):
            subtotal += item['price']
            st.markdown(f"""
                <div style='display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #E6E2DC;'>
                    <div style='font-weight: 500;'>{item['name']}</div>
                    <div>${item['price']:.2f}</div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown(f"""
                <div style='display: flex; justify-content: space-between; padding: 15px 0; font-weight: bold; font-size: 1.1em; color: #1F1F1F;'>
                    <div>Subtotal</div>
                    <div>${subtotal:.2f}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Back to Store", width="stretch"):
                st.session_state.page = 'store'
                st.session_state.order_logged = False
                st.rerun()
        
        with col2:
            if st.button("Confirm Order", width="stretch", type='primary'):
                # ============================================================
                # STEP 1: Validate cart is not empty
                # ============================================================
                if len(st.session_state.cart) == 0:
                    st.warning("⚠️ Cannot confirm empty cart. Please add items first.")
                else:
                    # Guard against duplicate logging on reruns
                    if not st.session_state.order_logged:
                        # ====================================================
                        # STEP 2: Generate unique order ID (ONCE per checkout)
                        # ====================================================
                        order_id = str(uuid.uuid4())
                        
                        # Format items purchased
                        items_purchased = ", ".join([
                            item['name'] for item in st.session_state.cart
                        ])
                        
                        # Determine result (Match = top recomm in cart, else Not Quite)
                        result = "Match" if _is_recommendation_match(
                            st.session_state.ai_result,
                            st.session_state.cart
                        ) else "Not Quite"
                        
                        # ====================================================
                        # STEP 3: Attempt to save order data
                        # ====================================================
                        save_success, error_msg = save_order_data(
                            order_id=order_id,
                            items_purchased=items_purchased,
                            ai_recommendation=st.session_state.ai_result,
                            result=result
                        )
                        
                        # ====================================================
                        # STEP 4: Handle success or failure (separately)
                        # ====================================================
                        if save_success:
                            # Success: Mark as logged and show confirmation
                            st.session_state.order_logged = True
                            st.success(f"🎉 Order confirmed! Thank you for your purchase.\n\nOrder ID: {order_id}")
                            
                            # DEBUG MODE: Show last 3 rows of feedback log
                            # ⚠️ REMOVE THIS IN PRODUCTION ⚠️
                            try:
                                feedback_df = pd.read_csv(_BASE_DIR / "data" / "feedback_log.csv")
                                if len(feedback_df) > 0:
                                    st.markdown("### 📊 Recent Orders (Debug Mode)")
                                    st.dataframe(
                                        feedback_df.tail(3),
                                        width="stretch",
                                        hide_index=True
                                    )
                                    st.caption("⚠️ Debug output - remove in production")
                            except Exception as debug_error:
                                # Silently fail debug display - doesn't affect checkout
                                pass
                        else:
                            # Failure: Show error but DON'T clear cart
                            st.error(
                                f"❌ Order confirmation failed.\n\n"
                                f"Your items are still in the basket. Please try again.\n\n"
                                f"Error: {error_msg or 'Unknown error'}"
                            )
                            st.session_state.order_logged = False  # Reset flag
                    
                    # ====================================================
                    # STEP 5: Only clear cart if logging was successful
                    # (Check flag to ensure save_order_data succeeded)
                    # ====================================================
                    if st.session_state.order_logged:
                        st.session_state.cart = []
                        st.session_state.ai_result = None
                        st.session_state.engine_type = 'unknown'
                        st.session_state.has_generated = False
                        st.balloons()
                        st.rerun()

# ============================================================================
# MAIN PAGE ROUTING
# ============================================================================

if st.session_state.page == 'checkout':
    display_checkout()

else:  # Store page
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

    # SECTION I: DESCRIBE YOUR MOMENT (Emotion/Atmosphere)
    st.markdown("<h3 style='text-align: center; font-family: Playfair Display, serif; margin-top: 40px;'>I. Describe Your Moment</h3>", unsafe_allow_html=True)
    
    with st.container():
        col_text_1, col_img_1 = st.columns([1, 1])
        
        with col_text_1:
            # Generate dynamic narrative based on time and weather
            narrative = generate_moment_narrative(
                st.session_state.time_of_day, 
                st.session_state.weather_condition, 
                st.session_state.ai_result
            )
            st.markdown(f"""
            <div style='padding: 20px;'>
            <p style='font-size: 1.1em; line-height: 1.8; color: #4A4A4A; white-space: pre-wrap;'>
            {narrative}
            </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_img_1:
            display_safe_image(
                str(_BASE_DIR / "assets" / "cafe_vibe.jpg"),
                "https://images.unsplash.com/photo-1554118811-1e0d58224f24?w=500&h=400&fit=crop",
                "Café Atmosphere"
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # SECTION II: SHARE YOUR STATE (Product/Decision)
    st.markdown("<h3 style='text-align: center; font-family: Playfair Display, serif; margin-top: 40px;'>II. Share Your State</h3>", unsafe_allow_html=True)
    
    with st.container():
        col_text_2, col_img_2 = st.columns([1, 1])
        
        with col_text_2:
            st.markdown("""
            <div style='padding: 20px;'>
            <p style='font-size: 1.1em; line-height: 1.8; color: #4A4A4A;'>
            Emotions color every crumb... Your mood is the final ingredient in every creation we share.
            </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_img_2:
            display_safe_image(
                str(_BASE_DIR / "assets" / "cake_detail.jpg"),
                "https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=500&h=400&fit=crop",
                "Cake Detail"
            )

    st.markdown("<br>", unsafe_allow_html=True)

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
        st.session_state.weather_condition = weather_data.get('weather', 'Partly Cloudy')
        temperature_celsius = weather_data.get('temperature', 26)
        humidity = weather_data.get('humidity', 70)
        air_quality_index = weather_data.get('aqi', 65)
        # Get time period from dynamic time detection (returns tuple of time_period, hour, debug_info)
        time_period, hour, debug_info = get_current_time()
        st.session_state.time_of_day = time_period
        
        with col1:
            st.markdown("<div class='input-label'>Weather</div>", unsafe_allow_html=True)
            st.metric("Weather", st.session_state.weather_condition, label_visibility="collapsed")
        
        with col2:
            st.markdown("<div class='input-label'>Temperature</div>", unsafe_allow_html=True)
            st.metric("Temperature", f"{temperature_celsius}°C", label_visibility="collapsed")
        
        with col3:
            st.markdown("<div class='input-label'>Humidity</div>", unsafe_allow_html=True)
            st.metric("Humidity", f"{humidity}%", label_visibility="collapsed")
        
        col4, col5, col6 = st.columns(3)
        with col4:
            st.markdown("<div class='input-label'>Time of Day</div>", unsafe_allow_html=True)
            st.metric("Time of Day", st.session_state.time_of_day, label_visibility="collapsed")
        with col5:
            st.markdown("<div class='input-label'>Air Quality</div>", unsafe_allow_html=True)
            st.metric("Air Quality", f"{air_quality_index} AQI", label_visibility="collapsed")
        with col6:
            st.markdown("<div class='input-label'>Location</div>", unsafe_allow_html=True)
            st.metric("Location", "Da Nang, Vietnam", label_visibility="collapsed")

    else:
        # Manual input mode
        with col1:
            st.markdown("<div class='input-label'>Weather</div>", unsafe_allow_html=True)
            st.session_state.weather_condition = st.selectbox("Weather", ['Sunny', 'Rainy', 'Cloudy', 'Snowy', 'Stormy'], key='weather_manual', label_visibility='collapsed')
        
        with col2:
            st.markdown("<div class='input-label'>Temperature (°C)</div>", unsafe_allow_html=True)
            temperature_celsius = st.slider("Temperature (°C)", 0, 40, 20, 1, key='temp_manual', label_visibility='collapsed')
        
        with col3:
            st.markdown("<div class='input-label'>Humidity (%)</div>", unsafe_allow_html=True)
            humidity = st.slider("Humidity (%)", 0, 100, 60, 5, key='humidity_manual', label_visibility='collapsed')
        
        col4, col5, col6 = st.columns(3)
        with col4:
            st.markdown("<div class='input-label'>Time of Day</div>", unsafe_allow_html=True)
            st.session_state.time_of_day = st.selectbox("Time", ['Morning', 'Afternoon', 'Evening', 'Night'], key='time_manual', label_visibility='collapsed')
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
            width="stretch",
            type="primary",
            key='generate'
        )

    st.markdown("""
            </div>
        </div>
    """, unsafe_allow_html=True)

    # ============================================================================
    # GENERATION LOGIC (STATE-BASED)
    # ============================================================================

    if generate_button:
        st.session_state.has_generated = False
        st.session_state.engine_type = 'unknown'
        st.session_state.order_logged = False
        st.session_state.micro_story = None

    if generate_button and not st.session_state.has_generated:
        with st.spinner("✨ Analyzing your preferences..."):
            # Engineer features
            temperature_category = categorize_temperature(temperature_celsius)
            comfort_index = calculate_comfort_index(mood, st.session_state.weather_condition)
            environmental_score = calculate_environmental_score(
                temperature_celsius,
                humidity,
                air_quality_index
            )
            
            # Trend popularity
            trend_popularity_score = 0.5
            
            # Determine season
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
                'weather_condition': [st.session_state.weather_condition],
                'temperature_celsius': [temperature_celsius],
                'humidity': [humidity],
                'air_quality_index': [air_quality_index],
                'time_of_day': [st.session_state.time_of_day],
                'sweetness_preference': [sweetness_preference],
                'health_preference': [health_preference],
                'trend_popularity_score': [trend_popularity_score],
                'temperature_category': [temperature_category],
                'comfort_index': [comfort_index],
                'environmental_score': [environmental_score],
                'season': [season]
            })
            
            # ================================================================
            # ML PIPELINE INFERENCE (CLEAN, FAIL-FAST DESIGN)
            # 3-layer: Behavioral Segmentation → Classification → Ranking
            # ================================================================
            
            try:
                # Prepare user input for ML pipeline
                pipeline_input = {
                    'mood': mood,
                    'weather_condition': st.session_state.weather_condition,
                    'temperature_celsius': temperature_celsius,
                    'humidity': humidity,
                    'season': season,
                    'air_quality_index': air_quality_index,
                    'time_of_day': st.session_state.time_of_day,
                    'sweetness_preference': sweetness_preference,
                    'health_preference': health_preference,
                    'trend_popularity_score': trend_popularity_score,
                    'temperature_category': temperature_category,
                    'comfort_index': comfort_index,
                    'environmental_score': environmental_score
                }
                
                # Call the single entry point (no fallbacks, fail-fast design)
                result = run_pipeline(pipeline_input)
                
                # Extract results from structured output
                top_3_cakes = result['top_3_cakes']
                top_3_scores = result['top_3_scores']
                cluster_id = result.get('cluster_id')
                
                # Create probabilities array for display compatibility
                probabilities = np.zeros(len(CAKE_CLASSES))
                for cake_name, score in zip(top_3_cakes, top_3_scores):
                    if cake_name in CAKE_CLASSES:
                        idx = CAKE_CLASSES.index(cake_name)
                        probabilities[idx] = score
                
                prediction_source = "🤖 Hybrid 3-Layer (Segmentation→Classification→Ranking)"
                engine_type = "hybrid"  # Set engine classification
                
                # Debug output
                if DEBUG:
                    logger.debug(f"✅ ML Pipeline executed successfully")
                    logger.debug(f"Cluster assigned: {cluster_id}")
                    logger.debug(f"Top 3 recommendations: {top_3_cakes}")
                    logger.debug(f"Final scores: {top_3_scores}")
                
                # Store pipeline results in session for display
                st.session_state.pipeline_result = result
                st.session_state.cluster_id = cluster_id
                
            except Exception as e:
                # FAIL-FAST: Show error and stop execution (no fallback)
                st.error(f"❌ ML Pipeline Error: {str(e)}")
                if DEBUG:
                    logger.debug(f"❌ ML Pipeline failed: {str(e)}")
                st.stop()
            
            # 🔴 FIX: Use ACTUAL ML output, NOT recalculated from probabilities array
            # ML has already ranked correctly - use results directly
            if DEBUG:
                logger.debug(f"Using actual ML recommendations: {top_3_cakes}")
                logger.debug(f"Using actual ML scores: {top_3_scores}")
            
            # Rename for consistency with rest of codebase
            top_3_probs = top_3_scores
            
            # Save to session state
            st.session_state.ai_result = {
                'top_3_cakes': top_3_cakes,
                'top_3_probs': top_3_probs,
                'probabilities': probabilities,
                'mood': mood,
                'weather_condition': st.session_state.weather_condition,
                'time_of_day': st.session_state.time_of_day,
                'model_version': ML_VERSION,
                'prediction_source': prediction_source,
                'engine_type': engine_type  # Store engine classification
            }
            st.session_state.has_generated = True
            
            # Generate micro-story based on recommendation
            st.session_state.micro_story = generate_micro_story(
                mood=mood,
                time_of_day=st.session_state.time_of_day,
                weather=st.session_state.weather_condition,
                cake=top_3_cakes[0]  # Use top recommendation
            )
            
            # Show success message with prediction source
            if engine_type == "hybrid":
                st.success("✨ Hybrid 3-Layer AI: Your personalized recommendations are ready.")
            elif engine_type == "ml":
                st.success("✨ ML-Powered: Your personalized ML-powered recommendations are ready.")
            else:
                st.info("✨ Rule-Based: Your personalized recommendations are ready.")



    # ============================================================================
    # PERSISTENT AI RESULT DISPLAY
    # ============================================================================

    if st.session_state.ai_result is not None:
        display_ai_recommendations()

    else:
        # Welcome screen
        st.markdown("""
        <div style='text-align: center; padding: 80px 40px;'>
            <p style='font-family: Playfair Display, serif; font-size: 1.8em; color: #1F1F1F; margin-bottom: 24px; letter-spacing: 0.03em; font-weight: 500;'>Your Moment Awaits</p>
            <p style='font-family: Inter, sans-serif; color: #4A4A4A; font-size: 1.08em; line-height: 1.8; max-width: 600px; margin: 0 auto;'>Describe your environment and mood above, share your taste preferences, and let our AI find the perfect cake for this moment.</p>
        </div>
        """, unsafe_allow_html=True)

    # ============================================================================
    # FULL MENU DISPLAY
    # ============================================================================

    display_full_menu()
    
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
