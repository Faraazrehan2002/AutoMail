#!/usr/bin/env python3
"""
Database verification script.
Checks Alembic version and verifies required columns exist.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.runtime.migration import MigrationContext
from sqlalchemy import create_engine, inspect
from app.config import settings


def main():
    """Check database schema"""
    print("=" * 60)
    print("Database Schema Check")
    print("=" * 60)
    print()
    
    errors = []
    
    # 1. Check Alembic version
    print("1. Checking Alembic version...")
    try:
        alembic_cfg = Config("alembic.ini")
        script = ScriptDirectory.from_config(alembic_cfg)
        
        engine = create_engine(
            settings.database_url,
            connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
        )
        
        with engine.connect() as connection:
            context = MigrationContext.configure(connection)
            current_rev = context.get_current_revision()
            head_rev = script.get_current_head()
        
        print(f"   Current revision: {current_rev or 'None (no migrations applied)'}")
        print(f"   Head revision: {head_rev}")
        
        if current_rev != head_rev:
            errors.append(f"Database is not at head revision (current: {current_rev}, head: {head_rev})")
            print("   ⚠️  WARNING: Database schema is out of date")
            print("   Run: alembic upgrade head")
        else:
            print("   ✓ Database is at head revision")
        
    except Exception as e:
        errors.append(f"Error checking Alembic version: {e}")
        print(f"   ✗ Error: {e}")
    
    print()
    
    # 2. Check send_logs table columns
    print("2. Checking send_logs table columns...")
    try:
        inspector = inspect(engine)
        
        if 'send_logs' not in inspector.get_table_names():
            errors.append("send_logs table does not exist")
            print("   ✗ send_logs table does not exist")
        else:
            columns = {col['name']: col for col in inspector.get_columns('send_logs')}
            column_names = list(columns.keys())
            
            print(f"   Found columns: {', '.join(column_names)}")
            print()
            
            # Check for batch_id
            if 'batch_id' not in column_names:
                errors.append("send_logs.batch_id column is missing")
                print("   ✗ batch_id column is MISSING")
            else:
                col = columns['batch_id']
                nullable = col.get('nullable', True)
                print(f"   ✓ batch_id exists (nullable: {nullable})")
            
            # Check for created_at
            if 'created_at' not in column_names:
                errors.append("send_logs.created_at column is missing")
                print("   ✗ created_at column is MISSING")
            else:
                col = columns['created_at']
                nullable = col.get('nullable', True)
                print(f"   ✓ created_at exists (nullable: {nullable})")
            
            # Check for batch_id index
            indexes = {idx['name']: idx for idx in inspector.get_indexes('send_logs')}
            if 'ix_send_logs_batch_id' not in indexes:
                print("   ⚠️  batch_id index (ix_send_logs_batch_id) is missing")
            else:
                print("   ✓ batch_id index exists")
    
    except Exception as e:
        errors.append(f"Error checking table columns: {e}")
        print(f"   ✗ Error: {e}")
    
    print()
    print("=" * 60)
    
    if errors:
        print("✗ FAILED - Found issues:")
        for error in errors:
            print(f"  - {error}")
        print()
        print("To fix:")
        print("  alembic upgrade head")
        sys.exit(1)
    else:
        print("✓ PASS - All checks passed")
        sys.exit(0)


if __name__ == "__main__":
    main()
