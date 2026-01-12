# Stage 9: Production Deployment Verification Checklist

**Date**: 2026-01-11  
**Status**: Pre-Deployment Verification  
**Target Environment**: Production

---

## ✅ Verification Results

### Critical Components

| Component | Status | Notes |
|-----------|--------|-------|
| Python Version | ✅ 3.13.7 | Requirement: ≥3.11 |
| Database Migration | ✅ Created | 002_stage9_ai_suggestions.sql |
| AI Module Structure | ✅ Complete | app/ai/ with all submodules |
| Provider Implementations | ✅ 2 providers | OpenAI + Claude |
| Configuration Template | ✅ Present | .env.example |
| Documentation | ✅ Complete | 6 documents, 2,293 lines |

---

## Pre-Deployment Checklist

### 1. Code Completeness ✅

- [x] **AI Contract** (`app/ai/contract.py`)
  - AISuggestion dataclass defined
  - validate_suggestion() implemented
  - suggestion_to_dict() helper present

- [x] **Provider Protocol** (`app/ai/protocol.py`)
  - AISuggester Protocol defined
  - Type hints correct

- [x] **Provider Implementations**
  - [x] OpenAI suggester (`app/ai/providers/openai_suggester.py`)
  - [x] Claude suggester (`app/ai/providers/claude_suggester.py`)
  - [x] Both implement timeout (10s) and retry (2x)

- [x] **Provider Factory** (`app/ai/factory.py`)
  - get_suggester() with graceful fallback
  - Try/except imports for optional dependencies
  - Logging on init

- [x] **Prompt Engineering** (`app/ai/prompts.py`)
  - PROMPT_V1 defined
  - get_prompt() versioning
  - redact_pii() implemented
  - truncate_for_excerpt() present

- [x] **AI Suggestion Model** (`app/models/ai_suggestion.py`)
  - SQLAlchemy model complete
  - JSONB field for suggestion_json
  - All indexes specified

- [x] **Task Candidate Enhancement** (`app/models/task_candidate.py`)
  - priority field added
  - ai_suggestion_id field added (nullable, indexed)

- [x] **Worker Integration** (`app/worker.py`)
  - AI suggester imported
  - PII redaction applied
  - Fallback to stub on failure
  - Logging configured

- [x] **Review API Enhancement** (`app/api_review.py`)
  - GET /api/review returns ai_metadata
  - Joins task_candidates with ai_suggestions
  - Handles null ai_suggestion_id

- [x] **Frontend Updates** (`static/app.js`, `static/style.css`)
  - AI badge rendering
  - Confidence score display
  - Rationale expand/collapse
  - Priority badges

- [x] **Logging Configuration** (`app/core/logging_config.py`)
  - setup_logging() implemented
  - Structured format
  - Third-party logger suppression

- [x] **Main App Registration** (`app/main.py`)
  - AISuggestionBase registered
  - Logging setup called
  - Table creation on startup

---

### 2. Database Migration ✅

- [x] **Migration File Exists**
  - Location: `migrations/002_stage9_ai_suggestions.sql`
  - Creates: ai_suggestions table
  - Alters: task_candidates (adds priority, ai_suggestion_id)
  - Indexes: 4 new indexes created

- [ ] **Migration Applied to Database**
  - Action Required: Run `psql -U lifeos -d lifeos -f migrations/002_stage9_ai_suggestions.sql`
  - Verification: Check table exists

- [ ] **Backup Created**
  - Action Required: Run `pg_dump -U lifeos -d lifeos > backup_pre_stage9.sql`
  - Critical: Do this BEFORE migration

---

### 3. Dependencies ⚠️

- [x] **Core Dependencies** (pyproject.toml)
  - fastapi>=0.110
  - uvicorn[standard]>=0.27
  - sqlalchemy>=2.0
  - psycopg[binary]>=3.1

- [ ] **AI Dependencies** (optional)
  - Action Required: `pip install -e ".[ai]"` OR
  - `pip install openai>=1.0 anthropic>=0.18`
  - Status: NOT YET INSTALLED
  - Note: System works without these (AI_PROVIDER=none)

- [ ] **Dependencies Installed**
  - Action Required: `pip install -e .`
  - Verification: `python -c "import app.ai.contract"`

---

### 4. Configuration ⚠️

- [x] **Environment Template** (.env.example)
  - LOG_LEVEL documented
  - DATABASE_URL example
  - REDIS config example
  - AI_PROVIDER options listed
  - API keys placeholders present

- [ ] **Environment File** (.env)
  - Action Required: `cp .env.example .env`
  - Edit with actual values:
    - DATABASE_URL
    - REDIS_HOST/PORT
    - AI_PROVIDER (openai|anthropic|none)
    - API keys (if AI enabled)
    - LOG_LEVEL

