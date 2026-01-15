-- Initial Schema: Create base tables for LifeOS-Tasks
-- This must run before other migrations

-- 1. Raw Events (inbox of all inputs)
CREATE TABLE IF NOT EXISTS raw_events (
    id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid()::text,
    source VARCHAR NOT NULL,
    payload TEXT NOT NULL,
    received_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    processed BOOLEAN DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_raw_events_received ON raw_events(received_at);
CREATE INDEX IF NOT EXISTS idx_raw_events_processed ON raw_events(processed);

-- 2. Summaries (human-readable context)
CREATE TABLE IF NOT EXISTS summaries (
    id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid()::text,
    raw_event_id VARCHAR REFERENCES raw_events(id),
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_summaries_raw_event ON summaries(raw_event_id);

-- 3. Tasks (authoritative task list)
CREATE TABLE IF NOT EXISTS tasks (
    id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid()::text,
    title VARCHAR NOT NULL,
    description TEXT DEFAULT '',
    priority VARCHAR DEFAULT 'medium',
    status VARCHAR DEFAULT 'active',
    raw_event_id VARCHAR REFERENCES raw_events(id),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL
);

CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_created ON tasks(created_at);

-- 4. Task Candidates (pending approval)
CREATE TABLE IF NOT EXISTS task_candidates (
    id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid()::text,
    raw_event_id VARCHAR REFERENCES raw_events(id),
    title VARCHAR NOT NULL,
    description TEXT DEFAULT '',
    priority VARCHAR DEFAULT 'medium',
    status VARCHAR DEFAULT 'pending',
    ai_suggestion_id VARCHAR,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_task_candidates_status ON task_candidates(status);
CREATE INDEX IF NOT EXISTS idx_task_candidates_raw_event ON task_candidates(raw_event_id);

-- Comments
COMMENT ON TABLE raw_events IS 'Inbox: all inputs from dictation, Slack, and manual entry';
COMMENT ON TABLE summaries IS 'Human-readable summaries of raw events';
COMMENT ON TABLE tasks IS 'Authoritative task list - only humans can create tasks here';
COMMENT ON TABLE task_candidates IS 'Pending suggestions awaiting human approval';
