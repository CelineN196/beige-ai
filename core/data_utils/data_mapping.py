"""
Data Mapping & Metadata Layer
======================================================
Centralized metadata, normalization, and explainability logic
for the Beige AI ML recommendation system.

This module provides:
- Normalized cake metadata lookup (no "N/A" values)
- ML confidence handling
- Context-aware explanations
- Safe fallbacks for missing data
"""

import numpy as np


# ============================================================================
# ENHANCED CAKE METADATA (Comprehensive descriptions)
# ============================================================================

CAKE_METADATA = {
    "Dark Chocolate Sea Salt Cake": {
        "category": "Indulgent",
        "flavor_profile": "Rich & Savory",
        "sweetness_level": 8,
        "health_score": 2,
        "description": "A decadent dark chocolate cake with sea salt finishing. Perfect for those seeking rich, complex flavors that balance sweetness with subtle salt undertones.",
        "mood_pairing": ["stressed", "contemplative", "indulgent"],
        "weather_pairing": ["cold", "rainy"],
        "time_pairing": ["evening", "night"]
    },
    "Matcha Zen Cake": {
        "category": "Energizing",
        "flavor_profile": "Herbaceous & Earthy",
        "sweetness_level": 6,
        "health_score": 8,
        "description": "A delicate matcha-infused cake with light, zen-like qualities. An ideal choice for clarity of mind and sustained energy throughout the day.",
        "mood_pairing": ["energetic", "focused", "calm"],
        "weather_pairing": ["sunny", "warm"],
        "time_pairing": ["morning", "afternoon"]
    },
    "Citrus Cloud Cake": {
        "category": "Refreshing",
        "flavor_profile": "Bright & Tangy",
        "sweetness_level": 7,
        "health_score": 7,
        "description": "Light, airy citrus layers with bright lemon and orange notes. A refreshing choice that uplifts mood and energizes the palate.",
        "mood_pairing": ["happy", "cheerful", "energetic"],
        "weather_pairing": ["hot", "sunny"],
        "time_pairing": ["afternoon", "morning"]
    },
    "Berry Garden Cake": {
        "category": "Fruity",
        "flavor_profile": "Fresh & Vibrant",
        "sweetness_level": 7,
        "health_score": 8,
        "description": "Layers of fresh berries (strawberry, blueberry, raspberry) with light sponge. Vibrant, natural flavors perfect for a wholesome moment.",
        "mood_pairing": ["happy", "playful", "social"],
        "weather_pairing": ["sunny", "warm"],
        "time_pairing": ["afternoon", "morning"]
    },
    "Silk Cheesecake": {
        "category": "Indulgent",
        "flavor_profile": "Creamy & Rich",
        "sweetness_level": 9,
        "health_score": 3,
        "description": "Ultra-smooth, velvety cheesecake with a delicate crust. An indulgent luxury for when you deserve to treat yourself.",
        "mood_pairing": ["celebratory", "happy", "indulgent"],
        "weather_pairing": ["cold", "warm"],
        "time_pairing": ["evening", "night"]
    },
    "Earthy Wellness Cake": {
        "category": "Health-Conscious",
        "flavor_profile": "Nutty & Wholesome",
        "sweetness_level": 4,
        "health_score": 9,
        "description": "A nutrient-rich cake made with whole grains, nuts, and minimal refined sugar. For those prioritizing wellness without sacrificing taste.",
        "mood_pairing": ["calm", "focused", "health-conscious"],
        "weather_pairing": ["any"],
        "time_pairing": ["morning", "afternoon"]
    },
    "Café Tiramisu": {
        "category": "Energizing",
        "flavor_profile": "Coffee & Cocoa",
        "sweetness_level": 7,
        "health_score": 5,
        "description": "A classic Italian dessert combining espresso, mascarpone cream, and cocoa. Perfect for a moment of warmth and comfort.",
        "mood_pairing": ["tired", "cold", "contemplative"],
        "weather_pairing": ["cold", "rainy"],
        "time_pairing": ["evening", "afternoon"]
    },
    "Korean Sesame Mini Bread": {
        "category": "Savory",
        "flavor_profile": "Nutty & Light",
        "sweetness_level": 2,
        "health_score": 6,
        "description": "A delicate Korean-inspired pastry with subtle sesame notes. Perfect for those seeking something light and savory over sweet.",
        "mood_pairing": ["calm", "focused"],
        "weather_pairing": ["warm", "sunny"],
        "time_pairing": ["morning", "afternoon"]
    },
    "Chocolate Cake": {
        "category": "Indulgent",
        "flavor_profile": "Rich & Decadent",
        "sweetness_level": 8,
        "health_score": 2,
        "description": "A classic, timeless chocolate cake. Rich, comforting, and universally beloved—perfect for any occasion.",
        "mood_pairing": ["happy", "indulgent", "celebratory"],
        "weather_pairing": ["cold", "any"],
        "time_pairing": ["afternoon", "evening"]
    },
    "Vanilla Cake": {
        "category": "Classic",
        "flavor_profile": "Smooth & Versatile",
        "sweetness_level": 7,
        "health_score": 5,
        "description": "A timeless, elegant vanilla cake with subtle vanilla bean notes. Versatile and universally appreciated.",
        "mood_pairing": ["calm", "social", "happy"],
        "weather_pairing": ["any"],
        "time_pairing": ["any"]
    },
    "Lemon Cake": {
        "category": "Refreshing",
        "flavor_profile": "Bright & Citrus",
        "sweetness_level": 6,
        "health_score": 7,
        "description": "Zesty lemon with a moist crumb. Perfect for lifting mood with bright, uplifting citrus flavors.",
        "mood_pairing": ["happy", "energetic"],
        "weather_pairing": ["hot", "sunny"],
        "time_pairing": ["afternoon", "morning"]
    },
    "Strawberry Cheesecake": {
        "category": "Fruity",
        "flavor_profile": "Creamy & Fresh",
        "sweetness_level": 8,
        "health_score": 4,
        "description": "Creamy cheesecake topped with fresh strawberries. A perfect balance of indulgence and freshness.",
        "mood_pairing": ["happy", "celebratory", "romantic"],
        "weather_pairing": ["warm", "any"],
        "time_pairing": ["evening", "afternoon"]
    },
    "Carrot Cake": {
        "category": "Health-Conscious",
        "flavor_profile": "Warm & Spiced",
        "sweetness_level": 6,
        "health_score": 8,
        "description": "A wholesome, nutrient-rich cake with warm spices and caramelized vegetables. For health-minded indulgence.",
        "mood_pairing": ["calm", "cozy", "health-conscious"],
        "weather_pairing": ["cold", "rainy"],
        "time_pairing": ["afternoon", "morning"]
    },
    "Black Forest Cake": {
        "category": "Indulgent",
        "flavor_profile": "Rich & Elegant",
        "sweetness_level": 8,
        "health_score": 2,
        "description": "Layers of chocolate sponge, cherries, and whipped cream. An elegant, sophisticated choice for special moments.",
        "mood_pairing": ["celebratory", "romantic", "special"],
        "weather_pairing": ["cold", "any"],
        "time_pairing": ["evening", "night"]
    },
    "Tiramisu Cake": {
        "category": "Energizing",
        "flavor_profile": "Coffee & Cocoa",
        "sweetness_level": 7,
        "health_score": 5,
        "description": "Classic Italian tiramisu transformed into cake form. Coffee-driven with layers of mascarpone and cocoa.",
        "mood_pairing": ["tired", "cold", "contemplative", "focused"],
        "weather_pairing": ["cold", "rainy"],
        "time_pairing": ["afternoon", "evening"]
    },
    "Red Velvet Cake": {
        "category": "Elegant",
        "flavor_profile": "Velvety & Subtle",
        "sweetness_level": 7,
        "health_score": 3,
        "description": "A classic with deep red color, subtle cocoa notes, and cream cheese frosting. Elegant and sophisticated.",
        "mood_pairing": ["celebratory", "romantic", "special"],
        "weather_pairing": ["any"],
        "time_pairing": ["evening", "special occasion"]
    }
}