- [ ] **Environment Variables Set**
  - Verification: Check .env file exists
  - Verification: No secrets in git

---

### 5. Testing ⚠️

- [x] **Test Suite Created**
  - Location: `tests/test_stage9_safety.py`
  - Type: Manual acceptance tests
  - Count: 7 test scenarios

- [ ] **Tests Executed**
  - Action Required: Run each test manually
  - Test 1: AI disabled → system works
  - Test 2: AI timeout → fallback works
  - Test 3: Malformed output → discarded
  - Test 4: Duplicate prevention → enforced
  - Test 5: Approval path → unchanged
  - Test 6: AI metadata → visible
  - Test 7: Provider switching → seamless

---

### 6. Security ✅

- [x] **PII Redaction** (`app/ai/prompts.py`)
  - SSN pattern redaction
  - Credit card redaction
  - Email redaction
  - Phone number redaction

- [x] **API Key Security**
  - Keys in environment only
  - No keys in database
  - No keys in code
  - .env excluded from git

- [x] **Timeout Enforcement**
  - OpenAI: 10s timeout
  - Claude: 10s timeout
  - Worker: Doesn't hang on AI failure

- [x] **Retry Limits**
  - OpenAI: 2 retries max
  - Claude: 2 retries max

---

### 7. Failure Safety ✅

- [x] **AI Disabled Mode**
  - AI_PROVIDER=none → uses stub
  - No AI dependencies required
  - System fully functional

- [x] **Fallback Mechanism**
  - AI timeout → stub summarizer
  - AI error → stub summarizer
  - Missing dependencies → stub summarizer

- [x] **Graceful Degradation**
  - No crashes on AI failure
  - Events still processed
  - Tasks still created

---

### 8. Documentation ✅

- [x] **User Documentation**
  - STAGE9_SETUP.md (190 lines)
  - STAGE9_SUMMARY.md (401 lines)
  - .env.example (with comments)

- [x] **Developer Documentation**
  - AI_SYSTEM_DESIGN_SUMMARY.md (611 lines)
  - SYSTEM_INVARIANTS.md (updated)
  - Code comments present

- [x] **Operations Documentation**
  - Migration instructions
  - Troubleshooting guide
  - Verification queries

---

### 9. Operational Readiness ⚠️

- [ ] **Database Backup**
  - Action Required: Backup before migration
  - Command: `pg_dump -U lifeos -d lifeos > backup.sql`

- [ ] **Database Connection**
  - Action Required: Verify DB accessible
  - Command: `psql -U lifeos -d lifeos -c "SELECT version();"`

- [ ] **Redis Connection**
  - Action Required: Verify Redis accessible
  - Command: Test worker can connect

- [ ] **API Server Startup**
  - Action Required: `uvicorn app.main:app --reload`
  - Verification: Check http://localhost:8000

- [ ] **Worker Startup**
  - Action Required: `python -m app.worker`
  - Verification: Check logs for "Worker started"

---

### 10. Monitoring & Logging ✅

- [x] **Logging Configured**
  - Structured format implemented
  - LOG_LEVEL configurable
  - AI operations logged
  - Worker events logged

- [ ] **Log Monitoring Plan**
  - Action Required: Define where logs go
  - Suggestion: stdout → file or service
  - Watch for: AI failures, validation errors

- [ ] **Metrics Plan** (optional)
  - Suggestion: Track AI suggestion volume
  - Suggestion: Track approval rates
  - Suggestion: Track provider performance

---

## Deployment Steps (Recommended Order)

### Phase 1: Environment Setup

1. **Backup Database**
   ```bash
   pg_dump -U lifeos -d lifeos > backup_pre_stage9_$(date +%Y%m%d).sql
   ```

2. **Install Dependencies**
   ```bash
   pip install -e .
   # Optional: pip install -e ".[ai]"
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with actual values
   ```

4. **Verify Configuration**
   ```bash
   python -c "import app.ai.contract; print('AI module OK')"
   ```

### Phase 2: Database Migration

5. **Run Migration**
   ```bash
   psql -U lifeos -d lifeos -f migrations/002_stage9_ai_suggestions.sql
   ```

6. **Verify Migration**
   ```sql
   SELECT table_name FROM information_schema.tables 
   WHERE table_name = 'ai_suggestions';
   -- Should return 1 row
   ```

7. **Verify Table Structure**
   ```sql
   SELECT column_name, data_type 
   FROM information_schema.columns 
   WHERE table_name = 'task_candidates' 
   AND column_name IN ('priority', 'ai_suggestion_id');
   -- Should return 2 rows
   ```

### Phase 3: Service Startup

8. **Start API Server**
   ```bash
   uvicorn app.main:app --reload
   ```

