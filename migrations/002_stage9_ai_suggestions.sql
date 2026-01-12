-- Stage 9: AI as a Replaceable Suggestion Engine
-- Migration: Add ai_suggestions evidence table and enhance task_candidates

-- 1. Create ai_suggestions table (evidence, not workflow)
CREATE TABLE IF NOT EXISTS ai_suggestions (
    id VARCHAR PRIMARY KEY,
    raw_event_id VARCHAR NOT NULL,
    provider VARCHAR NOT NULL,         -- openai | anthropic | local
    model VARCHAR NOT NULL,             -- gpt-4o-mini, claude-3.5-sonnet, etc.
    prompt_version VARCHAR NOT NULL,    -- v1, v2, etc.
    input_excerpt TEXT NOT NULL,        -- first 500 chars for replay
    suggestion_json JSONB NOT NULL,     -- structured proposal
    rationale TEXT NOT NULL,            -- human-readable explanation
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 2. Indexes for ai_suggestions queries
CREATE INDEX IF NOT EXISTS idx_ai_suggestions_raw_event 
ON ai_suggestions(raw_event_id);

CREATE INDEX IF NOT EXISTS idx_ai_suggestions_provider 
ON ai_suggestions(provider);

CREATE INDEX IF NOT EXISTS idx_ai_suggestions_created 
ON ai_suggestions(created_at);

-- 3. Add fields to task_candidates for AI integration
ALTER TABLE task_candidates
ADD COLUMN IF NOT EXISTS priority VARCHAR DEFAULT 'medium',
ADD COLUMN IF NOT EXISTS ai_suggestion_id VARCHAR NULL;

-- 4. Index for task_candidates linkage
CREATE INDEX IF NOT EXISTS idx_task_candidates_ai_suggestion 
ON task_candidates(ai_suggestion_id);

-- 5. Add comments for documentation
COMMENT ON TABLE ai_suggestions IS 'Immutable evidence log of all AI-generated task suggestions. Advisory only, not authoritative.';
COMMENT ON COLUMN ai_suggestions.provider IS 'AI provider used: openai, anthropic, or local';
COMMENT ON COLUMN ai_suggestions.prompt_version IS 'Prompt template version for replay and debugging';
COMMENT ON COLUMN ai_suggestions.suggestion_json IS 'Complete AI response as JSONB for structured queries';
COMMENT ON COLUMN ai_suggestions.rationale IS 'Human-readable explanation of why AI suggested this task';
COMMENT ON COLUMN task_candidates.ai_suggestion_id IS 'Links to ai_suggestions if AI-generated, NULL if manual';
COMMENT ON COLUMN task_candidates.priority IS 'Task priority: low, medium, or high';

-- 6. System invariants enforced by this migration:
-- ✓ AI suggestions are evidence only (separate table from workflow)
-- ✓ Task candidates can exist without AI suggestions (NULL ai_suggestion_id)
-- ✓ All AI suggestions are traceable to raw events
-- ✓ Prompt versions enable replay and debugging
-- ✓ Provider abstraction enforced (no provider-specific columns)

-- 7. Verification queries
-- Check ai_suggestions table exists:
-- SELECT table_name FROM information_schema.tables WHERE table_name = 'ai_suggestions';

-- Verify task_candidates enhancements:
-- SELECT column_name, data_type, is_nullable 
-- FROM information_schema.columns 
-- WHERE table_name = 'task_candidates' 
-- AND column_name IN ('priority', 'ai_suggestion_id');

-- Count AI vs manual candidates:
-- SELECT 
--   CASE WHEN ai_suggestion_id IS NULL THEN 'manual' ELSE 'AI-generated' END as source,
--   COUNT(*) as count
-- FROM task_candidates
-- GROUP BY source;
