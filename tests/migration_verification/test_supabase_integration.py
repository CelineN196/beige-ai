"""
COMPLETE MINIMAL EXAMPLE
Supabase feedback logging integration test script for Beige AI.
Tests recommendation logging, user feedback, and A/B experiments.
"""

import sys
sys.path.insert(0, '/Users/queenceline/Downloads/Beige AI')

from backend.integrations.supabase_logger import log_feedback, get_session_id
from backend.integrations.supabase_integration import log_recommendation
from datetime import datetime
import time


def test_basic_logging():
    """Test basic feedback logging with multiple use cases."""
    
    session_id = get_session_id()
    print(f"\n📊 Session ID: {session_id}\n")
    
    # ========================================================================
    # TEST CASE 1: Log a simple recommendation
    # ========================================================================
    print("1️⃣ Logging basic recommendation...")
    try:
        success = log_feedback(
            session_id=session_id,
            user_input={
                "mood": "happy",
                "sweetness_preference": 7,
                "health_preference": 5,
            },
            recommended_cake="Dark Chocolate Sea Salt Cake",
            context={
                "weather": "sunny",
                "mood": "happy",
                "time_of_day": "afternoon",
                "temperature": 25,
                "hour": 14,
            },
            latency_ms=250,
            confidence_score=0.85,
            cluster_id=1,
            ml_features={
                "cluster": 1,
                "mood": "happy",
                "sweetness": 7,
            },
        )
        if success:
            print("   ✅ Success - Recommendation logged to Supabase\n")
        else:
            print("   ⚠️ Failed - Check connection and credentials\n")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}\n")
    
    # ========================================================================
    # TEST CASE 2: Log with user feedback (rating)
    # ========================================================================
    print("2️⃣ Logging with user feedback...")
    try:
        success = log_feedback(
            session_id=session_id,
            user_input={
                "mood": "happy",
                "sweetness_preference": 7,
            },
            recommended_cake="Dark Chocolate Sea Salt Cake",
            context={
                "weather": "sunny",
                "time_of_day": "afternoon",
            },
            user_feedback=5,
            feedback_notes="Loved the recommendation!",
        )
        if success:
            print("   ✅ Success - User feedback logged\n")
        else:
            print("   ⚠️ Failed - Feedback may not have been saved\n")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}\n")
    
    # ========================================================================
    # TEST CASE 3: Log with A/B test experiment ID
    # ========================================================================
    print("3️⃣ Logging with A/B test experiment...")
    try:
        success = log_feedback(
            session_id=session_id,
            user_input={"mood": "calm"},
            recommended_cake="Café Tiramisu",
            context={"weather": "rainy"},
            experiment_id="exp_model_v1_vs_v2",
            latency_ms=180,
            confidence_score=0.92,
        )
        if success:
            print("   ✅ Success - Experiment data logged\n")
        else:
            print("   ⚠️ Failed - Experiment logging unsuccessful\n")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}\n")
    
    # ========================================================================
    # COMPLETION
    # ========================================================================
    print("✅ All tests completed!\n")
    print("📝 Next steps:")
    print("   1. Check Supabase dashboard: https://supabase.com")
    print("   2. Go to Table Editor → feedback_logs")
    print("   3. Verify 3 new rows appear with your session_id")
    print("   4. Review data quality (all fields populated)")
    print()


if __name__ == "__main__":
    test_basic_logging()