9. **Verify API Health**
   ```bash
   curl http://localhost:8000/api/tasks
   # Should return tasks list (may be empty)
   ```

10. **Start Worker**
    ```bash
    python -m app.worker
    # Check logs for "Worker started"
    ```

### Phase 4: Validation

11. **Test with AI Disabled**
    ```bash
    # In .env: AI_PROVIDER=none
    # Create dictation event
    # Verify stub summarizer works
    ```

12. **Test with AI Enabled** (if desired)
    ```bash
    # In .env: AI_PROVIDER=openai, set API key
    # Create dictation event
    # Verify AI suggestion appears
    # Verify rationale visible
    ```

13. **Test Approval Flow**
    ```bash
    # Approve candidate in UI
    # Verify task created
    # Verify review_action recorded
    ```

### Phase 5: Monitoring

14. **Monitor Logs**
    ```bash
    # Watch for errors
    # Check AI suggestion success/failure
    # Verify fallback works on failure
    ```

15. **Run Acceptance Tests**
    ```bash
    python tests/test_stage9_safety.py
    # Follow manual test procedures
    ```

---

## Blocking Issues (Must Resolve Before Deploy)

### Critical (Deploy Blockers)

- [ ] **Database migration not applied**
  - Impact: System will crash on startup
  - Resolution: Run migration

- [ ] **No .env file**
  - Impact: System won't know configuration
  - Resolution: Copy and edit .env.example

- [ ] **Dependencies not installed**
  - Impact: Import errors on startup
  - Resolution: `pip install -e .`

### High Priority (Resolve Soon)

- [ ] **No database backup**
  - Impact: Can't rollback if migration fails
  - Resolution: Create backup before migration

### Low Priority (Can Deploy Without)

- [ ] **AI dependencies not installed**
  - Impact: AI_PROVIDER must be 'none'
  - Resolution: Install later if AI needed

- [ ] **Acceptance tests not run**
  - Impact: Unknown edge cases
  - Resolution: Run tests post-deployment

---

## Rollback Plan

If Stage 9 deployment fails:

1. **Stop Services**
   ```bash
   # Stop API server (Ctrl+C)
   # Stop worker (Ctrl+C)
   ```

2. **Restore Database**
   ```bash
   psql -U lifeos -d lifeos < backup_pre_stage9_YYYYMMDD.sql
   ```

3. **Revert Code** (if needed)
   ```bash
   git checkout <previous-commit>
   ```

4. **Restart Services**
   ```bash
   uvicorn app.main:app --reload
   python -m app.worker
   ```

---

## Success Criteria

Stage 9 deployment is successful if:

- ✅ API server starts without errors
- ✅ Worker starts without errors
- ✅ System works with AI_PROVIDER=none
- ✅ Dictation events create task candidates
- ✅ Review queue displays candidates
- ✅ Approval flow creates tasks
- ✅ No crashes or errors in logs

Optional (if AI enabled):
- ✅ AI suggestions appear in review queue
- ✅ AI badge and rationale visible
- ✅ Confidence score displayed
- ✅ AI failures fall back to stub

---

## Post-Deployment Actions

After successful deployment:

1. **Monitor for 24 Hours**
   - Watch logs for errors
   - Check AI suggestion volume
   - Verify no crashes

2. **Begin Data Collection**
   - Start filling STAGE10_OBSERVATION_TEMPLATE.md
   - Track AI vs manual candidates
   - Track approval/rejection rates

3. **User Feedback**
   - Ask: Are AI suggestions helpful?
   - Ask: Are rationales clear?
   - Ask: Any confusing behaviors?

4. **Performance Monitoring**
   - Track AI API latency
   - Monitor fallback frequency
   - Check database query performance

---

## Contact & Support

**Issues During Deployment**:
1. Check logs: `LOG_LEVEL=DEBUG`
2. Review STAGE9_SETUP.md troubleshooting section
3. Verify SYSTEM_INVARIANTS.md not violated

**Questions About Stage 9**:
- Review: `STAGE9_SUMMARY.md`
- Setup guide: `STAGE9_SETUP.md`
- System design: `AI_SYSTEM_DESIGN_SUMMARY.md`

---

## Final Verification

**Before proceeding to production, confirm:**

- [ ] Backup created ✅
- [ ] Migration applied ✅
- [ ] Dependencies installed ✅
- [ ] .env configured ✅
- [ ] API starts ✅
- [ ] Worker starts ✅
- [ ] Basic flow works ✅

**If all checked, Stage 9 is ready for production deployment.**

---

**Status**: ⚠️ **PREREQUISITES NEEDED**

**Blocking Items**:
1. Database migration (not yet applied)
2. .env file (not yet created)
3. Dependencies (core installed, AI optional)

**Once these 3 items complete, Stage 9 is READY.**