# ============================================================================
# NORMALIZATION LAYER
# ============================================================================

def _normalize_name(name: str) -> str:
    """
    Normalize cake name for case-insensitive, whitespace-safe lookup.
    
    Handles:
    - Case conversion to lowercase
    - Whitespace trimming
    - Underscore to space conversion (e.g., dark_chocolate_cake -> dark chocolate cake)
    - Multiple spaces to single space
    """
    # Replace underscores with spaces
    name = name.replace('_', ' ')
    # Strip leading/trailing whitespace
    name = name.strip()
    # Convert to lowercase
    name = name.lower()
    # Normalize multiple spaces to single space
    name = ' '.join(name.split())
    return name


# Build normalized lookup map
_normalized_metadata = {
    _normalize_name(k): v for k, v in CAKE_METADATA.items()
}


# ============================================================================
# SAFE METADATA LOOKUP
# ============================================================================

def get_cake_metadata(cake_name: str) -> dict:
    """
    Get complete cake metadata with robust fallback handling.
    
    Returns dict with keys:
    - category: str
    - flavor_profile: str
    - sweetness_level: int (1-10)
    - health_score: int (1-10)
    - description: str
    - mood_pairing: list[str]
    - weather_pairing: list[str]
    - time_pairing: list[str]
    
    All fields guaranteed to be present and non-null.
    """
    normalized_key = _normalize_name(cake_name)
    
    if normalized_key in _normalized_metadata:
        return _normalized_metadata[normalized_key]
    
    # Safe fallback (silent)
    return {
        "category": "Signature",
        "flavor_profile": "Balanced",
        "sweetness_level": 5,
        "health_score": 5,
        "description": "A curated special recommendation from Beige AI.",
        "mood_pairing": ["any"],
        "weather_pairing": ["any"],
        "time_pairing": ["any"]
    }


