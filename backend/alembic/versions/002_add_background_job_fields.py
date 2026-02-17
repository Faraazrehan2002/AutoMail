"""Add background job processing fields

Revision ID: 002_background_jobs
Revises: 767e54592c24
Create Date: 2026-02-16
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '002_background_jobs'
down_revision = '767e54592c24'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add last_batch_id to jobs
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('jobs')]
    
    if 'last_batch_id' not in columns:
        op.add_column('jobs', sa.Column('last_batch_id', sa.String(), nullable=True))
    
    # Ensure updated_at has server_default (SQLite limitation - can't modify existing column)
    # The model already has server_default, so new rows will have it
    # For existing rows, we'll leave it as is
    
    # Add progress_index to send_logs
    columns = [col['name'] for col in inspector.get_columns('send_logs')]
    if 'progress_index' not in columns:
        op.add_column('send_logs', sa.Column('progress_index', sa.Integer(), nullable=True))
    
    # Update status default to "queued" (model change only, no DB migration needed)
    # Make sent_at nullable (model already has nullable=True)
    # SQLite doesn't support ALTER COLUMN for these changes, so we rely on model defaults


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('send_logs')]
    
    if 'progress_index' in columns:
        op.drop_column('send_logs', 'progress_index')
    
    columns = [col['name'] for col in inspector.get_columns('jobs')]
    if 'last_batch_id' in columns:
        op.drop_column('jobs', 'last_batch_id')
