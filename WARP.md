# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

**LifeOS-Tasks** is a personal task management system with a unique AI architecture philosophy: "Intelligence Without Authority." The system demonstrates that AI can suggest and understand patterns, but humans remain the sole authority over all decisions.

### Core Architecture Principle
```
raw_events → AI Suggester (advisory) → task_candidates → Human Review → tasks
```

**Critical Design Constraint**: AI suggestions NEVER bypass human approval. AI can only create `task_candidates` with `status='pending'`. Only explicit human action (approve/reject) creates actual tasks.

## Technology Stack

- **Backend**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Queue**: Redis (for background job processing)
- **AI Providers**: OpenAI (gpt-4o-mini), Anthropic (claude-3.5-sonnet), or none (optional)
- **Frontend**: Vanilla JavaScript + HTML/CSS (served as static files)

## Development Commands

### Setup
```bash
# Install core dependencies
pip install -e .

# Install with AI support (optional)
pip install -e ".[ai]"

# Copy environment template
cp .env.example .env

# Run database migrations
psql -U lifeos -d lifeos -f migrations/001_stage8_audit_and_lifecycle.sql
psql -U lifeos -d lifeos -f migrations/002_stage9_ai_suggestions.sql
```

### Running the Application
```bash
# Start API server (default: http://localhost:8000)
uvicorn app.main:app --reload

# Start background worker (separate terminal)
python -m app.worker

# Access web interface
# http://localhost:8000
```

### Testing
```bash
# Run manual acceptance tests (Stage 9 safety tests)
python tests/test_stage9_safety.py

# Note: These are manual integration tests, not automated unit tests
# Follow the printed instructions to verify each test case
```

### Database Operations
```bash
# Backup database before changes
pg_dump -U lifeos -d lifeos > backup_$(date +%Y%m%d_%H%M%S).sql

# Connect to database
psql -U lifeos -d lifeos

# Useful verification queries (see SYSTEM_INVARIANTS.md)
```

## Architecture Overview

### Core Components

**1. Data Flow Layers**
- `app/models/`: SQLAlchemy models (raw_event, summary, task_candidate, task, review_action, ai_suggestion)
- `app/core/`: Database connection, queue, logging, security utilities
- `app/ai/`: AI provider abstraction (protocol-based, swappable)
- `app/main.py`: FastAPI application with REST endpoints
- `app/worker.py`: Background event processor
- `static/`: Frontend (index.html, app.js, style.css)

**2. AI Provider Architecture**
The system uses a **Protocol-based** design pattern for AI providers:
- `app/ai/protocol.py`: Defines `AISuggester` interface
- `app/ai/factory.py`: Provider selection via environment config
- `app/ai/providers/`: OpenAI and Anthropic implementations
- `app/ai/contract.py`: AI response validation
- `app/ai/prompts.py`: PII redaction, prompt versioning

**Key Feature**: Switch AI providers by changing `AI_PROVIDER` env var only (openai | anthropic | none). No code changes, no migration needed.

**3. Database Tables & Relationships**
```
raw_events (inbox of all inputs)
    ↓
summaries (human-readable context)
task_candidates (AI or manual suggestions, status=pending/approved/rejected)
    ↓ (human approval)
tasks (authoritative task list, status=active/completed/archived)

review_actions (immutable audit ledger of all approve/reject decisions)
ai_suggestions (AI evidence: provider, model, rationale, confidence)
```

**Critical Constraint**: `UNIQUE INDEX idx_tasks_raw_event_unique ON tasks(raw_event_id)` prevents duplicate task creation (idempotency).

### System Invariants (MUST PRESERVE)

These are constitutional constraints enforced at database and application level:

1. **Idempotency**: A raw event can create at most one task (enforced by unique index)
2. **Traceability**: Every task traces to either a raw_event (AI-generated) or manual entry
3. **Auditability**: All approval/rejection decisions recorded immutably in `review_actions` (append-only)
4. **Transparency**: No silent mutations - every action has explicit response + UI feedback
5. **Reconstructibility**: All critical state persisted in PostgreSQL (not Redis/memory)
6. **AI Subordination**: AI cannot create, approve, or reject tasks autonomously

**See SYSTEM_INVARIANTS.md for enforcement details and verification queries.**

### AI Integration (Stage 9)

**Philosophy**: AI is OPTIONAL, ADVISORY, REPLACEABLE
- System works fully with `AI_PROVIDER=none`
- AI failures fall back to stub summarizer
- Humans approve 100% of tasks
- All suggestions logged with rationale/confidence

