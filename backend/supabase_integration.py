"""
Streamlit Integration for Supabase Feedback Logging
============================================================================

This module provides Streamlit-specific integration for the feedback logging system.
It handles non-blocking logging, error handling, and provides utility functions
for collecting feedback directly from the Streamlit UI.

Integration Points:
- Post-recommendation feedback collection
- Automated context capture (time, session state)
- User rating feedback form
- Non-blocking logging (doesn't freeze UI)
- Error resilience (logging failures don't crash the app)
"""

import streamlit as st
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import logging

from backend.supabase_logger import (
    log_feedback,
    get_session_id,
    get_model_version_info,
    CURRENT_MODEL_VERSION,
)

logger = logging.getLogger(__name__)

# ============================================================================
# STREAMLIT SESSION STATE INITIALIZATION
# ============================================================================

def init_feedback_session_state():
    """
    Initialize Streamlit session state for feedback tracking.
    Call this once at app startup.
    """
    if "session_id" not in st.session_state:
        st.session_state.session_id = get_session_id()
        st.session_state.recommendation_count = 0
        st.session_state.logged_feedback = []
        logger.info(f"📊 New session initialized: {st.session_state.session_id}")

def get_or_create_session_id() -> str:
    """Get existing session ID or create a new one."""
    init_feedback_session_state()
    return st.session_state.session_id

# ============================================================================
# CONTEXT CAPTURE
# ============================================================================

