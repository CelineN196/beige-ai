"""
Supabase Feedback Logging System for Beige AI
============================================================================

This module provides production-ready logging for ML recommendation feedback.
It captures user interactions, recommendations, and feedback with automatic
model versioning for ML experimentation and A/B testing.

Key Features:
- Model version tracking for experiment comparison
- Automatic retry logic (2 retries on failure)
- Graceful error handling (non-blocking failures)
- Input validation
- Idempotency through session_id + timestamp
- Async support for high-throughput scenarios
"""

try:
    from dotenv import load_dotenv
    import os
    load_dotenv()
except ImportError:
    import os
    # python-dotenv not available - environment variables must be set manually

import json
import logging
import time
import uuid
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
import hashlib

# Supabase async client
from supabase import create_client, Client
import asyncio
from typing import Coroutine

# ============================================================================
# CONFIGURATION & VERSIONING
# ============================================================================

# MODEL VERSION CONSTANT - Update when deploying new models
# Format: {model_type}_v{major}.{minor}_{deployment_date}
CURRENT_MODEL_VERSION = "hybrid_v1"

# Logging setup
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# ============================================================================
# SUPABASE CLIENT INITIALIZATION
# ============================================================================

def init_supabase_client() -> Optional[Client]:
    """
    Initialize Supabase client from environment variables.
    
    Environment variables required:
    - SUPABASE_URL: Your Supabase project URL
    - SUPABASE_KEY: Your Supabase anon/service role key
    
    Returns:
        Client: Initialized Supabase client, or None if credentials missing
    """
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        logger.warning(
            "⚠️ Supabase credentials not found. "
            "Set SUPABASE_URL and SUPABASE_KEY environment variables. "
            "Logging will be disabled."
        )
        return None
    
    try:
        client = create_client(supabase_url, supabase_key)
        logger.info("✅ Supabase client initialized successfully")
        return client
    except Exception as e:
        logger.error(f"❌ Failed to initialize Supabase client: {e}")
        return None

# Global client instance
_supabase_client: Optional[Client] = None

def get_supabase_client() -> Optional[Client]:
    """Get or initialize the global Supabase client."""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = init_supabase_client()
    return _supabase_client

# ============================================================================
# DATA VALIDATION
# ============================================================================

@dataclass
class FeedbackLog:
    """Validated feedback log entry."""
    session_id: str
    user_input: Dict[str, Any]
    recommended_cake: str
    context: Dict[str, Any]
    model_version: str = CURRENT_MODEL_VERSION
    
    # Optional fields
    user_id: Optional[str] = None
    recommended_cakes_top_3: Optional[list] = None
    recommendation_match: str = "unknown"  # 'match', 'did_not_match', 'unknown'
    user_feedback: Optional[int] = None
    feedback_notes: Optional[str] = None
    latency_ms: Optional[int] = None
    confidence_score: Optional[float] = None
    cluster_id: Optional[int] = None
    ml_features: Optional[Dict] = None
    experiment_id: Optional[str] = None
    is_held_out: bool = False
    
    def validate(self) -> Tuple[bool, Optional[str]]:
        """
        Validate feedback log entry.
        
        Returns:
            (is_valid, error_message)
        """
        # Required fields
        if not self.session_id or not isinstance(self.session_id, str):
            return False, "session_id is required and must be a string"
        
        if not self.user_input or not isinstance(self.user_input, dict):
            return False, "user_input is required and must be a dict"
        
        # recommended_cake: allow string, warn on non-string but don't fail validation
        # The string conversion happens in log_feedback before FeedbackLog is created
        if not self.recommended_cake:
            logger.warning("⚠️ recommended_cake is empty or None - will use 'unknown' as fallback")
        elif not isinstance(self.recommended_cake, str):
            logger.warning(
                f"⚠️ recommended_cake is type {type(self.recommended_cake).__name__} not str. "
                f"This should have been converted upstream in log_checkout_order()"
            )
        
        if not self.context or not isinstance(self.context, dict):
            return False, "context is required and must be a dict"
        
        if not self.model_version or not isinstance(self.model_version, str):
            return False, "model_version is required and must be a string"
        
        # Optional field validation
        if self.user_feedback is not None:
            if not isinstance(self.user_feedback, int) or not (1 <= self.user_feedback <= 5):
                return False, "user_feedback must be integer between 1-5"
        
        if self.latency_ms is not None:
            if not isinstance(self.latency_ms, int) or self.latency_ms < 0:
                return False, "latency_ms must be non-negative integer"
        
        if self.confidence_score is not None:
            if not isinstance(self.confidence_score, (int, float)) or not (0 <= self.confidence_score <= 1):
                return False, "confidence_score must be float between 0-1"
        
        if self.cluster_id is not None:
            if not isinstance(self.cluster_id, int) or self.cluster_id < 0:
                return False, "cluster_id must be non-negative integer"
        
        return True, None

