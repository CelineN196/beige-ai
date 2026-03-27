"""
Beige.AI Menu Configuration
================================================================
Centralized configuration for the cake menu used across all modules.

This file contains the authoritative list of cake categories used in:
- Data generation (beige_ai_data_generation.py)
- Analytics (beige_ai_analytics.py)
- Classification models (Phase 3)
- Recommendation engines

Update this file to modify the cake menu across the entire project.
"""

# ============================================================================
# CAKE MENU - Beige.AI Product Catalog
# ============================================================================

CAKE_MENU = [
    "Dark Chocolate Sea Salt Cake",
    "Matcha Zen Cake",
    "Citrus Cloud Cake",
    "Berry Garden Cake",
    "Silk Cheesecake",
    "Earthy Wellness Cake",
    "Café Tiramisu",
    "Korean Sesame Mini Bread"
]

# ============================================================================
# CAKE MENU CATEGORIES (Optional: for future use)
# ============================================================================

CAKE_CATEGORIES = {
    "Dark Chocolate Sea Salt Cake": {
        "category": "Indulgent",
        "flavor_profile": "Rich & Savory",
        "sweetness_level": 8,
        "health_score": 2
    },
    "Matcha Zen Cake": {
        "category": "Energizing",
        "flavor_profile": "Herbaceous & Earthy",
        "sweetness_level": 6,
        "health_score": 8
    },
    "Citrus Cloud Cake": {
        "category": "Refreshing",
        "flavor_profile": "Bright & Tangy",
        "sweetness_level": 7,
        "health_score": 7
    },
    "Berry Garden Cake": {
        "category": "Fruity",
        "flavor_profile": "Fresh & Vibrant",
        "sweetness_level": 7,
        "health_score": 8
    },
    "Silk Cheesecake": {
        "category": "Indulgent",
        "flavor_profile": "Creamy & Rich",
        "sweetness_level": 9,
        "health_score": 3
    },
    "Earthy Wellness Cake": {
        "category": "Health-Conscious",
        "flavor_profile": "Nutty & Wholesome",
        "sweetness_level": 4,
        "health_score": 9
    },
    "Café Tiramisu": {
        "category": "Energizing",
        "flavor_profile": "Coffee & Cocoa",
        "sweetness_level": 7,
        "health_score": 5
    },
    "Korean Sesame Mini Bread": {
        "category": "Savory",
        "flavor_profile": "Nutty & Light",
        "sweetness_level": 2,
        "health_score": 6
    },
    # ===== Fallback cake metadata (for rule-based predictor) =====
    "Chocolate Cake": {
        "category": "Indulgent",
        "flavor_profile": "Rich & Decadent",
        "sweetness_level": 8,
        "health_score": 2
    },
    "Vanilla Cake": {
        "category": "Classic",
        "flavor_profile": "Smooth & Versatile",
        "sweetness_level": 7,
        "health_score": 5
    },
    "Lemon Cake": {
        "category": "Refreshing",
        "flavor_profile": "Bright & Citrus",
        "sweetness_level": 6,
        "health_score": 7
    },
    "Strawberry Cheesecake": {
        "category": "Fruity",
        "flavor_profile": "Creamy & Fresh",
        "sweetness_level": 8,
        "health_score": 4
    },
    "Carrot Cake": {
        "category": "Health-Conscious",
        "flavor_profile": "Warm & Spiced",
        "sweetness_level": 6,
        "health_score": 8
    },
    "Black Forest Cake": {
        "category": "Indulgent",
        "flavor_profile": "Rich & Elegant",
        "sweetness_level": 8,
        "health_score": 2
    },
    "Tiramisu Cake": {
        "category": "Energizing",
        "flavor_profile": "Coffee & Cocoa",
        "sweetness_level": 7,
        "health_score": 5
    },
    "Red Velvet Cake": {
        "category": "Elegant",
        "flavor_profile": "Velvety & Subtle",
        "sweetness_level": 7,
        "health_score": 3
    }
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_cake_menu():
    """
    Returns the list of available cake categories.
    
    Returns:
        list: List of cake names
    """
    return CAKE_MENU

def get_cake_count():
    """
    Returns the total number of cakes in the menu.
    
    Returns:
        int: Number of cakes
    """
    return len(CAKE_MENU)

def is_valid_cake(cake_name):
    """
    Checks if a given cake name is in the menu.
    
    Args:
        cake_name (str): Name of the cake to validate
        
    Returns:
        bool: True if cake is in menu, False otherwise
    """
    return cake_name in CAKE_MENU

def get_cake_properties(cake_name):
    """
    Returns the properties of a specific cake.
    
    Args:
        cake_name (str): Name of the cake
        
    Returns:
        dict: Properties of the cake, or None if not found
    """
    return CAKE_CATEGORIES.get(cake_name)

# ============================================================================
# COMPATIBILITY CHECKS
# ============================================================================

def validate_menu():
    """
    Validates that all cakes in CAKE_MENU have properties defined.
    
    Returns:
        tuple: (is_valid, missing_cakes)
    """
    missing_cakes = [cake for cake in CAKE_MENU if cake not in CAKE_CATEGORIES]
    return len(missing_cakes) == 0, missing_cakes

# Validate on import (silent mode - no console output)
_is_valid, _missing = validate_menu()
# Validation check runs silently for production

# ============================================================================
# NORMALIZED CAKE METADATA LOOKUP
# ============================================================================

def _normalize_name(name: str) -> str:
    """
    Normalize cake name for case-insensitive, whitespace-safe lookup.
    
    Handles:
    - Converts to lowercase
    - Strips leading/trailing whitespace
    - Collapses multiple spaces into single space
    - Handles tabs and other whitespace characters
    
    Args:
        name: Cake name to normalize
        
    Returns:
        Normalized name (lowercase, whitespace-collapsed)
    """
    # Strip and convert to lowercase
    name = name.strip().lower()
    # Collapse multiple whitespace characters into single space
    name = ' '.join(name.split())
    return name

# Build normalized lookup table (lazily cached)
_normalized_cake_data = None

def _build_normalized_cache():
    """Build normalized lookup table from CAKE_CATEGORIES."""
    global _normalized_cake_data
    if _normalized_cake_data is None:
        _normalized_cake_data = {
            _normalize_name(k): v for k, v in CAKE_CATEGORIES.items()
        }
    return _normalized_cake_data

def get_cake_info(cake_name: str) -> dict:
    """
    Get cake metadata with robust fallback.
    
    Handles:
    - Case differences (Chocolate vs CHOCOLATE vs ChOcOlAtE)
    - Extra whitespace (Chocolate Cake  vs Chocolate Cake)
    - Missing metadata (returns defaults)
    
    Args:
        cake_name: Name of the cake (any case, may have extra spaces)
        
    Returns:
        dict: Cake metadata with keys:
            - category: str (default: "Signature")
            - flavor_profile: str (default: "Balanced")
            - sweetness_level: int (default: 5)
            - health_score: int (default: 5)
            
    Example:
        >>> info = get_cake_info("chocolate cake")
        >>> print(info['category'])
        'Indulgent'
        >>> print(info['flavor_profile'])
        'Rich & Decadent'
    """
    # Normalize input
    normalized_key = _normalize_name(cake_name)
    
    # Build cache if needed
    cache = _build_normalized_cache()
    
    # Try direct lookup
    if normalized_key in cache:
        return cache[normalized_key]
    
    # Return safe defaults (no logging for production)
    return {
        "category": "Signature",
        "flavor_profile": "Balanced",
        "sweetness_level": 5,
        "health_score": 5
    }
