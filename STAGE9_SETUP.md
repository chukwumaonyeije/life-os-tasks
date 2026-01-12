# Stage 9 Setup Guide

## Installation

### 1. Install Core Dependencies
```bash
pip install -e .
```

### 2. Install AI Dependencies (Optional)
```bash
# For OpenAI support
pip install -e ".[ai]"

# Or install providers individually
pip install openai>=1.0
pip install anthropic>=0.18
```

## Configuration

### 1. Copy Environment Template
```bash
cp .env.example .env
```

### 2. Configure AI Provider

**Option A: Disable AI (Default)**
```bash
AI_PROVIDER=none
```
System remains fully functional without AI.

**Option B: Enable OpenAI**
```bash
AI_PROVIDER=openai
AI_MODEL=gpt-4o-mini
OPENAI_API_KEY=sk-your-key-here
```

**Option C: Enable Anthropic Claude**
```bash
AI_PROVIDER=anthropic
AI_MODEL=claude-3-5-sonnet-20241022
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

## Database Migration

### 1. Backup Database
```bash
pg_dump -U lifeos -d lifeos > backup_pre_stage9.sql
```

### 2. Run Migration
```bash
psql -U lifeos -d lifeos -f migrations/002_stage9_ai_suggestions.sql
```

### 3. Verify Migration
```bash
psql -U lifeos -d lifeos -c "SELECT table_name FROM information_schema.tables WHERE table_name = 'ai_suggestions';"
```

## Running the System

### 1. Start API Server
```bash
uvicorn app.main:app --reload
```

### 2. Start Worker
```bash
python -m app.worker
```

### 3. Access Web Interface
```
http://localhost:8000
```

## Testing AI Integration

### 1. Test with AI Disabled
```bash
AI_PROVIDER=none python -m app.worker
```
Expected: Worker uses stub summarizer (existing behavior).

### 2. Test with AI Enabled
```bash
AI_PROVIDER=openai
OPENAI_API_KEY=sk-...
python -m app.worker
```
Expected: Worker attempts AI suggestion, falls back to stub on failure.

### 3. Verify AI Metadata
1. Create dictation event via UI
2. Check review queue
3. Look for purple AI badge with provider/model
4. Expand "Why suggested" rationale

## Troubleshooting

### AI Dependencies Not Installed
```
WARNING: AI provider 'openai' dependencies not installed
INFO: To enable openai, install with: pip install openai
```
**Solution:** Run `pip install -e ".[ai]"`

### API Key Not Set
```
ValueError: OPENAI_API_KEY environment variable not set
```
**Solution:** Add API key to `.env` file

### AI Timeout/Failure
```
ERROR: AI suggestion failed for event_id: timeout
INFO: Using stub summarizer for event_id
```
**Expected behavior** - system continues with stub.

### No AI Badge Showing
- Check `AI_PROVIDER` is not `none`
- Check API key is valid
- Check worker logs for AI suggestion success
- Verify `ai_suggestions` table has records

## Provider Switching

To switch providers (zero code changes):

```bash
# In .env file
AI_PROVIDER=anthropic  # was: openai
AI_MODEL=claude-3-5-sonnet-20241022
ANTHROPIC_API_KEY=sk-ant-...
```

Restart worker. No database migration needed.

## Verification Queries

### Count AI vs Manual Candidates
```sql
SELECT 
  CASE WHEN ai_suggestion_id IS NULL THEN 'manual' ELSE 'AI' END as source,
  COUNT(*) as count
FROM task_candidates
GROUP BY source;
```

### View AI Suggestions
```sql
SELECT provider, model, rationale, created_at
FROM ai_suggestions
ORDER BY created_at DESC
LIMIT 10;
```

### Provider Performance
```sql
SELECT 
  provider,
  COUNT(*) as suggestions,
  AVG((suggestion_json->>'confidence')::float) as avg_confidence
FROM ai_suggestions
GROUP BY provider;
```

## Security Checklist

- [ ] Never commit `.env` to version control
- [ ] API keys stored in environment only
- [ ] PII redaction enabled before AI calls
- [ ] Timeout enforcement (10 seconds)
- [ ] Prompt versioning in place

## Stage 9 Axioms Verified

- [ ] System works with `AI_PROVIDER=none`
- [ ] Humans approve all tasks (no auto-approve)
- [ ] Provider swap = change env var only
- [ ] AI downtime doesn't break system
- [ ] All suggestions traceable in database
- [ ] Rationale visible to humans
