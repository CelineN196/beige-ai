"""
SUPABASE INTEGRATION QUICKSTART GUIDE
============================================================================

Step-by-step guide to integrating feedback logging into beige_ai_app.py

This guide shows exact code snippets to add to the Streamlit app.
"""

# ============================================================================
# STEP 1: REQUIREMENTS
# ============================================================================

"""
Add to requirements.txt:

    supabase>=2.0.0,<3.0.0  # Latest stable Supabase Python client
    python-httpx>=0.24.0     # HTTP client dependency

Install:
    pip install -r requirements.txt

NOTE: Supabase v2.x uses a modernized API with better error handling.
The code examples in this guide are compatible with v2.x.
"""

# ============================================================================
# STEP 2: ENVIRONMENT SETUP
# ============================================================================

"""
Create .env file in project root:

    SUPABASE_URL=https://your-project.supabase.co
    SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

How to get these:
  1. Go to https://supabase.com
  2. Create new project or use existing
  3. Go to Settings → API
  4. Copy Project URL and anon/public key
  5. Paste into .env

NEVER commit .env to git - add to .gitignore !
"""

# ============================================================================
# STEP 3: INITIALIZE SUPABASE SCHEMA
# ============================================================================

"""
1. Go to Supabase dashboard
2. Click "SQL Editor"
3. Copy entire contents of backend/supabase_schema.sql
4. Paste into SQL editor
5. Click "Run"
6. Wait for success message

Verify:
  - Go to "Table Editor"
  - You should see: feedback_logs, model_versions, experiments
  - Click feedback_logs and verify 15 columns
  - Check Views: v_model_performance, v_session_analytics
"""

# ============================================================================
# STEP 4: INTEGRATE INTO STREAMLIT APP
# ============================================================================

"""
Add these imports at top of frontend/beige_ai_app.py:

    from backend.integrations.supabase_integration import (
        init_feedback_session_state,
        log_recommendation,
        show_feedback_form,
        log_user_feedback,
        show_session_info,
        show_model_info,
    )
    from backend.integrations.supabase_logger import get_or_create_session_id
    import time  # for latency measurement

Add to main() function, right after @st.cache_resource (if any):

    # Initialize feedback session state (once at startup)
    init_feedback_session_state()

In your recommendation section (where you show the cake), add:

    ─────────────────────────────────────────────────────────
    EXAMPLE: Implement feedback logging after your ML inference
    ─────────────────────────────────────────────────────────

    # Start timing for latency
    inference_start = time.time()
    
    # Your existing ML inference code:
    top_3_cakes, top_3_scores, cluster_id = ml_model.predict(
        user_input=user_input,
        ...
    )
    
    # Calculate latency
    latency_ms = int((time.time() - inference_start) * 1000)
    
    # Get confidence score (first recommendation score)
    confidence_score = float(top_3_scores[0]) if top_3_scores[0] > 0 else 0.5
    
    # ML features used (for debugging/analysis)
    ml_features = {
        "cluster": cluster_id,
        "mood": user_input.get("mood"),
        "weather": user_input.get("weather_condition"),
    }
    
    # CRITICAL: Log the recommendation (non-blocking)
    success = log_recommendation(
        recommended_cake=top_3_cakes[0],
        top_3_cakes=top_3_cakes,
        latency_ms=latency_ms,
        confidence_score=confidence_score,
        cluster_id=cluster_id,
        ml_features=ml_features,
        user_input=user_input,
        additional_context={
            "weather": user_input.get("weather_condition"),
            "mood": user_input.get("mood"),
            "temperature": user_input.get("temperature_celsius"),
        },
    )
    
    # Display the recommendation
    st.write(f"### 🍰 We recommend: **{top_3_cakes[0]}**")
    st.write("_(and alternatives: {}, {})_".format(top_3_cakes[1], top_3_cakes[2]))
    
    # Show feedback form - this collects user rating
    feedback = show_feedback_form(top_3_cakes[0])
    if feedback:
        log_success = log_user_feedback(
            session_id=st.session_state.session_id,
            recommended_cake=top_3_cakes[0],
            feedback_dict=feedback,
        )
        if log_success:
            st.success("✨ Thanks for your feedback!")
        else:
            st.info("Feedback saved locally (connection issue)")
    
    # Optional: Show session debug info in sidebar
    show_session_info()
    show_model_info()
"""

# ============================================================================
# STEP 5: FULL PYTHON EXAMPLE
# ============================================================================

