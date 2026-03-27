-- ============================================================================
-- BEIGE AI FEEDBACK LOGGING SYSTEM - PostgreSQL Schema
-- For Supabase
-- ============================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS uuid-ossp;

-- ============================================================================
-- MAIN FEEDBACK LOGS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS feedback_logs (
    -- Primary Key & Timestamps
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Session & User Tracking
    session_id TEXT NOT NULL,                      -- Unique per session
    user_id TEXT,                                  -- Optional: authenticated users
    
    -- User Input & Recommendation
    user_input JSONB NOT NULL,                     -- Full user input (mood, weather, preferences, etc.)
    recommended_cake TEXT NOT NULL,                -- Primary recommendation
    recommended_cakes_top_3 TEXT[] DEFAULT NULL,   -- Alternative recommendations
    
    -- User Feedback
    user_feedback INTEGER CHECK (user_feedback BETWEEN 1 AND 5),  -- 1=Poor, 5=Excellent
    feedback_notes TEXT,                           -- Optional: qualitative feedback
    
    -- Context & Environment
    context JSONB NOT NULL,                        -- {weather, mood, time_of_day, temperature, etc.}
    
    -- Model Versioning (CRITICAL FOR EXPERIMENTS)
    model_version TEXT NOT NULL,                   -- e.g., "hybrid_v1", "ml_seg_v2_2026-03-26"
    
    -- Performance Metrics
    latency_ms INTEGER,                            -- Inference time in milliseconds
    confidence_score FLOAT,                        -- ML confidence (0-1)
    
    -- ML Pipeline Metadata
    cluster_id INTEGER,                            -- Behavioral cluster assignment
    ml_features JSONB,                             -- Input features used by ML
    
    -- Training & Experimentation
    is_used_for_training BOOLEAN DEFAULT FALSE,   -- Flag for retraining pipeline
    experiment_id TEXT,                            -- Link to A/B test or experiment
    is_held_out BOOLEAN DEFAULT FALSE,             -- Holdout for evaluation
    
    -- Data Quality & Auditing
    is_valid BOOLEAN DEFAULT TRUE,                 -- Data quality flag
    error_message TEXT,                            -- If validation failed
    
    -- Constraints & Indexes
    CONSTRAINT valid_feedback CHECK (user_feedback IS NULL OR user_feedback BETWEEN 1 AND 5),
    CONSTRAINT valid_latency CHECK (latency_ms IS NULL OR latency_ms >= 0),
    CONSTRAINT valid_confidence CHECK (confidence_score IS NULL OR (confidence_score >= 0 AND confidence_score <= 1)),
    CONSTRAINT valid_cluster CHECK (cluster_id IS NULL OR cluster_id >= 0)
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Speed up session lookups
CREATE INDEX idx_feedback_logs_session_id 
ON feedback_logs(session_id);

-- Speed up model version analysis
CREATE INDEX idx_feedback_logs_model_version 
ON feedback_logs(model_version);

-- Speed up time-based queries
CREATE INDEX idx_feedback_logs_created_at 
ON feedback_logs(created_at DESC);

-- Composite index for A/B testing queries
CREATE INDEX idx_feedback_logs_model_created 
ON feedback_logs(model_version, created_at DESC);

-- Speed up feedback analysis
CREATE INDEX idx_feedback_logs_user_feedback 
ON feedback_logs(user_feedback)
WHERE user_feedback IS NOT NULL;

-- Speed up experiment analysis
CREATE INDEX idx_feedback_logs_experiment 
ON feedback_logs(experiment_id)
WHERE experiment_id IS NOT NULL;

-- ============================================================================
-- VIEW: MODEL PERFORMANCE COMPARISON
-- ============================================================================

CREATE OR REPLACE VIEW v_model_performance AS
SELECT 
    model_version,
    COUNT(*) as total_interactions,
    COUNT(user_feedback) as feedback_count,
    ROUND(AVG(user_feedback)::NUMERIC, 2) as avg_rating,
    ROUND(AVG(confidence_score)::NUMERIC, 4) as avg_confidence,
    ROUND(AVG(latency_ms)::NUMERIC, 2) as avg_latency_ms,
    MIN(created_at) as first_seen,
    MAX(created_at) as last_seen,
    COUNT(CASE WHEN is_used_for_training THEN 1 END) as training_count
FROM feedback_logs
WHERE is_valid = TRUE
GROUP BY model_version
ORDER BY last_seen DESC;

-- ============================================================================
-- VIEW: SESSION ANALYTICS
-- ============================================================================

CREATE OR REPLACE VIEW v_session_analytics AS
SELECT 
    session_id,
    COUNT(*) as interactions,
    COUNT(DISTINCT recommended_cake) as unique_cakes_recommended,
    COUNT(user_feedback) as feedback_count,
    ROUND(AVG(user_feedback)::NUMERIC, 2) as avg_rating,
    MAX(created_at) - MIN(created_at) as session_duration,
    ARRAY_AGG(DISTINCT model_version) as models_encountered
FROM feedback_logs
WHERE is_valid = TRUE
GROUP BY session_id
ORDER BY MAX(created_at) DESC;

-- ============================================================================
-- TABLE: MODEL VERSIONS (REFERENCE DATA)
-- ============================================================================

CREATE TABLE IF NOT EXISTS model_versions (
    id SERIAL PRIMARY KEY,
    version_name TEXT NOT NULL UNIQUE,
    version_type TEXT NOT NULL,  -- 'rule_based', 'ml_hybrid', 'ml_neural', etc.
    description TEXT,
    deployed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Performance baseline
    baseline_avg_rating FLOAT,
    baseline_latency_ms INTEGER,
    
    -- Rollback info
    previous_version TEXT,
    
    created_by TEXT,
    notes JSONB
);

-- ============================================================================
-- TABLE: A/B TEST EXPERIMENTS
-- ============================================================================

CREATE TABLE IF NOT EXISTS experiments (
    id SERIAL PRIMARY KEY,
    experiment_id TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    description TEXT,
    
    -- Variant versions being compared
    model_version_a TEXT NOT NULL REFERENCES model_versions(version_name),
    model_version_b TEXT NOT NULL REFERENCES model_versions(version_name),
    
    -- Experiment metadata
    start_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    end_date TIMESTAMP WITH TIME ZONE,
    sample_size INTEGER,
    
    -- Results
    winner TEXT,
    winner_metric FLOAT,
    is_completed BOOLEAN DEFAULT FALSE,
    
    created_by TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- PERMISSIONS (Optional: Row-level security)
-- ============================================================================

-- Enable RLS
ALTER TABLE feedback_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE model_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE experiments ENABLE ROW LEVEL SECURITY;

-- Create policy for authenticated users (example)
-- Note: Customize based on your auth setup
-- CREATE POLICY "Enable read for authenticated users"
--   ON feedback_logs FOR SELECT
--   USING (auth.role() = 'authenticated');

-- CREATE POLICY "Enable insert for authenticated users"
--   ON feedback_logs FOR INSERT
--   WITH CHECK (auth.role() = 'authenticated');

-- ============================================================================
-- SEEDING: Initial Model Versions
-- ============================================================================

INSERT INTO model_versions (version_name, version_type, description, is_active, created_by)
VALUES 
    ('hybrid_v1', 'ml_hybrid', '3-Layer Hybrid: Segmentation→Classification→Ranking', TRUE, 'system'),
    ('hybrid_v1_fallback', 'rule_based', 'Rule-based fallback (for testing)', FALSE, 'system')
ON CONFLICT (version_name) DO NOTHING;

-- ============================================================================
-- GRANTS (Customize for your Supabase project)
-- ============================================================================

-- Grant permissions to anon user (public)
-- GRANT SELECT ON feedback_logs TO anon;
-- GRANT INSERT ON feedback_logs TO anon;

-- Grant to authenticated users
-- GRANT SELECT, INSERT, UPDATE ON feedback_logs TO authenticated;
-- GRANT SELECT ON v_model_performance TO authenticated;
-- GRANT SELECT ON v_session_analytics TO authenticated;
