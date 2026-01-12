# Database Migrations

This directory contains SQL migration scripts for the LifeOS-Tasks database schema.

## Running Migrations

### Prerequisites
- PostgreSQL database running
- Connection credentials configured
- Database `lifeos` created

### Execute Migration

```bash
# Using psql
psql -U lifeos -d lifeos -f migrations/001_stage8_audit_and_lifecycle.sql

# Or with connection string
psql postgresql://lifeos:lifeos@localhost:5432/lifeos -f migrations/001_stage8_audit_and_lifecycle.sql
```

### Verify Migration

```sql
-- Check for new columns
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'tasks' AND column_name IN ('status', 'completed_at');

-- Check for review_actions table
SELECT * FROM information_schema.tables WHERE table_name = 'review_actions';

-- Verify unique index exists
SELECT indexname, indexdef 
FROM pg_indexes 
WHERE tablename = 'tasks' AND indexname = 'idx_tasks_raw_event_unique';
```

## Migration History

### 001_stage8_audit_and_lifecycle.sql
**Date**: Stage 8 implementation  
**Purpose**: Add durable state, auditability, and execution readiness

**Changes**:
- Added `status` and `completed_at` to tasks table
- Created `review_actions` audit table
- Added unique index for idempotency (`idx_tasks_raw_event_unique`)
- Added performance indexes

**Rollback** (if needed):
```sql
-- Remove new columns
ALTER TABLE tasks DROP COLUMN IF EXISTS status;
ALTER TABLE tasks DROP COLUMN IF EXISTS completed_at;

-- Drop audit table
DROP TABLE IF EXISTS review_actions;

-- Drop indexes
DROP INDEX IF EXISTS idx_tasks_raw_event_unique;
DROP INDEX IF EXISTS idx_tasks_raw_event_id;
```

## Best Practices

1. **Always backup before migration**:
   ```bash
   pg_dump -U lifeos lifeos > backup_$(date +%Y%m%d_%H%M%S).sql
   ```

2. **Test migrations on dev/staging first**

3. **Run migrations during low-traffic periods**

4. **Keep migrations idempotent** (use `IF NOT EXISTS`, `IF EXISTS`)

5. **Document rollback procedures** for each migration
