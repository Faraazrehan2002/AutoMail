# Fix Migration Issue

The error "Target database is not up to date" means Alembic hasn't been initialized yet.

## Solution

Since the migration file already exists, follow these steps:

### Option 1: If database tables already exist (from create_all)

```bash
# 1. Stamp the database as being at the base (no migrations)
alembic stamp base

# 2. Now upgrade to head
alembic upgrade head
```

### Option 2: If you want to start fresh

```bash
# 1. Backup your database first!
cp automail.db automail.db.backup

# 2. Delete the database
rm automail.db

# 3. Run the migration (creates tables + applies migration)
alembic upgrade head
```

### Option 3: If tables don't exist yet

```bash
# Just run the upgrade - it will create everything
alembic upgrade head
```

## Verify

After running the commands:

```bash
# Check current revision
alembic current

# Verify schema
python scripts/db_check.py
```

## What Happened?

The database was created using `Base.metadata.create_all()` which doesn't create the `alembic_version` table that Alembic needs to track migrations. The `alembic stamp base` command initializes Alembic tracking without running any migrations.
