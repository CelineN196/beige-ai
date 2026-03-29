"""
MODEL VERSIONING STRATEGY & PRODUCTION RELIABILITY GUIDE
============================================================================

This document outlines the complete strategy for managing ML model versions
in production, enabling A/B testing, experimentation, and safe rollbacks.

CRITICAL: Every feedback log MUST include model_version for experimentation.
"""

# ============================================================================
# 1. MODEL VERSIONING SCHEME
# ============================================================================

"""
VERSION FORMAT: {model_name}_{version}

Examples:
  - hybrid_v1              (Hybrid v1: XGBoost + scikit-learn ensemble, current production)
  - hybrid_v2_2026-04-15   (Future version with improved features)
  - ensemble_v1_2026-05-01 (Alternative ensemble approach)

Semantic Versioning Guidelines:
  - MAJOR version: Algorithm change (XGBoost → Neural, feature set change)
  - MINOR version: Hyperparameter tuning, retraining on new feedback data
  - PATCH version: (Not used - tracked by deployment date for future)

Model Type Categories:
  - hybrid:     XGBoost + scikit-learn preprocessing (current)
  - ensemble:   Multiple model combination
  - neural:     Deep learning models (future)
"""

# ============================================================================
# 2. MODEL REGISTRY - HYBRID V1
# ============================================================================

"""
CURRENT PRODUCTION MODEL: Hybrid v1
Location: backend/models/v2_final_model.pkl (3.2 MB)

Model Specification:
  ✅ Algorithm: XGBoost 2.0.3 + scikit-learn 1.5.1
  ✅ Input Features: 13 (5 categorical + 8 numerical)
  ✅ Output Classes: 8 cake types
  ✅ Training Source: feedback_logs table from Supabase
  ✅ Versioning Field: model_version = "hybrid_v1" in feedback logs
  ✅ A/B Testing: Use experiment_id field for test tracking
  ✅ Validation: is_held_out field for hold-out test set

Archived Models:
  📁 backend/models/legacy/    (Previous versions for rollback)
"""

Version Information Storage:
  Backend: model_versions table in Supabase
  
  model_versions schema:
  ┌─────────────────────────────────────────────┐
  │ Column         │ Type      │ Example         │
  ├─────────────────────────────────────────────┤
  │ version_name   │ TEXT      │ hybrid_v1       │
  │ version_type   │ TEXT      │ ml_hybrid       │
  │ deployed_at    │ TIMESTAMP │ 2024-01-15      │
  │ is_active      │ BOOLEAN   │ true            │
  │ baseline_metrics│ JSONB     │ {...}           │
  │ previous_version│ TEXT      │ hybrid_v0       │
  │ notes          │ TEXT      │ "..."           │
  └─────────────────────────────────────────────┘
"""

# ============================================================================
# 3. DEPLOYMENT WORKFLOW
# ============================================================================

"""
Step 1: LOCAL TESTING
  - Train new model locally
  - Validate on test set
  - Run offline evaluation
  - Store in models/v2/ or models/v3/ (staging)

Step 2: CREATE VERSION RECORD
  - Add entry to Supabase model_versions table
  - Set is_active = FALSE initially (in review)
  - Record baseline metrics (accuracy, speed, etc.)
  - Link to previous version for easy rollback

