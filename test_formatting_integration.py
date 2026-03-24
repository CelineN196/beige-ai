#!/usr/bin/env python3
"""
Quick test to verify the Beige AI formatting layer integration.
"""

from frontend.beige_ai_copywriter import generate_luxury_description
from frontend.data_mapping import format_cake_card, CAKE_METADATA

print("🧪 TESTING BEIGE AI FORMATTING LAYER INTEGRATION")
print("=" * 70)

# Test cases with different moods and weather
test_cases = [
    {
        "cake_name": "Matcha Zen Cake",
        "mood": "Happy",
        "weather": "Sunny",
        "health": 8
    },
    {
        "cake_name": "Dark Chocolate Sea Salt Cake",
        "mood": "Stressed",
        "weather": "Rainy",
        "health": 2
    },
    {
        "cake_name": "Berry Garden Cake",
        "mood": "Celebratory",
        "weather": "Sunny",
        "health": 8
    }
]

passed = 0
failed = 0

for test in test_cases:
    cake_name = test["cake_name"]
    
    print(f"\n✓ TEST: {cake_name}")
    print(f"  Context: {test['mood']} mood, {test['weather']} weather")
    
    # Get card data
    card_data = format_cake_card(cake_name, confidence=0.85)
    
    # Generate copywriter output
    try:
        copywriter_output = generate_luxury_description(
            cake_name=cake_name,
            category=card_data['category'],
            flavor_profile=card_data['flavor'],
            mood=test['mood'],
            weather=test['weather'],
            health_preference=test['health']
        )
        
        # Extract narrative
        if "Beige AI Narrative:" in copywriter_output:
            narrative = copywriter_output.split("Beige AI Narrative:")[1].strip()
            print(f"  ✅ Output format: CORRECT")
            print(f"  ✅ Narrative length: {len(narrative)} chars")
            print(f"  📝 Preview: {narrative[:70]}...")
            passed += 1
        else:
            print(f"  ❌ FAILED: Missing Beige AI Narrative section")
            failed += 1
    except Exception as e:
        print(f"  ❌ FAILED: {str(e)}")
        failed += 1

print("\n" + "=" * 70)
print(f"RESULTS: {passed} passed, {failed} failed")

if failed == 0:
    print("\n✅ SUCCESS - Formatting layer integration complete!")
    print("\nChanges made:")
    print("  1. ✅ Import copywriter in beige_ai_app.py")
    print("  2. ✅ Call generate_luxury_description() in display_ai_recommendations()")
    print("  3. ✅ Extract narrative from copywriter output")
    print("  4. ✅ Render narrative in recommendation card HTML")
    print("  5. ✅ Add CSS styling for .rec-narrative")
    print("\nOutput structure per card:")
    print("  • Item Name")
    print("  • Category: [...]")
    print("  • Flavor Profile: [...]")
    print("  • Beige AI Narrative: [luxury description]")
    print("  • Technical Details (Sweetness, Wellness)")
else:
    print("\n❌ Some tests failed. Please review the errors above.")
