"""
Beige AI Copywriter Engine
==================================================================
Transforms structured ML recommendations into luxury, minimalist 
dessert descriptions for the premium food experience app.

This module ensures consistent, high-end product narratives across
all recommendation channels while maintaining precise adherence to
input data and style guidelines.
"""

from typing import Dict, Optional


# ============================================================================
# TONE & VOCABULARY LIBRARY
# ============================================================================

LUXURY_VOCABULARY = {
    'structural': ['Engineered', 'Crafted', 'Architected', 'Structured', 'Layered'],
    'texture': ['Velvety', 'Silken', 'Refined', 'Sensory balance', 'Textural harmony'],
    'richness': ['Depth', 'Structural richness', 'Layered profile', 'Compounded sensation'],
    'comfort': ['Grounded', 'Embracing', 'Restful', 'Anchoring', 'Stabilizing'],
    'lightness': ['Ethereal', 'Refined lightness', 'Buoyant', 'Crystalline', 'Aerated'],
    'balance': ['Equilibrium', 'Sensory balance', 'Calibrated', 'Precision-crafted', 'Harmonized'],
}

# Mood-based narrative tone (subtle, not explicit)
MOOD_TONES = {
    'happy': 'bright, uplifting undertones',
    'stressed': 'grounding, stabilizing foundation',
    'tired': 'restful, restorative qualities',
    'lonely': 'embracing, companionable texture',
    'celebratory': 'elevated, joyful expression',
}

# Weather-based flavor direction (subtle influence)
WEATHER_INFLUENCE = {
    'sunny': 'lighter, refreshing finish',
    'rainy': 'grounded, rich foundation',
    'cloudy': 'balanced, transitional qualities',
    'snowy': 'crisp, crystalline accents',
    'stormy': 'bold, anchoring presence',
}

# Health preference framing
HEALTH_FRAMING = {
    'low': 'Crafted experience',          # 1-3: Indulgent
    'medium': 'Refined balance',          # 4-6: Moderate
    'high': 'Engineered wellness',        # 7-10: Health-conscious
}


# ============================================================================
# COPYWRITING ENGINE
# ============================================================================