# ============================================================================
# FEEDBACK LOGGING FUNCTION
# ============================================================================

def log_feedback(
    session_id: str,
    user_input: Dict[str, Any],
    recommended_cake: str,
    context: Dict[str, Any],
    user_feedback: Optional[int] = None,
    feedback_notes: Optional[str] = None,
    latency_ms: Optional[int] = None,
    confidence_score: Optional[float] = None,
    cluster_id: Optional[int] = None,
    ml_features: Optional[Dict] = None,
    experiment_id: Optional[str] = None,
    model_version: Optional[str] = None,
    user_id: Optional[str] = None,
    recommended_cakes_top_3: Optional[list] = None,
    recommendation_match: str = "unknown",
    max_retries: int = 2,
) -> bool:
    """
    Log a feedback entry to Supabase with automatic retries.
    
    This is the main entry point for logging user interactions. It handles:
    - Input validation
    - Automatic model version attachment
    - Retry logic for network failures
    - Graceful error handling
    
    Args:
        session_id: Unique session identifier
        user_input: User input dict (mood, weather, preferences, etc.)
        recommended_cake: Primary recommendation
        context: Context dict (weather, mood, time_of_day, etc.)
        user_feedback: Optional rating (1-5)
        feedback_notes: Optional qualitative feedback
        latency_ms: Optional inference latency in ms
        confidence_score: Optional ML confidence (0-1)
        cluster_id: Optional behavioral cluster assignment
        ml_features: Optional input features used by ML
        experiment_id: Optional A/B test experiment ID
        model_version: Optional override (default: CURRENT_MODEL_VERSION)
        user_id: Optional authenticated user ID
        recommended_cakes_top_3: Optional list of alternatives
        max_retries: Number of retries on failure (default: 2)
    
    Returns:
        bool: True if logged successfully, False otherwise
    """
    
    # Use provided model_version or current default
    if model_version is None:
        model_version = CURRENT_MODEL_VERSION
    
    # SAFETY: Ensure recommended_cake is always a string
    # Handle dict (e.g., full AI result), list, None, or non-string types
    if isinstance(recommended_cake, dict):
        # Extract first cake name from dict if it has 'top_3_cakes'
        if "top_3_cakes" in recommended_cake and isinstance(recommended_cake.get("top_3_cakes"), list):
            cakes = recommended_cake["top_3_cakes"]
            if cakes:
                recommended_cake = str(cakes[0])
            else:
                recommended_cake = "unknown"
        else:
            # Serialize dict to JSON string
            try:
                recommended_cake = json.dumps(recommended_cake, ensure_ascii=False)[:200]
            except Exception as e:
                logger.warning(f"Failed to serialize dict recommendation: {e}")
                recommended_cake = "unknown"
    
    elif isinstance(recommended_cake, list):
        # Take first element from list
        if recommended_cake:
            recommended_cake = str(recommended_cake[0])
        else:
            recommended_cake = "unknown"
    
    elif recommended_cake is None:
        recommended_cake = "unknown"
    
    elif not isinstance(recommended_cake, str):
        # Other types: convert to string
        try:
            recommended_cake = str(recommended_cake)
        except Exception as e:
            logger.warning(f"Failed to convert recommended_cake to string: {e}")
            recommended_cake = "unknown"
    
    # Ensure string is not empty
    if not recommended_cake or recommended_cake.strip() == "":
        logger.warning("recommended_cake is empty after conversion - using 'unknown'")
        recommended_cake = "unknown"
    
    # Create feedback log entry
    log_entry = FeedbackLog(
        session_id=session_id,
        user_input=user_input,
        recommended_cake=recommended_cake,
        context=context,
        model_version=model_version,
        user_id=user_id,
        recommended_cakes_top_3=recommended_cakes_top_3,
        recommendation_match=recommendation_match,
        user_feedback=user_feedback,
        feedback_notes=feedback_notes,
        latency_ms=latency_ms,
        confidence_score=confidence_score,
        cluster_id=cluster_id,
        ml_features=ml_features,
        experiment_id=experiment_id,
    )
    
    # Validate entry
    is_valid, error_msg = log_entry.validate()
    if not is_valid:
        logger.warning(f"⚠️ Validation failed: {error_msg}")
        return False
    
    # Get Supabase client
    client = get_supabase_client()
    if client is None:
        logger.warning("⚠️ Supabase client not initialized. Feedback not logged.")
        return False
    
    # Convert entry to dict and prepare for insertion
    log_dict = asdict(log_entry)
    
    # Retry logic with fallback for missing column
    for attempt in range(max_retries + 1):
        try:
            # Insert into Supabase
            response = client.table("feedback_logs").insert(log_dict).execute()
            
            logger.info(
                f"✅ Feedback logged successfully "
                f"[session={session_id}, model={model_version}, cake={recommended_cake}]"
            )
            return True
            
        except Exception as e:
            error_str = str(e)
            error_type = type(e).__name__
            
            logger.error(
                f"❌ Attempt {attempt + 1}/{max_retries + 1} failed: {error_type}: {error_str}"
            )
            
            # Debug: Log RLS failure indicators
            if "policy" in error_str.lower() or "permission" in error_str.lower() or "rls" in error_str.lower():
                logger.error(
                    f"   🔒 RLS POLICY ISSUE DETECTED. Check Supabase RLS policies on feedback_logs table."
                )
                logger.error(
                    f"   📋 Payload size: {len(str(log_dict))} bytes"
                )
                logger.error(
                    f"   👤 Session: {session_id}, User: {user_id}"
                )
            
            # Fallback: if column not found, remove recommendation_match and retry
            if "recommendation_match" in error_str.lower() and "could not find" in error_str.lower():
                logger.warning(
                    f"   🔄 FALLBACK: 'recommendation_match' column not found in database."
                )
                logger.warning(
                    f"   💡 Please run this SQL in Supabase to add the column:"
                )
                logger.warning(
                    f"      ALTER TABLE feedback_logs ADD COLUMN recommendation_match TEXT DEFAULT 'unknown';"
                )
                
                # Remove the problematic field and retry
                if "recommendation_match" in log_dict:
                    log_dict.pop("recommendation_match")
                    logger.warning(
                        f"   🔁 Retrying insert WITHOUT recommendation_match field..."
                    )
                    continue
            
            if attempt < max_retries:
                # Exponential backoff: 1s, 2s, etc.
                wait_time = 2 ** attempt
                logger.info(f"   ⏳ Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                logger.error(f"❌ Failed to log feedback after {max_retries + 1} attempts")
                return False
    
    return False

# ============================================================================
# ASYNC LOGGING (For high-throughput scenarios)
# ============================================================================

async def log_feedback_async(
    session_id: str,
    user_input: Dict[str, Any],
    recommended_cake: str,
    context: Dict[str, Any],
    **kwargs
) -> bool:
    """
    Async version of log_feedback for non-blocking logging.
    
    Use this in high-throughput scenarios or when you want to avoid
    blocking the main thread.
    
    Args:
        Same as log_feedback()
    
    Returns:
        bool: True if logged successfully
    """
    # Run sync function in thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        log_feedback,
        session_id,
        user_input,
        recommended_cake,
        context,
    )

