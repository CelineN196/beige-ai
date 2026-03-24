"""Quick verification that all imports work after changes."""
import sys

print("Verifying Beige AI app imports...")

try:
    from frontend.beige_ai_app import display_ai_recommendations
    print("✅ beige_ai_app imports successfully")
except Exception as e:
    print(f"❌ Error importing beige_ai_app: {e}")
    sys.exit(1)

try:
    from frontend.beige_ai_copywriter import generate_luxury_description
    print("✅ beige_ai_copywriter imports successfully")
except Exception as e:
    print(f"❌ Error importing beige_ai_copywriter: {e}")
    sys.exit(1)

try:
    from frontend.data_mapping import format_cake_card, CAKE_METADATA
    print("✅ data_mapping imports successfully")
except Exception as e:
    print(f"❌ Error importing data_mapping: {e}")
    sys.exit(1)

try:
    from frontend.hybrid_recommender import create_or_load_system
    print("✅ hybrid_recommender imports successfully")
except Exception as e:
    print(f"❌ Error importing hybrid_recommender: {e}")
    sys.exit(1)

print("\n🎉 All imports successful - App is ready to run!")