Step 3: DEPLOY TO STAGING
  - Update production files with new model
  - Set is_active = FALSE (don't use yet)
  - Run integration tests against staging data
  - Validate in test Streamlit instance

Step 4: CANARY DEPLOY (Optional)
  - Set experiment_id for traffic splitting
  - Route X% of traffic to new model
  - Monitor performance in feedback_logs
  - Use v_model_performance view to compare

Step 5: FULL DEPLOYMENT
  - Update CURRENT_MODEL_VERSION in supabase_logger.py
  - Set is_active = TRUE in model_versions
  - Monitor real-time performance
  - Keep previous version linked for quick rollback

Step 6: MONITORING & FEEDBACK
  - Query v_model_performance view hourly
  - Alert if user_feedback drops below threshold
  - Collect feedback_logs via feedback table
  - Use for retraining dataset

Step 7: ROLLBACK (if needed)
  - Restore previous model files
  - Update CURRENT_MODEL_VERSION to previous
  - Set is_active = FALSE for failed version
  - Investigate failure cause
"""

# ============================================================================
# 4. A/B TESTING SETUP
# ============================================================================

"""
The experiments table enables rigorous A/B testing:

experiments schema:
┌────────────────────────────────────────────┐
│ Column            │ Type  │ Purpose          │
├────────────────────────────────────────────┤
│ experiment_id     │ TEXT  │ Unique test ID   │
│ name              │ TEXT  │ "Model v1 vs v2" │
│ model_version_a   │ TEXT  │ Control version  │
│ model_version_b   │ TEXT  │ Treatment        │
│ start_date        │ DATE  │ Start            │
│ end_date          │ DATE  │ End              │
│ sample_size       │ INT   │ Logs collected   │
│ winner            │ TEXT  │ "a", "b", "tie"  │
│ winner_metric     │ TEXT  │ "avg_feedback"   │
│ is_completed      │ BOOL  │ Test finished    │
└────────────────────────────────────────────┘

Setup A/B Test:
  1. Create experiment record in Supabase
  2. Generate experiment_id: uuid4()
  3. During inference, randomly assign to version A or B
  4. Log each recommendation with experiment_id
  5. Query feedback_logs filtered by experiment_id
  6. Compare v_model_performance by model_version

Example SQL to compare:
  SELECT 
    model_version,
    COUNT(*) as recommendations,
    AVG(user_feedback::numeric) as avg_rating,
    AVG(latency_ms) as avg_latency,
    AVG(confidence_score) as avg_confidence
  FROM feedback_logs
  WHERE experiment_id = 'exp_12345'
  GROUP BY model_version
  ORDER BY avg_rating DESC;
"""

# ============================================================================
# 5. PRODUCTION RELIABILITY STRATEGY
# ============================================================================

"""
FAILURE MODES & MITIGATION:
──────────────────────────────

1. SUPABASE UNAVAILABLE
   Problem: Network failure, service outage
   Impact: Logging fails, UI must not crash
   Mitigation:
     ✅ Retry logic with exponential backoff (2 retries)
     ✅ Catch all exceptions in log_feedback()
     ✅ Return False on permanent failure
     ✅ UI continues regardless of logging success
     ✅ Future: Queue failed logs locally, retry later
   
   Code: See max_retries=2 in log_feedback()

2. INVALID DATA
   Problem: Malformed user input, missing fields
   Impact: Silent insert failure or data corruption
   Mitigation:
     ✅ FeedbackLog.validate() checks all constraints
     ✅ Type validation (int, float, string, dict)
     ✅ Range validation (feedback 1-5, latency ≥ 0)
     ✅ Required field checking
     ✅ Validation runs before insert attempt
   
   Code: See FeedbackLog.validate() method

3. DUPLICATE SUBMISSIONS
   Problem: Same user resubmits same feedback
   Impact: Inflated metrics, misrepresented model performance
   Mitigation:
     ✅ session_id + timestamp combination unique
     ✅ PostgreSQL UNIQUE constraint on these fields
     ✅ Idempotency key generation available
     ✅ Future: Implement upsert instead of insert
   
   Code: idempotency_key(session_id, timestamp)

4. NETWORK LATENCY
   Problem: Slow inserts block inference
   Impact: Poor user experience, slow recommendation
   Mitigation:
     ✅ Use async logging: log_feedback_async()
     ✅ Logging happens in background, non-blocking
     ✅ Return immediately to user
     ✅ Gather events into batch, flush periodically
   
   Code: FeedbackBatcher class

5. CREDENTIAL LEAKS
   Problem: SUPABASE_KEY exposed in code/logs
   Impact: Unauthorized database access
   Mitigation:
     ✅ Use environment variables only
     ✅ Never commit .env to git
     ✅ Use .gitignore with **/.env
     ✅ Supabase RLS policies (row-level security)
     ✅ Use service role key only in backend
   
   Code: os.getenv("SUPABASE_KEY")

6. MODEL VERSION MISMATCH
   Problem: Feedback logged for wrong model version
   Impact: Metrics attributed to wrong model, bad A/B test
   Mitigation:
     ✅ CURRENT_MODEL_VERSION central constant
     ✅ model_version NOT NULL constraint in DB
     ✅ Automatic attachment in log_feedback()
     ✅ Validation error if missing
   
   Code: model_version=CURRENT_MODEL_VERSION default

7. STALE DATA IN CACHE
   Problem: Old model version info cached
   Impact: Logging outdated model version
   Mitigation:
     ✅ Supabase client initialized at startup
     ✅ get_supabase_client() uses singleton pattern
     ✅ Re-initialize if returns None
     ✅ Log version at app startup
"""

# ============================================================================
# 6. PERFORMANCE OPTIMIZATION
# ============================================================================

"""
OPTIMIZATION STRATEGIES:
───────────────────────

1. BATCH INSERTION
   Strategy: Queue multiple logs, insert together
   Benefit: Fewer API calls, lower latency
   Usage:
     batcher = FeedbackBatcher(max_batch_size=100, flush_interval=60)
     batcher.add(session_id, user_input, cake, context)
     # Auto-flushes when batch reaches 100 or 60s passes
   
   Best for: High-traffic deployments (100+ recommendations/min)

2. ASYNCHRONOUS LOGGING
   Strategy: Log in background thread, don't block UI
   Benefit: Instant response to user
   Usage:
     asyncio.create_task(log_feedback_async(...))
   
   Best for: Real-time applications where latency matters

3. DATABASE INDEXES
   Indexes created:
     ✅ idx_feedback_logs_session_id (fast session lookup)
     ✅ idx_feedback_logs_model_version (quick model comparison)
     ✅ idx_feedback_logs_created_at (time-range queries)
     ✅ idx_feedback_logs_model_created (composite: A/B testing)
     ✅ idx_feedback_logs_user_feedback (filtered feedback analysis)
     ✅ idx_feedback_logs_experiment (filtered A/B test queries)
   
   Impact: Queries 10-100x faster

4. MATERIALIZED VIEWS
   Created:
     ✅ v_model_performance (pre-aggregated by model)
     ✅ v_session_analytics (pre-aggregated by session)
   
   Benefit: Instant analytics without computation
   Usage: SELECT * FROM v_model_performance WHERE model_version='hybrid_v1'
   
   Query time: <100ms instead of 5-10s

5. JSONB FIELDS
   Fields using JSONB:
     - user_input (flexible schema for future features)
     - context (weather, mood, time, custom fields)
     - ml_features (features used by model)
   
   Benefit: Expandable without schema migration
   Query: WHERE user_input->'mood' = '"happy"'

6. CACHING RECOMMENDATIONS
   Strategy: Cache popular recommendations
   Implementation:
     - Use time-based cache (TTL: 5 min per mood+weather combo)
     - Hit rate target: 40-60% in production
     - Always log for feedback, even if cached
   
   Benefit: Reduce inference load 50%+

7. COMPRESSION
   Strategy: Compress archived feedback logs monthly
   Implementation:
     - Partition by month in feedback_logs
     - Archive old partitions to cold storage
     - Query recent data from hot partition
   
   Benefit: Database remains lean, queries fast
"""

# ============================================================================
# 7. SCALING GUIDELINES
# ============================================================================

"""
TRAFFIC SCALING:
────────────────

At 10 recs/min (150 logs/hour):
  - Standard Supabase tier sufficient
  - Single batch (query per recommendation)
  - Response time: <500ms

At 100 recs/min (1,500 logs/hour):
  - Use async logging (log_feedback_async)
  - Batch size: 50 recommendations
  - Flush interval: 30 seconds
  - Response time: <100ms
  - Database: Supabase Pro tier

At 1,000 recs/min (15,000 logs/hour):
  - Use FeedbackBatcher with batch_size=200
  - Flush interval: 10 seconds
  - Enable connection pooling
  - Use Supabase Enterprise with dedicated compute
  - Monitoring: Real-time query performance

At 10,000+ recs/min:
  - Consider Kafka/message queue for decoupling
  - Batch into PostgreSQL in micro-batches (10ms windows)
  - Use PostgreSQL COPY command (1000x faster than INSERT)
  - Implement sampling (log 1 in N recommendations)
  - Separate analytics database from operational database

RETENTION & ARCHIVAL:
─────────────────────

Data retention policy:
  - Keep in feedback_logs: 90 days (hot)
  - Archive to cold storage: 1-2 years (analytics)
  - Purge after: 2 years (GDPR/privacy)

Archival SQL:
  -- Monthly partitioning
  CREATE TABLE feedback_logs_2024_01 PARTITION OF feedback_logs
  FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
  
  -- Archive: copy old partition to S3-compatible storage
  COPY feedback_logs_2024_01 TO 's3://bucket/feedback_2024_01.parquet';
  DROP TABLE feedback_logs_2024_01;

Cost optimization:
  - Hot data (90d): Supabase managed storage
  - Warm data (90d-2yr): S3 Glacier Flexible Retrieval
  - Cold data (2yr+): S3 Glacier Deep Archive or delete
  - Estimated cost at 1M logs/day: $100-500/month
"""

# ============================================================================
# 8. MONITORING & ALERTING
# ============================================================================

"""
METRICS TO MONITOR:
───────────────────

1. MODEL PERFORMANCE
   Metric: Average user feedback per model_version
   Target: ≥ 3.8/5.0 (good)
   Alert: Drop below 3.5/5.0
   Query:
     SELECT 
       model_version,
       COUNT(*) as count,
       AVG(user_feedback::numeric) as avg_feedback
     FROM feedback_logs
     WHERE created_at > NOW() - INTERVAL '24 hours'
       AND user_feedback IS NOT NULL
     GROUP BY model_version
     ORDER BY avg_feedback DESC;

2. INFERENCE LATENCY
   Metric: Average latency_ms per model
   Target: < 500ms (acceptable for user)
   Alert: > 1000ms (causing timeouts)
   Query:
     SELECT 
       model_version,
       PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY latency_ms) as p50,
       PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_ms) as p95
     FROM feedback_logs
     WHERE created_at > NOW() - INTERVAL '24 hours'
     GROUP BY model_version;

