# LifeOS-Tasks System Invariants

## The Constitution of LifeOS-Tasks

These invariants are **enforced** at the database and application level. Violations are prevented by design, not by policy.

---

## 1. Idempotency: No Duplicate Tasks

**Invariant**: A raw event can create **at most one task**.

**Enforcement**:
- Database: `UNIQUE INDEX idx_tasks_raw_event_unique ON tasks(raw_event_id) WHERE raw_event_id IS NOT NULL`
- Application: `IntegrityError` handling in `api_review.py`

**Test**:
```python
# Approve same candidate twice
# Expected: Second attempt returns error "Task already exists for this event"
```

**Why it matters**: Prevents duplicate work from Slack retries, browser double-submits, worker restarts.

---

## 2. Traceability: Every Task Has a Source

**Invariant**: Every task must trace back to either:
- A raw event (AI-generated), OR
- Manual entry (user-created)

**Enforcement**:
- Database: `raw_event_id` field (nullable for manual tasks)
- UI: Display shows "AI-generated" or "manual" source

**Test**:
```sql
-- All tasks should have clear provenance
SELECT id, title, 
       CASE WHEN raw_event_id IS NULL THEN 'manual' ELSE 'AI-generated' END as source
FROM tasks;
```

**Why it matters**: Medical-legal defensibility, debugging, trust building.

---

## 3. Auditability: Every Decision is Recorded

**Invariant**: Every approval/rejection is recorded **immutably** in the audit ledger.

**Enforcement**:
- Database: Append-only `review_actions` table
- Application: Audit record created **before** task creation
- No DELETE or UPDATE operations on `review_actions`

**Test**:
```sql
-- Every candidate should have an audit trail
SELECT ra.action, ra.timestamp, tc.title, tc.status
FROM review_actions ra
JOIN task_candidates tc ON ra.candidate_id = tc.id
ORDER BY ra.timestamp DESC
LIMIT 10;
```

**Why it matters**: 
- Replayability (reconstruct system state)
- Analytics ("What % of AI suggestions are rejected?")
- Compliance and legal defensibility

---

## 4. Transparency: No Silent Mutations

**Invariant**: No UI action mutates state silently.

**Enforcement**:
- Backend: Every endpoint returns explicit `{status, message}` response
- Frontend: Toast notifications for every action
- Visual feedback: Processing states, strike-throughs, badges

**Test**:
```javascript
// Every mutation should show toast
// approve() → "Task created successfully"
// reject() → "Candidate dismissed"
// complete() → "Task marked as complete"
```

**Why it matters**: User trust, debugging, preventing confusion.

---

## 5. Reconstructibility: Database is Source of Truth

**Invariant**: System state can be **completely rebuilt** from the database.

**Enforcement**:
- All state mutations are persisted
- Timestamped events enable replay
- No critical state in Redis or memory only

**Test**:
```bash
# Stop all services
# Drop Redis
# Restart API server
# Expected: All tasks, candidates, and history are intact
```

**Why it matters**: 
- Disaster recovery
- Migration to new infrastructure
- Debugging production issues

---

## Verification Commands

### Check Idempotency Protection
```sql
SELECT indexname, indexdef 
FROM pg_indexes 
WHERE indexname = 'idx_tasks_raw_event_unique';
```

### Audit Trail Completeness
```sql
SELECT 
  COUNT(*) as total_actions,
  COUNT(DISTINCT candidate_id) as unique_candidates,
  action,
  COUNT(*) as count_per_action
FROM review_actions
GROUP BY action;
```

### Task Lifecycle Distribution
```sql
SELECT status, COUNT(*) as count
FROM tasks
GROUP BY status;
```

### Source Attribution Coverage
```sql
SELECT 
  CASE WHEN raw_event_id IS NULL THEN 'manual' ELSE 'AI-generated' END as source,
  COUNT(*) as count
FROM tasks
GROUP BY source;
```

---

## Invariant Violations (Should Never Happen)

| Violation | Detection | Response |
|-----------|-----------|----------|
| Duplicate task from same event | `IntegrityError` on insert | Return error to user, log warning |
| Approval without audit record | Query mismatch | **System bug** - requires investigation |
| Task without source attribution | `raw_event_id` NULL check | Allowed (manual tasks) |
| Silent mutation | Missing toast notification | **UI bug** - requires fix |
| Lost state on restart | Missing data after reboot | **Critical bug** - data loss |

---

## Design Principles Behind These Invariants

1. **Trust by Default, Verify Always**
   - Assume good intent, but enforce correctness at system level

2. **Explicit Over Implicit**
   - No hidden state changes, no silent failures

3. **Immutable History**
   - Events are append-only, never mutated or deleted

4. **Database as Judge**
   - Constraints enforced by PostgreSQL, not application logic

5. **Human Authority**
   - AI suggests, humans decide, audit log records

---

## When to Update These Invariants

Update this document when:
- New tables are added
- New constraints are enforced
- Invariants are relaxed (rare, requires justification)
- System architecture fundamentally changes

## 6. AI Subordination: AI Cannot Create, Approve, or Reject Tasks

**Invariant**: AI suggestions are advisory only. AI cannot autonomously create, approve, or reject tasks.

**Enforcement**:
- Worker: AI only creates `task_candidates` with `status='pending'`
- Review API: Requires explicit human action (approve/reject endpoints)
- Database: `ai_suggestions` has no foreign key to `tasks` table
- Architecture: AI suggestions → task_candidates → human review → tasks

**Test**:
```sql
-- Verify no tasks were created without human approval
SELECT t.id, t.title
FROM tasks t
LEFT JOIN review_actions ra ON ra.raw_event_id = t.raw_event_id
WHERE ra.id IS NULL;
-- Should return 0 rows (all tasks have corresponding review_action)
```

**Why it matters**: 
- Maintains human authority over all task creation
- AI failures don't create bad tasks
- Legal/medical defensibility (human-in-the-loop)
- Prevents autonomous AI behavior

---

**Last Updated**: Stage 9 implementation