def capture_context(additional_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Capture current context from Streamlit session and app state.
    
    Args:
        additional_context: Extra context dict to merge
    
    Returns:
        Dict: Complete context including time, weather, etc.
    """
    context = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "time_of_day": get_time_of_day(),
        "hour": datetime.now().hour,
        "day_of_week": datetime.now().strftime("%A"),
    }
    
    # Add Streamlit widget values if available
    if "user_mood" in st.session_state:
        context["mood"] = st.session_state.user_mood
    
    if "weather_condition" in st.session_state:
        context["weather"] = st.session_state.weather_condition
    
    if "temperature_celsius" in st.session_state:
        context["temperature"] = st.session_state.temperature_celsius
    
    # Merge additional context
    if additional_context:
        context.update(additional_context)
    
    return context

def get_time_of_day() -> str:
    """Determine time of day from current hour."""
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "morning"
    elif 12 <= hour < 16:
        return "afternoon"
    elif 16 <= hour < 21:
        return "evening"
    else:
        return "night"

# ============================================================================
# RECOMMENDATION LOGGING
# ============================================================================

def log_recommendation(
    recommended_cake: str,
    top_3_cakes: list,
    latency_ms: int,
    confidence_score: float,
    cluster_id: int,
    ml_features: Dict[str, Any],
    user_input: Dict[str, Any],
    additional_context: Optional[Dict[str, Any]] = None,
    experiment_id: Optional[str] = None,
) -> bool:
    """
    Log a recommendation to Supabase (non-blocking).
    
    This is called automatically after each ML recommendation in the UI.
    Failures do NOT block the UI - logging is best-effort.
    
    Args:
        recommended_cake: Primary recommendation
        top_3_cakes: List of top 3 recommendations
        latency_ms: Inference time in milliseconds
        confidence_score: ML confidence (0-1)
        cluster_id: Behavioral cluster ID
        ml_features: Features used by ML model
        user_input: Original user input
        additional_context: Extra context to merge
        experiment_id: Optional A/B test experiment ID
    
    Returns:
        bool: True if logged successfully
    """
    
    session_id = get_or_create_session_id()
    context = capture_context(additional_context)
    
    try:
        success = log_feedback(
            session_id=session_id,
            user_input=user_input,
            recommended_cake=recommended_cake,
            recommended_cakes_top_3=top_3_cakes,
            context=context,
            latency_ms=latency_ms,
            confidence_score=confidence_score,
            cluster_id=cluster_id,
            ml_features=ml_features,
            experiment_id=experiment_id,
            model_version=CURRENT_MODEL_VERSION,
        )
        
        if success:
            st.session_state.recommendation_count += 1
            logger.info(f"✅ Logged recommendation #{st.session_state.recommendation_count}")
        else:
            logger.warning("⚠️ Failed to log recommendation (non-blocking)")
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Error logging recommendation: {e}")
        # Don't raise - let UI continue
        return False

# ============================================================================
# FEEDBACK COLLECTION UI
# ============================================================================

def show_feedback_form(cake_name: str) -> Optional[int]:
    """
    Display feedback form in Streamlit sidebar.
    
    Returns:
        int: User rating (1-5) or None if not submitted
    """
    st.sidebar.divider()
    st.sidebar.subheader("📝 How did you like this recommendation?")
    
    feedback = st.sidebar.radio(
        "Rate this recommendation:",
        options=[1, 2, 3, 4, 5],
        format_func=lambda x: ["👎 Not great", "😐 Okay", "👌 Good", "😊 Great", "🤩 Excellent"][x-1],
        horizontal=True,
        key=f"feedback_{cake_name}",
    )
    
    notes = st.sidebar.text_input(
        "Any additional feedback? (optional)",
        placeholder="Too sweet? Not sweet enough? Remind you of something?",
        key=f"notes_{cake_name}",
    )
    
    if st.sidebar.button("Submit Feedback", key=f"submit_{cake_name}"):
        return {
            "rating": feedback,
            "notes": notes if notes else None,
        }
    
    return None

def log_user_feedback(
    session_id: str,
    recommended_cake: str,
    feedback_dict: Dict[str, Any],
) -> bool:
    """
    Log user feedback rating and notes.
    
    Args:
        session_id: Session ID
        recommended_cake: Cake being rated
        feedback_dict: {"rating": 1-5, "notes": "..."}
    
    Returns:
        bool: True if logged
    """
    try:
        from backend.supabase_logger import FeedbackLog
        
        # Create entry with just feedback update
        log_entry = FeedbackLog(
            session_id=session_id,
            user_input={},  # Already logged with recommendation
            recommended_cake=recommended_cake,
            context=capture_context(),
            user_feedback=feedback_dict.get("rating"),
            feedback_notes=feedback_dict.get("notes"),
            model_version=CURRENT_MODEL_VERSION,
        )
        
        is_valid, _ = log_entry.validate()
        if is_valid:
            return log_feedback(
                session_id=session_id,
                user_input={},
                recommended_cake=recommended_cake,
                context=capture_context(),
                user_feedback=feedback_dict.get("rating"),
                feedback_notes=feedback_dict.get("notes"),
            )
        return False
        
    except Exception as e:
        logger.error(f"❌ Error logging user feedback: {e}")
        return False

# ============================================================================
# DEBUG & MONITORING
# ============================================================================

def show_session_info():
    """Show session and logging info in sidebar (for debugging)."""
    if st.sidebar.checkbox("📊 Show session info"):
        st.sidebar.info(
            f"""
            **Session ID:** `{st.session_state.session_id}`
            
            **Model Version:** `{CURRENT_MODEL_VERSION}`
            
            **Recommendations Logged:** {st.session_state.recommendation_count}
            
            **Feedback Entries:** {len(st.session_state.logged_feedback)}
            """
        )

def show_model_info():
    """Display current model version info."""
    info = get_model_version_info()
    st.caption(f"🤖 Model: {info['version']}")

# ============================================================================
# INTEGRATION EXAMPLE
# ============================================================================

"""
USAGE IN YOUR STREAMLIT APP:
============================

In frontend/beige_ai_app.py, after getting recommendations:

    from backend.supabase_integration import (
        init_feedback_session_state,
        log_recommendation,
        show_feedback_form,
        log_user_feedback,
    )
    
    # At app startup:
    init_feedback_session_state()
    
    # After ML inference:
    top_3_cakes, top_3_scores, latency_ms, cluster_id, ml_features = ml_model.predict(...)
    
    # Log the recommendation (non-blocking):
    log_recommendation(
        recommended_cake=top_3_cakes[0],
        top_3_cakes=top_3_cakes,
        latency_ms=latency_ms,
        confidence_score=top_3_scores[0],
        cluster_id=cluster_id,
        ml_features=ml_features,
        user_input={...},
        experiment_id=None,  # or experiment_id from A/B test
    )
    
    # Display cake and then show feedback form:
    st.write(f"We recommend: **{top_3_cakes[0]}**")
    
    feedback = show_feedback_form(top_3_cakes[0])
    if feedback:
        log_user_feedback(
            st.session_state.session_id,
            top_3_cakes[0],
            feedback,
        )
        st.success("Thanks for your feedback! ✨")

"""