# ============================================================================
# EXPLAINABILITY LAYER (CONTEXT-AWARE EXPLANATIONS)
# ============================================================================

def explain_recommendation(
    cake_name: str,
    mood: str,
    weather: str,
    time_of_day: str,
    confidence: float,
    debug: bool = False
) -> str:
    """
    Generate a DYNAMIC, time-aware explanation for why this cake was recommended.
    
    CRITICAL: This function now creates UNIQUE narratives per cake based on:
    - Item-specific properties from metadata
    - Actual current time (not hardcoded)
    - Mood + weather context
    
    Args:
        cake_name: Name of the recommended cake
        mood: Current mood (happy, stressed, tired, etc.)
        weather: Current weather condition
        time_of_day: Current time of day (should be LIVE, not cached)
        confidence: ML confidence score (0-1)
        debug: If True, print time detection info
    
    Returns:
        Natural language explanation (UNIQUE per cake + time)
    """
    from datetime import datetime
    
    # Get ACTUAL current time for validation
    actual_hour = datetime.now().hour
    
    # Determine actual time period (NOT from session state)
    if 5 <= actual_hour < 12:
        actual_time_period = 'morning'
    elif 12 <= actual_hour < 17:
        actual_time_period = 'afternoon'
    elif 17 <= actual_hour <= 20:
        actual_time_period = 'evening'
    else:
        actual_time_period = 'night'
    
    # DEBUG: Log detected vs expected time
    if debug:
        # Time period validation (silent mode)
    
    # Use ACTUAL time, not session state
    time_period = actual_time_period
    
    metadata = get_cake_metadata(cake_name)
    explanations = []
    
    # ========================================================================
    # MOOD-BASED EXPLANATION (Item-specific + mood)
    # ========================================================================
    mood_lower = mood.lower()
    if mood_lower in metadata.get("mood_pairing", []):
        # Create unique mood narrative based on cake properties
        flavor = metadata.get("flavor_profile", "balanced").lower()
        if mood_lower == "stressed" or mood_lower == "tired":
            explanations.append(
                f"Perfect for your {mood_lower} state—this {flavor} composition "
                f"in {cake_name} provides comfort and grounding."
            )
        elif mood_lower == "happy" or mood_lower == "celebratory":
            explanations.append(
                f"Celebrates your {mood_lower} mood—{cake_name}'s {flavor} profile "
                f"elevates the moment with joy."
            )
        elif mood_lower == "energetic" or mood_lower == "focused":
            explanations.append(
                f"Matches your {mood_lower} energy—{cake_name} sustains "
                f"focus and vitality through its crafted composition."
            )
        elif mood_lower == "calm" or mood_lower == "contemplative":
            explanations.append(
                f"Complements your {mood_lower} state—the {flavor} notes "
                f"in {cake_name} deepen introspection."
            )
    
    # ========================================================================
    # WEATHER-BASED EXPLANATION (Item-specific + weather)
    # ========================================================================
    weather_lower = weather.lower()
    if weather_lower in metadata.get("weather_pairing", []) or "any" in metadata.get("weather_pairing", []):
        category = metadata.get("category", "dessert")
        if weather_lower == "cold" or weather_lower == "rainy":
            explanations.append(
                f"Perfect for the {weather_lower} weather right now—"
                f"{cake_name}'s warm, {category.lower()} character brings comfort."
            )
        elif weather_lower == "hot" or weather_lower == "sunny":
            explanations.append(
                f"Ideal for the {weather_lower} conditions—"
                f"{cake_name} offers a refreshing contrast with its balanced indulgence."
            )
    
    # ========================================================================
    # TIME-BASED EXPLANATION (Dynamic based on ACTUAL current time)
    # ========================================================================
    if time_period in metadata.get("time_pairing", []) or "any" in metadata.get("time_pairing", []):
        category = metadata.get("category", "indulgence")
        texture = metadata.get("texture", "exquisite")
        
        # Create UNIQUE narratives per time period using cake-specific details
        if time_period == "morning":
            explanations.append(
                f"RIGHT NOW (morning)—{cake_name} awakens the senses with "
                f"its {texture} {category.lower()}, perfect for starting your day."
            )
        elif time_period == "afternoon":
            explanations.append(
                f"RIGHT NOW (afternoon)—{cake_name} provides the ideal indulgence "
                f"for this perfect moment, a {texture} pause in your day."
            )
        elif time_period == "evening":
            explanations.append(
                f"RIGHT NOW (evening)—{cake_name} offers warmth and comfort, "
                f"its {texture} composition suited to a reflective close to your day."
            )
        elif time_period == "night":
            explanations.append(
                f"RIGHT NOW (night)—{cake_name} provides ritual and deep satisfaction, "
                f"its {texture} character perfect for quieter moments."
            )
    
    # ========================================================================
    # FALLBACK: Item-specific generic explanation
    # ========================================================================
    if not explanations:
        category = metadata.get("category", "Signature")
        flavor = metadata.get("flavor_profile", "Balanced")
        explanations.append(
            f"{cake_name}—a {category.lower()} choice with {flavor.lower()} notes—"
            f"matches your {time_period} context perfectly."
        )
    
    # ========================================================================
    # CONFIDENCE STATEMENT
    # ========================================================================
    if confidence >= 0.8:
        confidence_text = "Our AI is highly confident in this recommendation."
    elif confidence >= 0.6:
        confidence_text = "Our AI is moderately confident in this recommendation."
    else:
        confidence_text = "This recommendation is worth exploring."
    
    explanation = " ".join(explanations) + f" {confidence_text}"
    return explanation


