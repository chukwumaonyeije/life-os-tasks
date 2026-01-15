# CLAUDE.md - LifeOS-Tasks

## Project Overview

LifeOS-Tasks is a personal task management system built on the **"Intelligence Without Authority"** philosophy. AI can suggest and understand patterns, but humans remain the sole authority over all decisions.

## Architecture Summary

```
Raw Events (dictation/Slack/manual)
    ↓
PII Redaction
    ↓
AI Suggester (advisory, optional)
    ↓
Task Candidates (pending approval)
    ↓
Human Review (approve/reject)
    ↓
Authoritative Tasks
    ↓
Audit Log (immutable review_actions)
```

**Critical Constraint**: AI NEVER writes directly to `tasks` table. It only creates `task_candidates` with `status='pending'`. Only explicit human action creates actual tasks.

## Tech Stack

- **Backend**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL + SQLAlchemy ORM
- **Queue**: Redis
- **AI Providers**: OpenAI (gpt-4o-mini), Anthropic (claude-3.5-sonnet), or none
- **Frontend**: Vanilla JavaScript + HTML/CSS

## Project Structure

```
app/
├── main.py              # FastAPI bootstrap, routes
├── worker.py            # Background event processor
├── ingest_dictation.py  # Dictation ingestion endpoint
├── ingest_slack.py      # Slack ingestion endpoint
├── api_review.py        # Review queue endpoints
├── models/              # SQLAlchemy ORM models
│   ├── raw_event.py     # Inbox of all inputs
│   ├── task.py          # Authoritative tasks
│   ├── task_candidate.py # AI/manual suggestions (pending)
│   ├── ai_suggestion.py # Audit evidence for AI
│   ├── review_action.py # Immutable audit ledger
│   └── summary.py       # Human-readable context
├── core/                # Infrastructure utilities
│   ├── db.py            # Database connection
│   ├── queue.py         # Redis queue operations
│   ├── security.py      # Slack signature verification
│   ├── summarizer.py    # Fallback stub summarizer
│   └── logging_config.py
└── ai/                  # AI provider abstraction
    ├── protocol.py      # AISuggester interface
    ├── factory.py       # Provider factory
    ├── contract.py      # Output validation
    ├── prompts.py       # Versioned prompts, PII redaction
    └── providers/
        ├── openai_suggester.py
        └── claude_suggester.py
static/                  # Frontend
migrations/              # SQL migrations
tests/                   # Acceptance tests
```

## Local Development with Docker

```bash
# Start PostgreSQL and Redis
docker-compose up -d

# Stop services
docker-compose down

# Stop and remove volumes (reset database)
docker-compose down -v
```

Migrations in `migrations/` run automatically on first start.

Default connection: `postgresql://lifeos:lifeos@localhost:5432/lifeos`

## Key Commands

```bash
# Install dependencies
pip install -e .                      # Core only
pip install -e ".[ai]"                # With AI support

# Start API server
uvicorn app.main:app --reload

# Start background worker (separate terminal)
python -m app.worker

# Run tests
pytest tests/
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `AI_PROVIDER` - `openai` | `anthropic` | `none`
- `AI_MODEL` - Provider-specific model name
- `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` - API credentials
- `LOG_LEVEL` - DEBUG | INFO | WARNING | ERROR | CRITICAL
- `SLACK_SIGNING_SECRET` - For Slack integration

## System Invariants (Never Break These)

1. **Idempotency**: One raw event → at most one task
2. **Traceability**: Every task traces to a source
3. **Auditability**: Every approval/rejection recorded immutably
4. **Transparency**: No silent mutations
5. **Reconstructibility**: Database is single source of truth
6. **AI Subordination**: AI cannot create, approve, or reject tasks

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/` | Frontend UI |
| POST | `/ingest/dictation` | Accept dictation input |
| POST | `/ingest/slack/events` | Slack integration |
| GET | `/api/review` | Get pending task candidates |
| POST | `/api/review/{id}/approve` | Approve candidate → create task |
| POST | `/api/review/{id}/reject` | Reject candidate |
| GET | `/api/review/approved` | Recently approved candidates |

## Development Notes

- AI provider is swappable via env var without code changes
- System works fully with `AI_PROVIDER=none`
- PII is redacted before sending to AI providers
- All AI failures gracefully fall back to stub summarizer
- The `review_actions` table is append-only (audit log)

## Current Status

- **Stage 8** ✅ Audit & lifecycle
- **Stage 9** ✅ AI suggestions
- **Stage 10** 🏗️ Semantic memory (designed, awaiting production data)
