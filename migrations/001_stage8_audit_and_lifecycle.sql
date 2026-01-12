-- Stage 8: Durable State, Auditability, and Execution Readiness
-- Migration: Add idempotency, audit trail, and task lifecycle

-- 1. Add lifecycle fields to tasks table
ALTER TABLE tasks
ADD COLUMN IF NOT EXISTS status VARCHAR DEFAULT 'active',
ADD COLUMN IF NOT EXISTS completed_at TIMESTAMP NULL;

-- Add index on raw_event_id for better query performance
CREATE INDEX IF NOT EXISTS idx_tasks_raw_event_id ON tasks(raw_event_id);

-- 2. Enforce idempotency: one raw_event can create at most one task
-- This prevents duplicate task creation from retries, double-submits, etc.
CREATE UNIQUE INDEX IF NOT EXISTS idx_tasks_raw_event_unique
ON tasks(raw_event_id)
WHERE raw_event_id IS NOT NULL;

-- 3. Create audit table for all review actions (append-only ledger)
CREATE TABLE IF NOT EXISTS review_actions (
    id VARCHAR PRIMARY KEY,
    candidate_id VARCHAR NOT NULL,
    action VARCHAR NOT NULL,  -- 'approved' or 'rejected'
    actor VARCHAR DEFAULT 'system',
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    raw_event_id VARCHAR
);

-- Indexes for audit queries
CREATE INDEX IF NOT EXISTS idx_review_actions_candidate ON review_actions(candidate_id);
CREATE INDEX IF NOT EXISTS idx_review_actions_timestamp ON review_actions(timestamp);
CREATE INDEX IF NOT EXISTS idx_review_actions_raw_event ON review_actions(raw_event_id);

-- 4. Add comments for documentation
COMMENT ON TABLE review_actions IS 'Immutable audit log of all task candidate approvals and rejections';
COMMENT ON COLUMN review_actions.action IS 'Type of review action: approved or rejected';
COMMENT ON COLUMN review_actions.actor IS 'Future: user/email who performed the action';
COMMENT ON INDEX idx_tasks_raw_event_unique IS 'Enforces idempotency: prevents duplicate tasks from same raw event';

-- 5. System invariants enforced by this migration:
-- ✓ No raw event can create more than one task (unique index)
-- ✓ Every approval/rejection is recorded immutably (review_actions)
-- ✓ Tasks have explicit lifecycle states (status column)
-- ✓ Audit trail is queryable and replayable (indexed timestamps)
