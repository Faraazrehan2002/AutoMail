"""Add batch_id and created_at to send_logs

Revision ID: 001_batch_id_created_at
Revises: 
Create Date: 2024-02-16

"""
from alembic import op
import sqlalchemy as sa
import uuid
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '001_batch_id_created_at'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Check if send_logs table exists
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()
    
    if 'send_logs' not in tables:
        # Table doesn't exist yet, will be created by Base.metadata.create_all
        # Just return - the model already has these fields
        return
    
    # Get existing columns
    columns = [col['name'] for col in inspector.get_columns('send_logs')]
    
    # Add batch_id column if it doesn't exist
    if 'batch_id' not in columns:
        op.add_column('send_logs', 
            sa.Column('batch_id', sa.String(), nullable=True)
        )
        
        # Backfill batch_id for existing rows
        # Generate UUID for each existing row, or use 'legacy' as fallback
        op.execute("""
            UPDATE send_logs 
            SET batch_id = 'legacy-' || substr(hex(randomblob(16)), 1, 32)
            WHERE batch_id IS NULL
        """)
        
        # Now make it non-nullable
        op.alter_column('send_logs', 'batch_id', nullable=False)
        
        # Create index
        op.create_index('ix_send_logs_batch_id', 'send_logs', ['batch_id'])
    
    # Add created_at column if it doesn't exist
    if 'created_at' not in columns:
        # SQLite doesn't support ALTER COLUMN to change nullability
        # So we add it as nullable, backfill, then recreate table if needed
        # For now, we'll add it as nullable and handle nulls in application code
        # OR we can use a table recreation approach for SQLite
        
        # Check if we have existing data
        result = conn.execute(sa.text("SELECT COUNT(*) FROM send_logs"))
        row_count = result.scalar()
        
        if row_count == 0:
            # No data, safe to add as non-nullable
            op.add_column('send_logs',
                sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
            )
        else:
            # Has data - add as nullable, backfill, then we'll need table recreation for SQLite
            # For simplicity, we'll add as nullable and enforce in application
            op.add_column('send_logs',
                sa.Column('created_at', sa.DateTime(timezone=True), nullable=True)
            )
            
            # Backfill created_at for existing rows (use sent_at or current time)
            op.execute("""
                UPDATE send_logs 
                SET created_at = COALESCE(sent_at, datetime('now'))
                WHERE created_at IS NULL
            """)
            
            # Note: SQLite doesn't support ALTER COLUMN to change nullability
            # The column will remain nullable, but we backfill all existing rows
            # Application code should handle this (model has server_default)


def downgrade() -> None:
    # Remove batch_id column and index
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('send_logs')]
    
    if 'batch_id' in columns:
        # Drop index first
        try:
            op.drop_index('ix_send_logs_batch_id', table_name='send_logs')
        except:
            pass
        op.drop_column('send_logs', 'batch_id')
    
    if 'created_at' in columns:
        op.drop_column('send_logs', 'created_at')
