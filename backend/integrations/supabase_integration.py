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

from backend.integrations.supabase_logger import (
    log_feedback,
    get_session_id,
    get_model_version_info,
    CURRENT_MODEL_VERSION,
)

import json

logger = logging.getLogger(__name__)

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def _safe_stringify_recommendation(value: Any) -> str:
    """
    Safely convert any recommendation value to a string.
    
    Handles:
    - str: returned as-is
    - dict: tries to extract 'top_3_cakes' first, else serializes to JSON
    - list: returns first element or "unknown"
    - None: converted to "unknown"
    - other: converted using str()
    
    Args:
        value: Any type to convert
    
    Returns:
        str: Safe string representation
    """
    if isinstance(value, str):
        # Already string - ensure it's not empty
        return value if value else "unknown"
    
    elif isinstance(value, dict):
        # Handle AI result dict from session_state
        if "top_3_cakes" in value and isinstance(value.get("top_3_cakes"), list):
            cakes = value["top_3_cakes"]
            if cakes:
                return str(cakes[0])
        
        # Fallback: serialize to JSON
        try:
            serialized = json.dumps(value, ensure_ascii=False)
            return serialized[:200]  # Limit to 200 chars for storage
        except Exception as e:
            logger.warning(f"Failed to serialize dict recommendation: {e}")
            return "unknown_recommendation"
    
    elif isinstance(value, list):
        # If list of cakes, take first one
        if value and len(value) > 0:
            return str(value[0])
        return "unknown"
    
    elif value is None:
        return "unknown"
    
    else:
        # Fallback: convert any other type
        try:
            result = str(value) if value else "unknown"
            return result if result else "unknown"
        except:
            return "unknown"

def _compute_recommendation_match(
    recommended_cake: str,
    purchased_items: list,
) -> str:
    """
    Compute whether the recommended cake matches purchased items.
    
    Args:
        recommended_cake: The recommended cake name (string)
        purchased_items: List of purchased items (list of dicts with 'name' key, or list of strings)
    
    Returns:
        str: "match", "did_not_match", or "unknown"
    """
    # Normalize recommended cake
    if not recommended_cake or recommended_cake == "unknown":
        return "unknown"
    
    rec_normalized = str(recommended_cake).strip().lower()
    
    # Handle empty purchase list
    if not purchased_items or len(purchased_items) == 0:
        return "unknown"
    
    # Extract cake names from purchased items
    purchased_names = []
    for item in purchased_items:
        if isinstance(item, dict):
            # Cart items are dicts with 'name' key
            name = item.get('name', '')
        else:
            # Or could be strings
            name = str(item)
        
        if name:
            purchased_names.append(name.strip().lower())
    
    # If no valid purchased names, unknown
    if not purchased_names:
        return "unknown"
    
    # Check if recommended cake is in purchased items
    if rec_normalized in purchased_names:
        return "match"
    else:
        return "did_not_match"

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
        from backend.integrations.supabase_logger import FeedbackLog
        
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
# CHECKOUT ORDER LOGGING
# ============================================================================

def log_checkout_order(
    order_id: str,
    items_purchased: str,
    ai_recommendation: Any,
    match_result: str,
    total_value: Optional[float] = None,
    purchased_items: Optional[list] = None,
) -> bool:
    """
    Log a checkout order to Supabase.
    
    Called after successful checkout to record purchase data.
    This bridges recommendation logging and actual purchase behavior.
    
    Args:
        order_id: Unique order ID (UUID)
        items_purchased: Comma-separated cake names purchased
        ai_recommendation: The recommended cake from AI (str, dict, list, or any type - will be converted)
        match_result: "Match" if recommendation was purchased, "Not Quite" otherwise
        total_value: Optional total order value
        purchased_items: List of purchased items (dicts with 'name' key) for detailed matching
    
    Returns:
        bool: True if logged successfully
    """
    session_id = get_or_create_session_id()
    
    try:
        # Convert ai_recommendation to string safely
        cake_str = _safe_stringify_recommendation(ai_recommendation)
        
        logger.debug(
            f"Checkout order: ai_recommendation type={type(ai_recommendation).__name__}, "
            f"converted to: {cake_str[:60]}..."
        )
        
        # Compute recommendation_match
        recommendation_match = _compute_recommendation_match(
            recommended_cake=cake_str,
            purchased_items=purchased_items or [],
        )
        
        logger.debug(
            f"Recommendation match: recommended='{cake_str}', "
            f"purchased_count={len(purchased_items) if purchased_items else 0}, "
            f"result='{recommendation_match}'"
        )
        
        # Log the order as a special feedback entry
        success = log_feedback(
            session_id=session_id,
            user_input={
                "order_id": order_id,
                "items_purchased": items_purchased,
                "match_result": match_result,
                "total_value": total_value,
            },
            recommended_cake=cake_str,
            context={
                "checkout": True,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            feedback_notes=f"Checkout: {match_result} | Purchased: {items_purchased}",
            model_version=CURRENT_MODEL_VERSION,
            recommendation_match=recommendation_match,
        )
        
        if success:
            logger.info(f"✅ Checkout logged to Supabase [order={order_id}, result={match_result}]")
        else:
            logger.warning(f"⚠️ Failed to log checkout to Supabase [order={order_id}]")
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Error logging checkout: {e}")
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

    from backend.integrations.supabase_integration import (
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