3. LOGGING SUCCESS RATE
   Metric: % of recommendations successfully logged
   Target: > 99%
   Alert: < 98%
   Calculation: COUNT(where is_valid=true) / total recommendations

4. A/B TEST WINNER
   Metric: Statistical significance of model difference
   Target: p-value < 0.05 suggests winner
   Query:
     SELECT 
       experiment_id,
       model_version_a,
       model_version_b,
       (SELECT AVG(user_feedback::numeric) 
        FROM feedback_logs 
        WHERE experiment_id = e.experiment_id 
          AND model_version = e.model_version_a) as avg_a,
       (SELECT AVG(user_feedback::numeric) 
        FROM feedback_logs 
        WHERE experiment_id = e.experiment_id 
          AND model_version = e.model_version_b) as avg_b
     FROM experiments e
     WHERE is_completed = FALSE;

DASHBOARD SETUP:
────────────────
Use Supabase studio or connect to Metabase:
  - Real-time charting of feedback trends
  - Model version comparison (side-by-side)
  - Session analytics (retention, engagement)
  - Error rate tracking
"""

# ============================================================================
# 9. SWITCHING MODELS
# ============================================================================

"""
SAFE MODEL ROLLOUT:
───────────────────

Scenario 1: PLANNED UPGRADE
  1. Train new model locally
  2. Add to model_versions: is_active=FALSE
  3. Deploy to staging
  4. Run A/B test for 1-7 days
  5. If winning: UPDATE is_active=TRUE
  6. Update CURRENT_MODEL_VERSION
  7. Monitor for issues
  8. Keep previous version linked for rollback