**Configuration** (via .env):
```bash
# Disable AI (default)
AI_PROVIDER=none

# Enable OpenAI
AI_PROVIDER=openai
AI_MODEL=gpt-4o-mini
OPENAI_API_KEY=sk-...

# Enable Anthropic
AI_PROVIDER=anthropic
AI_MODEL=claude-3-5-sonnet-20241022
ANTHROPIC_API_KEY=sk-ant-...
```

**AI Suggester Workflow** (in worker.py):
1. Raw event arrives (dictation/slack)
2. PII redaction applied (`redact_pii()`)
3. AI suggestion attempted (with timeout/retry limits)
4. Evidence persisted to `ai_suggestions` table
5. Task candidate created with link to AI record
6. On failure: graceful fallback to stub summarizer

### Semantic Memory (Stage 10) - DESIGNED, NOT IMPLEMENTED

Stage 10 is fully designed but deferred pending production data collection. Key principle: **Retrospective intelligence without feedback loops.**

**Capabilities** (when implemented):
- Semantic search (find similar tasks by meaning)
- Pattern recognition (detect recurring themes)
- Trend analysis (observe changes over time)
- AI performance insights (confidence vs approval correlation)

**Five Constitutional Invariants**:
1. All semantic memory is derivative (rebuildable)
2. All analysis is retrospective (never predictive)
3. No insight can mutate state (read-only)
4. No learned artifact can bypass review (one-way flow)
5. Semantic layers can be deleted without loss

**See STAGE10_README.md and STAGE10_ETHICS_AND_INVARIANTS.md for complete design.**

## Development Guidelines

### When Making Changes

**DO:**
- Preserve all six system invariants (see above)
- Log all AI failures with context
- Return explicit `{status, message}` from endpoints
- Use database constraints (not just application logic)
- Test idempotency (approve same candidate twice)
- Verify audit trail completeness

**DO NOT:**
- Allow AI to write to `tasks` table directly
- Create feedback loops (Stage 10 → Stage 9)
- Bypass human review for task creation
- Store secrets in code/commits (use .env)
- Delete audit records from `review_actions`
- Make silent state mutations

### Common Scenarios

**Adding a new AI provider:**
1. Implement `AISuggester` protocol in `app/ai/providers/`
2. Add provider to `get_suggester()` factory
3. Document env vars in `.env.example`
4. Test with manual acceptance tests

**Modifying task workflow:**
1. Check impact on system invariants
2. Ensure `review_actions` audit trail intact
3. Update relevant migration files
4. Test idempotency constraint

**Database schema changes:**
1. Create new migration in `migrations/`
2. Document rollback procedure
3. Update SYSTEM_INVARIANTS.md if constraints change
4. Backup before running

### Important Files Reference

| File | Purpose |
|------|---------|
| `SYSTEM_INVARIANTS.md` | Constitutional constraints (READ FIRST) |
| `AI_SYSTEM_DESIGN_SUMMARY.md` | Stage 9 & 10 philosophy and architecture |
| `STAGE9_SETUP.md` | Installation, configuration, troubleshooting |
| `.env.example` | Environment configuration template |
| `app/worker.py` | Background processing pipeline |
| `app/api_review.py` | Human review endpoints (approve/reject) |
| `app/ai/factory.py` | AI provider selection logic |
| `tests/test_stage9_safety.py` | Manual acceptance tests for Stage 9 axioms |

### Logging

Logging is configured via `LOG_LEVEL` environment variable (DEBUG | INFO | WARNING | ERROR | CRITICAL).

Key log patterns:
- `"AI suggestion successful"` - AI provider returned valid suggestion
- `"AI suggestion failed"` - AI provider error, falling back to stub
- `"Using stub summarizer"` - Fallback mode (AI disabled or failed)
- `"Worker started"` - Background processor running

### Security Notes

- PII redaction applied before sending text to AI (`redact_pii()` in prompts.py)
- API keys stored in `.env` only (never committed)
- Timeout enforcement: 10 seconds max per AI call
- Retry limits: 2 attempts max per suggestion
- Prompt versioning tracked (`CURRENT_PROMPT_VERSION`)

## Project Stage Evolution

- **Stage 8**: Audit & lifecycle (review_actions, task status, idempotency)
- **Stage 9**: AI suggestions (IMPLEMENTED) - advisory AI with human authority
- **Stage 10**: Semantic memory (DESIGNED, DEFERRED) - retrospective intelligence

Current status: Stage 9 complete, awaiting production deployment and data collection before Stage 10 implementation.