# ============================================================================
# BATCH LOGGING (For efficiency)
# ============================================================================

class FeedbackBatcher:
    """
    Batch multiple feedback entries and insert them together.
    
    This reduces API calls and is more efficient for high-volume logging.
    
    Example:
        batcher = FeedbackBatcher(max_batch_size=100, flush_interval=60)
        batcher.add(session_id, user_input, recommended_cake, context)
        batcher.start()  # Start flush worker
    """
    
    def __init__(self, max_batch_size: int = 100, flush_interval: int = 60):
        """
        Initialize feedback batcher.
        
        Args:
            max_batch_size: Max entries before auto-flush
            flush_interval: Seconds between flushes
        """
        self.max_batch_size = max_batch_size
        self.flush_interval = flush_interval
        self.batch: list = []
        self.lock = asyncio.Lock()
        self._flush_task = None
    
    def add(self, **kwargs) -> None:
        """Add entry to batch."""
        log_entry = FeedbackLog(
            session_id=kwargs['session_id'],
            user_input=kwargs['user_input'],
            recommended_cake=kwargs['recommended_cake'],
            context=kwargs['context'],
            model_version=kwargs.get('model_version', CURRENT_MODEL_VERSION),
            **{k: v for k, v in kwargs.items() 
               if k not in ['session_id', 'user_input', 'recommended_cake', 'context', 'model_version']}
        )
        
        is_valid, _ = log_entry.validate()
        if is_valid:
            self.batch.append(asdict(log_entry))
            
            # Auto-flush if batch full
            if len(self.batch) >= self.max_batch_size:
                _ = self.flush()
    
    def flush(self) -> bool:
        """Flush batch to Supabase."""
        if not self.batch:
            return True
        
        client = get_supabase_client()
        if client is None:
            logger.warning("⚠️ Supabase client not initialized. Batch not flushed.")
            return False
        
        try:
            response = client.table("feedback_logs").insert(self.batch).execute()
            logger.info(f"✅ Flushed {len(self.batch)} feedback entries")
            self.batch = []
            return True
        except Exception as e:
            logger.error(f"❌ Failed to flush batch: {e}")
            return False
    
    async def start_periodic_flush(self) -> None:
        """Start periodic flush worker (async)."""
        while True:
            await asyncio.sleep(self.flush_interval)
            self.flush()

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_session_id() -> str:
    """Generate a unique session ID."""
    return str(uuid.uuid4())