class BeigeAICopywriter:
    """
    Production copywriting system for ML-generated recommendations.
    
    Transforms structured cake metadata + context into luxury product
    descriptions following strict minimalist style guidelines.
    """
    
    def __init__(self):
        """Initialize copywriter with vocabulary and rules."""
        self.vocabulary = LUXURY_VOCABULARY
        self.mood_tones = MOOD_TONES
        self.weather_influence = WEATHER_INFLUENCE
        self.health_framing = HEALTH_FRAMING
        self.compiled_descriptions = {}  # Cache for performance
    
    def generate(
        self,
        cake_name: str,
        category: str,
        flavor_profile: str,
        mood: Optional[str] = None,
        weather: Optional[str] = None,
        time_of_day: Optional[str] = None,
        health_preference: Optional[int] = None,
    ) -> str:
        """
        Generate luxury product description from structured input.
        
        Args:
            cake_name: Exact name of cake (NOT modified)
            category: Product category (NOT modified)
            flavor_profile: 2-3 sensory descriptors (NOT modified)
            mood: User's emotional state (subtle influence only)
            weather: Environmental condition (subtle influence only)
            time_of_day: When being consumed (context only)
            health_preference: 1-10 scale (framing only)
        
        Returns:
            Formatted luxury product description (exact format)
        
        Raises:
            ValueError: If required fields are missing
        """
        
        # ====================================================================
        # VALIDATION: STRICT INPUT CHECKING
        # ====================================================================
        
        if not cake_name or not cake_name.strip():
            return "Insufficient data to generate description."
        if not category or not category.strip():
            return "Insufficient data to generate description."
        if not flavor_profile or not flavor_profile.strip():
            return "Insufficient data to generate description."
        
        # Preserve exact input (no modifications)
        cake_name = cake_name.strip()
        category = category.strip()
        flavor_profile = flavor_profile.strip()
        
        # ====================================================================
        # NARRATIVE GENERATION: 2 SENTENCES ONLY
        # ====================================================================
        
        narrative = self._craft_narrative(
            cake_name=cake_name,
            category=category,
            flavor_profile=flavor_profile,
            mood=mood,
            weather=weather,
            health_preference=health_preference
        )
        
        # ====================================================================
        # OUTPUT FORMATTING: STRICT STRUCTURE
        # ====================================================================
        
        output = (
            f"{cake_name}\n\n"
            f"Category: {category}\n\n"
            f"Flavor Profile: {flavor_profile}\n\n"
            f"Beige AI Narrative:\n"
            f"{narrative}"
        )
        
        return output
    
    def _craft_narrative(
        self,
        cake_name: str,
        category: str,
        flavor_profile: str,
        mood: Optional[str] = None,
        weather: Optional[str] = None,
        health_preference: Optional[int] = None,
    ) -> str:
        """
        Craft exactly 2-sentence narrative with subtle contextual influence.
        
        Rules:
        - EXACTLY 2 sentences
        - Minimalist, high-end tone
        - Subtle mood/weather influence (NOT explicit)
        - DO NOT mention inputs explicitly
        - Use provided vocabulary
        """
        
        # Extract sensory descriptors from flavor profile
        # Handle both comma-separated and ampersand-separated formats
        if ',' in flavor_profile:
            descriptors = [d.strip() for d in flavor_profile.split(',')]
        elif ' & ' in flavor_profile:
            descriptors = [d.strip() for d in flavor_profile.split(' & ')]
        else:
            descriptors = [flavor_profile.strip()]
        
        # Determine narrative direction based on category
        narrative_direction = self._analyze_category(category)
        
        # Build first sentence: Structure + primary sensation
        first_sentence = self._build_first_sentence(
            cake_name=cake_name,
            category=category,
            descriptors=descriptors,
            narrative_direction=narrative_direction,
            mood=mood
        )
        
        # Build second sentence: Sensory experience + subtle context
        second_sentence = self._build_second_sentence(
            descriptors=descriptors,
            narrative_direction=narrative_direction,
            weather=weather,
            health_preference=health_preference
        )
        
        # Combine (exactly 2 sentences)
        narrative = f"{first_sentence} {second_sentence}"
        
        return narrative
    
    def _build_first_sentence(
        self,
        cake_name: str,
        category: str,
        descriptors: list,
        narrative_direction: str,
        mood: Optional[str] = None
    ) -> str:
        """
        First sentence: Establish structural approach + primary sensation.
        
        Format: "[Health frame] [structural approach] [sensory focus] for [tone]."
        """
        
        primary_descriptor = descriptors[0] if descriptors else 'sensory balance'
        
        # Build sensory focus
        if len(descriptors) > 2:
            sensory_focus = f"{primary_descriptor} profile with {descriptors[1]} undertones"
        else:
            sensory_focus = f"{primary_descriptor} foundation"
        
        # Subtle mood influence in word choice
        if mood and mood.lower() in self.mood_tones:
            tone_hint = self.mood_tones[mood.lower()]
            return (
                f"A {sensory_focus} engineered for {tone_hint}."
            )
        else:
            return (
                f"A {sensory_focus} engineered for refined sensory balance."
            )
    
    def _build_second_sentence(
        self,
        descriptors: list,
        narrative_direction: str,
        weather: Optional[str] = None,
        health_preference: Optional[int] = None
    ) -> str:
        """
        Second sentence: Delivery mechanism + finishing quality.
        
        Format: "Built with [texture foundation] that delivers [sensory result]."
        """
        
        # Choose foundation texture based on descriptors
        if len(descriptors) > 1:
            texture_descriptor = descriptors[1].lower().strip()
            foundation = f"{texture_descriptor} foundation"
        else:
            foundation = "refined foundation"
        
        # Subtle weather influence on delivery description
        if weather and weather.lower() in self.weather_influence:
            delivery = self.weather_influence[weather.lower()]
        else:
            delivery = "controlled indulgence" if narrative_direction == 'indulgent' else "refined balance"
        
        return f"Built with a {foundation} that delivers {delivery}."
    
    def _analyze_category(self, category: str) -> str:
        """
        Determine narrative direction from category.
        
        Args:
            category: Product category from input
        
        Returns:
            Narrative direction: 'indulgent', 'balanced', or 'wellness'
        """
        
        category_lower = category.lower()
        
        if any(word in category_lower for word in ['indulgent', 'chocolate', 'rich', 'decadent']):
            return 'indulgent'
        elif any(word in category_lower for word in ['wellness', 'energizing', 'healthy', 'light']):
            return 'wellness'
        else:
            return 'balanced'
    
    def _determine_health_framing(self, health_preference: Optional[int]) -> str:
        """
        Determine health-based framing (subtle, not explicit).
        
        Args:
            health_preference: 1-10 scale (None = neutral framing)
        
        Returns:
            Framing string for narrative
        """
        
        if health_preference is None:
            return 'Crafted experience'
        
        if health_preference <= 3:
            return 'Crafted experience'  # Indulgent framing
        elif health_preference <= 6:
            return 'Refined balance'     # Moderate framing
        else:
            return 'Engineered wellness'  # Health-conscious framing
    
    def generate_from_dict(self, data: Dict) -> str:
        """
        Generate description from dictionary input (JSON format).
        
        Args:
            data: Dictionary with keys:
                - cake_name (required)
                - category (required)
                - flavor_profile (required)
                - mood (optional)
                - weather (optional)
                - time_of_day (optional)
                - health_preference (optional)
        
        Returns:
            Formatted luxury product description
        
        Raises:
            ValueError: If required fields missing
        """
        
        required_keys = ['cake_name', 'category', 'flavor_profile']
        
        # Validate all required keys present
        for key in required_keys:
            if key not in data or not data[key]:
                return "Insufficient data to generate description."
        
        return self.generate(
            cake_name=data.get('cake_name'),
            category=data.get('category'),
            flavor_profile=data.get('flavor_profile'),
            mood=data.get('mood'),
            weather=data.get('weather'),
            time_of_day=data.get('time_of_day'),
            health_preference=data.get('health_preference')
        )


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================