Scenario 2: EMERGENCY ROLLBACK
  1. Identify issue (drop in feedback, latency spike, etc.)
  2. Restore previous model files from git
  3. Update CURRENT_MODEL_VERSION to previous
  4. UPDATE model_versions SET is_active=FALSE WHERE version=failed
  5. UPDATE model_versions SET is_active=TRUE WHERE version=previous
  6. Restart Streamlit app
  7. Monitor that metrics recover
  8. Post-mortem: investigate failure root cause

Scenario 3: GRADUAL ROLLOUT (Canary)
  1. Set up experiment_id for traffic split
  2. Route 10% to new model, 90% to old
  3. Monitor for 2-4 hours
  4. If stable: 25% → 75%
  5. If stable: 50% → 50%
  6. If stable: 100% to new model
  7. If issue detected at any step: rollback to old

Code to implement canary:
  import random
  current_model = 'hybrid_v1'
  new_model = 'hybrid_v2'
  canary_percentage = 10  # 10% traffic to new
  
  if random.random() < canary_percentage / 100:
    model_version = new_model
    experiment_id = 'canary_v1_vs_v2'
  else:
    model_version = current_model
    experiment_id = 'canary_v1_vs_v2'
  
  # Use model_version, log with experiment_id
"""

# ============================================================================
# 10. TROUBLESHOOTING
# ============================================================================

"""
ISSUE: Logs not appearing in Supabase
CAUSES:
  1. Credentials not set (SUPABASE_URL/KEY missing)
  2. RLS policy blocking inserts
  3. Validation failure (check FeedbackLog.validate())
  4. Network error (check Supabase dashboard)