# ============================================================================
# DISPLAY-READY METADATA
# ============================================================================

def format_cake_card(
    cake_name: str,
    confidence: float = None,
    rank: str = None
) -> dict:
    """
    Format cake metadata for display in the UI.
    
    Returns dict with keys ready for template rendering:
    - name: str
    - category: str
    - flavor: str
    - description: str
    - confidence_pct: str (e.g., "78%")
    - sweetness: int
    - health: int
    - rank: str (e.g., "I", "II", "III")
    """
    metadata = get_cake_metadata(cake_name)
    
    return {
        "name": cake_name,
        "category": metadata.get("category", "Signature"),
        "flavor": metadata.get("flavor_profile", "Balanced"),
        "description": metadata.get("description", ""),
        "confidence_pct": f"{confidence*100:.0f}%" if confidence is not None else "N/A",
        "confidence_decimal": confidence,
        "sweetness": metadata.get("sweetness_level", 5),
        "health": metadata.get("health_score", 5),
        "rank": rank or ""
    }


# ============================================================================
# METADATA VALIDATION
# ============================================================================

def validate_metadata() -> tuple:
    """
    Validate metadata integrity.
    
    Returns: (is_valid: bool, missing_cakes: list)
    """
    missing = [cake for cake in CAKE_METADATA if not all([
        CAKE_METADATA[cake].get("category"),
        CAKE_METADATA[cake].get("flavor_profile"),
        CAKE_METADATA[cake].get("description"),
    ])]
    
    return len(missing) == 0, missing


# Validate on import
_is_valid, _missing = validate_metadata()
if not _is_valid:
    # Validation check (silent mode)
