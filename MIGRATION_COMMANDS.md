# Database Migration Commands

## Quick Start

Run these commands in order:

```bash
# 1. Apply the migration
alembic upgrade head

# 2. Verify the schema
python scripts/db_check.py

# 3. (Optional) Check current status
alembic current
```

## Detailed Steps

### Step 1: Verify Alembic Configuration

The Alembic setup is already configured:
- ✅ `alembic.ini` exists and points to `alembic/` directory
- ✅ `alembic/env.py` imports `app.config.settings` and uses `DATABASE_URL`
- ✅ `target_metadata` is set to `Base.metadata` from `app.models`

### Step 2: Apply Migration

```bash
# Apply all pending migrations
alembic upgrade head
```

This will:
- Add `batch_id` column to `send_logs` (with index)
- Add `created_at` column to `send_logs`
- Backfill existing rows:
  - `batch_id`: Generated UUID for each row (format: `legacy-<random>`)
  - `created_at`: Uses `sent_at` if available, otherwise current timestamp

### Step 3: Verify Migration

```bash
# Run the verification script
python scripts/db_check.py
```

Expected output:
```
============================================================
Database Schema Check
============================================================

1. Checking Alembic version...
   Current revision: 001_batch_id_created_at
   Head revision: 001_batch_id_created_at
   ✓ Database is at head revision

2. Checking send_logs table columns...
   Found columns: id, batch_id, job_id, recipient_email, status, error_message, sendgrid_message_id, sent_at, created_at, personalization
   
   ✓ batch_id exists (nullable: False)
   ✓ created_at exists (nullable: False)
   ✓ batch_id index exists

============================================================
✓ PASS - All checks passed
```

### Step 4: Test the Application

```bash
# Start the server
uvicorn app.main:app --reload
```

On startup, you should see:
- ✅ "Database initialized"
- ✅ "✓ Database schema is up to date" (or a warning if migrations are behind)

## Development Auto-Migration (Optional)

To automatically run migrations on startup in development:

```bash
# Add to .env
AUTO_MIGRATE_DEV=true
```

**Warning**: Only use this in development. Never auto-migrate in production.

## Troubleshooting

### Error: "no such column: batch_id"

**Solution**: Run migrations
```bash
alembic upgrade head
```

### Error: "Table 'alembic_version' doesn't exist"

**Solution**: This means Alembic hasn't been initialized. Run:
```bash
alembic upgrade head
```

### Error: "Database is locked" (SQLite)

**Solution**: Close any connections to the database and try again.

### Check Migration Status

```bash
# See current revision
alembic current

# See migration history
alembic history

# See what would be applied (dry run)
alembic upgrade head --sql
```

### Rollback (if needed)

```bash
# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>
```

## Migration File Details

The migration file is located at:
`alembic/versions/001_add_batch_id_and_created_at_to_send_logs.py`

It:
- ✅ Is idempotent (safe to run multiple times)
- ✅ Handles SQLite limitations
- ✅ Backfills existing data
- ✅ Creates indexes
- ✅ Has a downgrade function

## Verification Checklist

After running migrations, verify:

- [ ] `alembic current` shows the migration revision
- [ ] `python scripts/db_check.py` passes
- [ ] Application starts without errors
- [ ] No "no such column" errors in logs
- [ ] Can create new send_logs entries with batch_id