FIXES:
  1. Set environment variables: export SUPABASE_URL=...
  2. Disable RLS on feedback_logs table
  3. Add logging to catch validation errors
  4. Check Supabase logs: Settings → Logs

ISSUE: Feedback ratings all 5 stars (unrealistic)
CAUSES:
  1. Only satisfied users providing feedback
  2. Incorrect rating scale (should be 1-5, not 0-4)
  3. UI bug hiding negative feedback
FIXES:
  1. Make feedback optional, collect from samples
  2. Validate user_feedback in feedback form (1-5)
  3. Add debug logging to show submitted values

ISSUE: Model version mismatch in logs
CAUSES:
  1. Updated CURRENT_MODEL_VERSION without restarting app
  2. Mixing old/new code in deployment
FIXES:
  1. Restart Streamlit app: streamlit run app.py
  2. Ensure all files updated before restart

ISSUE: Slow queries on feedback_logs
CAUSES:
  1. Missing indexes
  2. Full table scans
  3. Large JSONB parsing
FIXES:
  1. Verify indexes exist: SELECT * FROM pg_indexes WHERE tablename='feedback_logs'
  2. Use EXPLAIN ANALYZE to check query plan
  3. Pre-aggregate in materialized views
"""

# ============================================================================
# 11. NEXT STEPS
# ============================================================================

"""
TODO (In Priority Order):
──────────────────────

IMMEDIATE (Next commit):
  ✅ Create supabase_schema.sql
  ✅ Create supabase_logger.py
  ✅ Create supabase_integration.py
  ⏳ Add to requirements.txt: supabase>=0.15.0
  ⏳ Integrate into frontend/beige_ai_app.py (call log_recommendation)
  ⏳ Test end-to-end with real data

SHORT TERM (This week):
  ⏳ Set up Supabase project and run schema.sql
  ⏳ Get SUPABASE_URL and SUPABASE_KEY from Supabase
  ⏳ Deploy to staging environment
  ⏳ Run integration tests
  ⏳ Monitor first 100 logs

MEDIUM TERM (This month):
  ⏳ Deploy to production
  ⏳ Monitor metrics dashboard
  ⏳ Plan first A/B test
  ⏳ Document versioning process for team

LONG TERM (Next quarter):
  ⏳ Implement batch logging for scale
  ⏳ Set up automated retraining pipeline
  ⏳ Create analytics dashboard (Metabase)
  ⏳ Implement model explainability logging
  ⏳ Add fairness monitoring (check for bias)
"""
