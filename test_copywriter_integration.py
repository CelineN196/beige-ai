"""
Copywriter Integration Test
====================================================
Demonstrates how to use the Beige AI Copywriter Engine
with the hybrid recommendation system.
"""

from frontend.beige_ai_copywriter import BeigeAICopywriter, generate_luxury_description
from frontend.data_mapping import CAKE_METADATA


def test_copywriter_with_metadata():
    """
    Test copywriter with actual cake metadata from data_mapping.py
    """
    
    print("=" * 80)
    print("COPYWRITER INTEGRATION TEST")
    print("=" * 80)
    print()
    
    copywriter = BeigeAICopywriter()
    
    # First, verify metadata is loading
    print("[DEBUG] Checking CAKE_METADATA availability...")
    print(f"  Available cakes: {list(CAKE_METADATA.keys())[:3]}...")
    print(f"  Total cakes: {len(CAKE_METADATA)}")
    print()
    
    # Example 1: Use copywriter with hybrid system output
    print("[EXAMPLE 1] Matcha Zen Cake - Happy + Sunny")
    print("-" * 80)
    
    # This would come from hybrid system inference
    recommendation_context = {
        'cake_name': 'Matcha Zen Cake',
        'mood': 'Happy',
        'weather': 'Sunny',
        'health_preference': 8,
        'time_of_day': 'Afternoon'
    }
    
    # Get metadata from data_mapping
    cake_data = CAKE_METADATA.get('Matcha Zen Cake', {})
    
    # Generate luxury description
    if cake_data and cake_data.get('flavor_profile'):
        print(f"  Cake: {cake_data.get('name', 'Matcha Zen Cake')}")
        print(f"  Category: {cake_data.get('category')}")
        print(f"  Flavor Profile: {cake_data.get('flavor_profile')}")
        print()
        
        description = copywriter.generate(
            cake_name=cake_data.get('name', 'Matcha Zen Cake'),
            category=cake_data.get('category'),
            flavor_profile=cake_data.get('flavor_profile'),
            mood=recommendation_context.get('mood'),
            weather=recommendation_context.get('weather'),
            time_of_day=recommendation_context.get('time_of_day'),
            health_preference=recommendation_context.get('health_preference')
        )
        print(description)
    else:
        print(f"  ERROR: Cake data not found. Found: {cake_data}")
    print()
    
    # Example 2: Dark Chocolate for Stressed + Rainy
    print("[EXAMPLE 2] Dark Chocolate Sea Salt Cake - Stressed + Rainy")
    print("-" * 80)
    
    recommendation_context = {
        'cake_name': 'Dark Chocolate Sea Salt Cake',
        'mood': 'Stressed',
        'weather': 'Rainy',
        'health_preference': 3,
        'time_of_day': 'Evening'
    }
    
    cake_data = CAKE_METADATA.get('Dark Chocolate Sea Salt Cake', {})
    
    if cake_data and cake_data.get('flavor_profile'):
        print(f"  Cake: {cake_data.get('name', 'Dark Chocolate Sea Salt Cake')}")
        print(f"  Category: {cake_data.get('category')}")
        print(f"  Flavor Profile: {cake_data.get('flavor_profile')}")
        print()
        
        description = copywriter.generate(
            cake_name=cake_data.get('name', 'Dark Chocolate Sea Salt Cake'),
            category=cake_data.get('category'),
            flavor_profile=cake_data.get('flavor_profile'),
            mood=recommendation_context.get('mood'),
            weather=recommendation_context.get('weather'),
            time_of_day=recommendation_context.get('time_of_day'),
            health_preference=recommendation_context.get('health_preference')
        )
        print(description)
    else:
        print(f"  ERROR: Cake data not found")
    print()
    
    # Example 3: Using convenience function with all cake types
    print("[EXAMPLE 3] Sample all cakes with Happy mood")
    print("-" * 80)
    
    sample_cakes = [
        'Matcha Zen Cake',
        'Dark Chocolate Sea Salt Cake',
        'Café Tiramisu',
        'Earthy Wellness Cake',
        'Berry Garden Cake'
    ]
    
    for cake_name in sample_cakes:
        if cake_name in CAKE_METADATA:
            cake_data = CAKE_METADATA[cake_name]
            description = generate_luxury_description(
                cake_name=cake_name,  # Use the key itself, not cake_data['name']
                category=cake_data.get('category'),
                flavor_profile=cake_data.get('flavor_profile'),
                mood='Happy',
                weather='Sunny',
                health_preference=6
            )
            print(f"\n{cake_name}:")
            # Extract just the narrative line
            lines = description.split('\n')
            narrative_start = [i for i, line in enumerate(lines) if 'Beige AI Narrative:' in line]
            if narrative_start:
                narrative = lines[narrative_start[0] + 1].strip()
                print(f"→ {narrative[:100]}...")
            else:
                print(f"→ {description[:100]}...")
    
    print()
    print("=" * 80)
    print("✅ INTEGRATION TEST COMPLETE")
    print("=" * 80)
    print()
    print("Usage Tips:")
    print("1. Import: from frontend.beige_ai_copywriter import generate_luxury_description")
    print("2. Use with hybrid system: Get cake metadata, pass to copywriter")
    print("3. Include mood/weather for contextual narratives")
    print("4. All descriptions automatically styled for luxury presentation")


if __name__ == "__main__":
    test_copywriter_with_metadata()