"""
COMPLETE MINIMAL EXAMPLE:
──────────────────────────

Save as test_supabase_integration.py:
"""

import sys
sys.path.insert(0, '/Users/queenceline/Downloads/Beige AI')

from backend.integrations.supabase_logger import log_feedback, get_session_id
from backend.integrations.supabase_integration import log_recommendation
from datetime import datetime
import time

def test_basic_logging():
    \"\"\"Test basic feedback logging.\"\"\"
    
    session_id = get_session_id()
    print(f"📊 Session ID: {session_id}")
    
    # Example 1: Log a simple recommendation
    print("\n1️⃣ Logging basic recommendation...")
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
    print(f"   Result: {'✅ Success' if success else '❌ Failed'}")
    
    # Example 2: Log with user feedback
    print("\n2️⃣ Logging with user feedback...")
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
    print(f"   Result: {'✅ Success' if success else '❌ Failed'}")
    
    # Example 3: Log with experiment ID (A/B test)
    print("\n3️⃣ Logging with A/B test experiment...")
    success = log_feedback(
        session_id=session_id,
        user_input={"mood": "calm"},
        recommended_cake="Café Tiramisu",
        context={"weather": "rainy"},
        experiment_id="exp_model_v1_vs_v2",
        latency_ms=180,
        confidence_score=0.92,
    )
    print(f"   Result: {'✅ Success' if success else '❌ Failed'}")
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    test_basic_logging()

# ============================================================================
# STEP 6: VALIDATION CHECKLIST
# ============================================================================

"""
Before deploying to production:

CONFIGURATION:
  ☐ .env file created with SUPABASE_URL and SUPABASE_KEY
  ☐ .env added to .gitignore
  ☐ All requirements installed: pip install -r requirements.txt
  ☐ Environment variables work (test with: python test_supabase_integration.py)

DATABASE:
  ☐ Supabase project created
  ☐ supabase_schema.sql run successfully
  ☐ feedback_logs table visible in Supabase UI
  ☐ All 6 columns present
  ☐ All 6 indexes created
  ☐ Views v_model_performance and v_session_analytics created

CODE:
  ☐ supabase_logger.py in backend/
  ☐ supabase_integration.py in backend/
  ☐ supabase_schema.sql in backend/
  ☐ Imports added to frontend/beige_ai_app.py
  ☐ log_recommendation() called after ML inference
  ☐ show_feedback_form() displayed to user
  ☐ session_id tracked consistently

TESTING:
  ☐ Test local: python test_supabase_integration.py
  ☐ Run integration tests (if exist)
  ☐ Test feedback logging: submit rating and verify in Supabase
  ☐ Monitor logs for errors: grep -i error app.log

DEPLOYMENT:
  ☐ Update requirements.txt
  ☐ Commit code changes
  ☐ Push to version control
  ☐ Deploy to production
  ☐ Monitor first 100 logs in Supabase
  ☐ Set up dashboard view
  ☐ Create manual backup of feedback logs
"""

# ============================================================================
# STEP 7: QUERYING YOUR DATA
# ============================================================================

"""
After logging first feedback, test queries in Supabase SQL editor:

QUERY 1: View recent logs
─────────────────────────
SELECT 
  created_at,
  session_id,
  recommended_cake,
  user_feedback,
  model_version,
  latency_ms
FROM feedback_logs
ORDER BY created_at DESC
LIMIT 10;

QUERY 2: Model performance comparison
──────────────────────────────────────
SELECT 
  model_version,
  COUNT(*) as recommendations,
  ROUND(AVG(user_feedback::numeric)::numeric, 2) as avg_rating,
  ROUND(AVG(latency_ms)::numeric, 0) as avg_latency_ms,
  COUNT(CASE WHEN user_feedback >= 4 THEN 1 END)::float / 
    COUNT(user_feedback) as satisfaction_rate
FROM feedback_logs
WHERE created_at > NOW() - INTERVAL '24 hours'
  AND user_feedback IS NOT NULL
GROUP BY model_version
ORDER BY avg_rating DESC;

QUERY 3: Which cakes are popular?
──────────────────────────────────
SELECT 
  recommended_cake,
  COUNT(*) as times_recommended,
  ROUND(AVG(user_feedback::numeric)::numeric, 2) as avg_feedback,
  COUNT(CASE WHEN user_feedback >= 4 THEN 1 END)::float / COUNT(user_feedback) as success_rate
FROM feedback_logs
WHERE user_feedback IS NOT NULL
GROUP BY recommended_cake
ORDER BY success_rate DESC
LIMIT 5;

QUERY 4: Latency analysis
─────────────────────────
SELECT 
  model_version,
  PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY latency_ms) as p25,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY latency_ms) as p50_median,
  PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY latency_ms) as p75,
  PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_ms) as p95,
  MAX(latency_ms) as max_latency
FROM feedback_logs
WHERE created_at > NOW() - INTERVAL '24 hours'
GROUP BY model_version;

QUERY 5: A/B test results
──────────────────────────
SELECT 
  experiment_id,
  model_version,
  COUNT(*) as sample_size,
  ROUND(AVG(user_feedback::numeric)::numeric, 2) as avg_feedback,
  ROUND(AVG(latency_ms)::numeric, 0) as avg_latency
FROM feedback_logs
WHERE experiment_id IS NOT NULL
  AND user_feedback IS NOT NULL
GROUP BY experiment_id, model_version
ORDER BY experiment_id, avg_feedback DESC;
"""