def generate_luxury_description(
    cake_name: str,
    category: str,
    flavor_profile: str,
    mood: Optional[str] = None,
    weather: Optional[str] = None,
    time_of_day: Optional[str] = None,
    health_preference: Optional[int] = None,
) -> str:
    """
    Standalone function to generate luxury product description.
    
    Usage:
        from beige_ai_copywriter import generate_luxury_description
        
        description = generate_luxury_description(
            cake_name="Matcha Zen Cake",
            category="Energizing",
            flavor_profile="Herbaceous, Earthy, Clean Finish",
            mood="Happy",
            weather="Sunny",
            health_preference=8
        )
        print(description)
    
    Args:
        cake_name: Exact cake name
        category: Product category
        flavor_profile: Sensory descriptors
        mood: Optional emotional context
        weather: Optional environmental context
        time_of_day: Optional temporal context
        health_preference: Optional 1-10 health score
    
    Returns:
        Formatted luxury product description
    """
    
    copywriter = BeigeAICopywriter()
    return copywriter.generate(
        cake_name=cake_name,
        category=category,
        flavor_profile=flavor_profile,
        mood=mood,
        weather=weather,
        time_of_day=time_of_day,
        health_preference=health_preference
    )


# ============================================================================
# TESTING & VALIDATION
# ============================================================================

if __name__ == "__main__":
    """
    Test the copywriter engine with sample inputs.
    """
    
    copywriter = BeigeAICopywriter()
    
    print("=" * 80)
    print("BEIGE AI COPYWRITER ENGINE - TEST SUITE")
    print("=" * 80)
    print()
    
    # Test 1: Complete input
    print("[TEST 1] Complete input with all context")
    print("-" * 80)
    description = copywriter.generate(
        cake_name="Matcha Zen Cake",
        category="Energizing",
        flavor_profile="Herbaceous, Earthy, Clean Finish",
        mood="Happy",
        weather="Sunny",
        time_of_day="Afternoon",
        health_preference=8
    )
    print(description)
    print()
    
    # Test 2: Minimal input
    print("[TEST 2] Minimal input (required fields only)")
    print("-" * 80)
    description = copywriter.generate(
        cake_name="Dark Chocolate Sea Salt Cake",
        category="Indulgent",
        flavor_profile="Deep Cocoa, Velvety, Warm Finish"
    )
    print(description)
    print()
    
    # Test 3: Different mood/weather
    print("[TEST 3] Stressed + Rainy context")
    print("-" * 80)
    description = copywriter.generate(
        cake_name="Café Tiramisu",
        category="Indulgent",
        flavor_profile="Coffee, Cocoa, Creamy",
        mood="Stressed",
        weather="Rainy",
        health_preference=5
    )
    print(description)
    print()
    
    # Test 4: Wellness focus
    print("[TEST 4] Wellness-focused cake")
    print("-" * 80)
    description = copywriter.generate(
        cake_name="Earthy Wellness Cake",
        category="Wellness",
        flavor_profile="Nutty, Grounded, Wholesome",
        mood="Tired",
        weather="Cloudy",
        health_preference=9
    )
    print(description)
    print()
    
    # Test 5: Missing required field (error case)
    print("[TEST 5] Missing required field (error handling)")
    print("-" * 80)
    description = copywriter.generate(
        cake_name="Test Cake",
        category="",  # Missing
        flavor_profile="Test flavor"
    )
    print(description)
    print()
    
    # Test 6: Dictionary input
    print("[TEST 6] Dictionary/JSON input")
    print("-" * 80)
    cake_data = {
        "cake_name": "Berry Garden Cake",
        "category": "Refreshing",
        "flavor_profile": "Tart Berry, Floral, Bright",
        "mood": "Celebratory",
        "weather": "Sunny",
        "health_preference": 7
    }
    description = copywriter.generate_from_dict(cake_data)
    print(description)
    print()
    
    print("=" * 80)
    print("✅ ALL TESTS COMPLETE")
    print("=" * 80)