def idempotency_key(session_id: str, timestamp: datetime) -> str:
    """
    Generate idempotency key to prevent duplicate inserts.
    
    Use as a unique constraint on (session_id, timestamp) combination.
    """
    key_str = f"{session_id}:{timestamp.isoformat()}"
    return hashlib.sha256(key_str.encode()).hexdigest()

def get_model_version_info() -> Dict[str, str]:
    """Get current model version and metadata."""
    return {
        "version": CURRENT_MODEL_VERSION,
        "set_at": datetime.now(timezone.utc).isoformat(),
        "type": "hybrid_ml",  # or 'rule_based', 'neural', etc.
    }

def get_or_create_session_id() -> str:
    return str(uuid.uuid4())

# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # This is a simple test - in production, use from Streamlit app
    
    # Example feedback entry
    success = log_feedback(
        session_id="session_12345",
        user_input={
            "mood": "happy",
            "weather_condition": "sunny",
            "temperature_celsius": 25,
            "sweetness_preference": 7,
            "health_preference": 6,
        },
        recommended_cake="Dark Chocolate Sea Salt Cake",
        context={
            "weather": "sunny",
            "mood": "happy",
            "time_of_day": "afternoon",
            "temperature": 25,
            "hour": 14,
        },
        user_feedback=5,
        feedback_notes="Loved this recommendation!",
        latency_ms=234,
        confidence_score=0.87,
        cluster_id=2,
    )
    
    print(f"Log result: {success}")