# ============================================================================
# STEP 8: TROUBLESHOOTING
# ============================================================================

"""
PROBLEM: "ModuleNotFoundError: No module named 'supabase'"
SOLUTION:
  pip install -r requirements.txt
  Or individually:
    pip install "supabase>=2.0.0"
    pip install "python-httpx>=0.24.0"

PROBLEM: "Credentials not found" warning in logs
SOLUTION:
  1. Create .env file with SUPABASE_URL and SUPABASE_KEY
  2. Source it: source .env
  3. Verify: echo $SUPABASE_URL
  4. Alternative: export SUPABASE_URL=... in terminal

PROBLEM: "Connection refused" or timeout
SOLUTION:
  1. Check Supabase dashboard is accessible
  2. Verify SUPABASE_URL is correct (no trailing slash)
  3. Check internet connection
  4. Try again (will retry 2 times automatically)

PROBLEM: "Table feedback_logs does not exist"
SOLUTION:
  1. Go to Supabase SQL editor
  2. Run backend/supabase_schema.sql
  3. Verify table appears in Table Editor
  4. Restart app

PROBLEM: Data not appearing in Supabase despite success=True
SOLUTION:
  1. Check RLS (Row Level Security) policies
  2. Go to Supabase → feedback_logs → RLS
  3. Disable RLS if blocking inserts (for testing)
  4. Or ensure policies allow authenticated inserts
  5. Check Supabase logs: Settings → Logs

PROBLEM: User feedback always None in database
SOLUTION:
  1. Verify feedback form is triggered (show_feedback_form)
  2. Check that user clicks "Submit Feedback"
  3. Verify log_user_feedback is called after submit
  4. Check that user_feedback is 1-5 integer (validate in form)
"""

# ============================================================================
# STEP 9: MONITORING
# ============================================================================

"""
SET UP MONITORING:
──────────────────

Option 1: Manual SQL queries (quick)
  - Run QUERY 2 above daily
  - Watch for avg_feedback drops
  - Alert if < 3.5 stars

Option 2: Supabase Studio dashboard
  - View Table Editor in real-time
  - Add custom views (visualization)
  - Set up email on issues

Option 3: Metabase (free analytics)
  - Connect Metabase to Supabase
  - Create dashboards
  - Set up alerts

Option 4: Python monitoring script
  - Query Supabase hourly
  - Check metrics
  - Send alerts if issues found

CRITICAL METRICS:
  1. Avg user feedback per model (target: > 3.8/5)
  2. Inference latency (target: < 500ms)
  3. Logging success rate (target: > 99%)
  4. Active models (should be 1 or 2 during A/B test)
"""

# ============================================================================
# STEP 10: NEXT PHASE
# ============================================================================

"""
After initial logging is working (100+ logs):

SHORT TERM (1-2 weeks):
  1. Monitor metrics dashboard
  2. Verify data quality (all fields populated)
  3. Test A/B experiment setup
  4. Plan first model upgrade

MEDIUM TERM (1 month):
  1. Implement automatic model versioning
  2. Set up batch insert for scale (if >100 recs/min)
  3. Create dashboard in Metabase
  4. Plan retraining pipeline

LONG TERM (3+ months):
  1. Implement real-time monitoring
  2. Set up automated alerting
  3. Build recommendation explanation logging
  4. Add fairness monitoring
  5. Implement automatic A/B testing

Contact Supabase if issues:
  - Dashboard: https://supabase.com
  - Docs: https://supabase.com/docs
"""
