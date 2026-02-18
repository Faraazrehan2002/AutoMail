"""SaaS Upgrade: Add users, templates, batches, and analytics

Revision ID: 003_saas_upgrade
Revises: 002_background_jobs
Create Date: 2026-02-17
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text


# revision identifiers
revision = '003_saas_upgrade'
down_revision = '002_background_jobs'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    # 1. Create users table
    if not inspector.has_table('users'):
        op.create_table(
            'users',
            sa.Column('id', sa.String(), nullable=False),
            sa.Column('email', sa.String(), nullable=False),
            sa.Column('hashed_password', sa.String(), nullable=False),
            sa.Column('full_name', sa.String(), nullable=True),
            sa.Column('is_active', sa.Boolean(), nullable=True, server_default='1'),
            sa.Column('is_superuser', sa.Boolean(), nullable=True, server_default='0'),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now(), server_default=sa.func.now()),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('ix_users_email', 'users', ['email'], unique=True)
    
    # 2. Add user_id to jobs (nullable for migration)
    columns = [col['name'] for col in inspector.get_columns('jobs')]
    if 'user_id' not in columns:
        op.add_column('jobs', sa.Column('user_id', sa.String(), nullable=True))
        op.create_foreign_key('fk_jobs_user_id', 'jobs', 'users', ['user_id'], ['id'])
        op.create_index('ix_jobs_user_id', 'jobs', ['user_id'])
    
    # 3. Add recipient_count to jobs
    if 'recipient_count' not in columns:
        op.add_column('jobs', sa.Column('recipient_count', sa.Integer(), nullable=True, server_default='0'))
        # Backfill recipient_count for existing jobs
        conn.execute(text("""
            UPDATE jobs 
            SET recipient_count = (
                SELECT COUNT(*) FROM recipients WHERE recipients.job_id = jobs.id
            )
        """))
    
    # 4. Add title to recipients
    recipient_columns = [col['name'] for col in inspector.get_columns('recipients')]
    if 'title' not in recipient_columns:
        op.add_column('recipients', sa.Column('title', sa.String(), nullable=True))
    
    # 5. Create batches table
    if not inspector.has_table('batches'):
        op.create_table(
            'batches',
            sa.Column('id', sa.String(), nullable=False),
            sa.Column('job_id', sa.String(), nullable=False),
            sa.Column('status', sa.String(), nullable=False, server_default='queued'),
            sa.Column('total', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('sent', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('failed', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('subject', sa.String(), nullable=False),
            sa.Column('body_hash', sa.String(), nullable=True),
            sa.Column('dry_run', sa.Boolean(), nullable=True, server_default='0'),
            sa.Column('scheduled_for', sa.DateTime(timezone=True), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['job_id'], ['jobs.id'])
        )
        op.create_index('ix_batches_job_id', 'batches', ['job_id'])
        op.create_index('ix_batches_status', 'batches', ['status'])
        op.create_index('ix_batches_body_hash', 'batches', ['body_hash'])
        op.create_index('ix_batches_scheduled_for', 'batches', ['scheduled_for'])
        op.create_index('ix_batches_created_at', 'batches', ['created_at'])
        op.create_index('idx_batch_job_status', 'batches', ['job_id', 'status'])
        op.create_index('idx_batch_scheduled', 'batches', ['scheduled_for', 'status'])
    
    # 6. Update send_logs to reference batches
    send_log_columns = [col['name'] for col in inspector.get_columns('send_logs')]
    if 'batch_id' in send_log_columns:
        # Check if it's already a foreign key
        fks = inspector.get_foreign_keys('send_logs')
        has_batch_fk = any(fk['referred_table'] == 'batches' for fk in fks)
        if not has_batch_fk:
            # Drop old batch_id column if it exists as string
            # SQLite doesn't support ALTER COLUMN, so we need to recreate
            # For now, just add the FK constraint if possible
            try:
                op.create_foreign_key('fk_send_logs_batch_id', 'send_logs', 'batches', ['batch_id'], ['id'])
            except:
                pass  # SQLite limitation
    else:
        op.add_column('send_logs', sa.Column('batch_id', sa.String(), nullable=True))
        op.create_index('ix_send_logs_batch_id', 'send_logs', ['batch_id'])
        try:
            op.create_foreign_key('fk_send_logs_batch_id', 'send_logs', 'batches', ['batch_id'], ['id'])
        except:
            pass
    
    # 7. Add updated_at to send_logs if missing
    if 'updated_at' not in send_log_columns:
        op.add_column('send_logs', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, onupdate=sa.func.now()))
    
    # 8. Create templates table
    if not inspector.has_table('templates'):
        op.create_table(
            'templates',
            sa.Column('id', sa.String(), nullable=False),
            sa.Column('user_id', sa.String(), nullable=False),
            sa.Column('name', sa.String(), nullable=False),
            sa.Column('subject', sa.String(), nullable=False),
            sa.Column('html_body', sa.Text(), nullable=False),
            sa.Column('variables', sa.JSON(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now(), server_default=sa.func.now()),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'])
        )
        op.create_index('ix_templates_user_id', 'templates', ['user_id'])
    
    # 9. Create analytics_snapshots table (optional, for performance)
    if not inspector.has_table('analytics_snapshots'):
        op.create_table(
            'analytics_snapshots',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('date', sa.DateTime(timezone=True), nullable=False),
            sa.Column('user_id', sa.String(), nullable=True),
            sa.Column('jobs_created', sa.Integer(), nullable=True, server_default='0'),
            sa.Column('batches_sent', sa.Integer(), nullable=True, server_default='0'),
            sa.Column('emails_sent', sa.Integer(), nullable=True, server_default='0'),
            sa.Column('emails_failed', sa.Integer(), nullable=True, server_default='0'),
            sa.Column('success_rate', sa.Float(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'])
        )
        op.create_index('ix_analytics_snapshots_date', 'analytics_snapshots', ['date'])
        op.create_index('ix_analytics_snapshots_user_id', 'analytics_snapshots', ['user_id'])
        op.create_index('idx_analytics_date_user', 'analytics_snapshots', ['date', 'user_id'])
    
    # 10. Migrate existing send_logs to create batches
    # For existing send_logs without batches, create a batch for each unique batch_id
    if inspector.has_table('send_logs') and inspector.has_table('batches'):
        result = conn.execute(text("""
            SELECT DISTINCT batch_id, job_id 
            FROM send_logs 
            WHERE batch_id IS NOT NULL 
            AND batch_id NOT IN (SELECT id FROM batches)
        """))
        for row in result:
            batch_id, job_id = row
            # Create a batch entry
            conn.execute(text("""
                INSERT INTO batches (id, job_id, status, total, sent, failed, subject, dry_run, created_at)
                SELECT 
                    :batch_id,
                    :job_id,
                    'completed',
                    COUNT(*),
                    SUM(CASE WHEN status = 'sent' THEN 1 ELSE 0 END),
                    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END),
                    'Migrated Batch',
                    0,
                    MIN(created_at)
                FROM send_logs
                WHERE batch_id = :batch_id
            """), {"batch_id": batch_id, "job_id": job_id})


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    # Drop in reverse order
    if inspector.has_table('analytics_snapshots'):
        op.drop_table('analytics_snapshots')
    
    if inspector.has_table('templates'):
        op.drop_table('templates')
    
    # Remove batch_id FK from send_logs (SQLite limitation - may need manual handling)
    try:
        op.drop_constraint('fk_send_logs_batch_id', 'send_logs', type_='foreignkey')
    except:
        pass
    
    if inspector.has_table('batches'):
        op.drop_table('batches')
    
    # Remove columns from jobs
    columns = [col['name'] for col in inspector.get_columns('jobs')]
    if 'recipient_count' in columns:
        op.drop_column('jobs', 'recipient_count')
    if 'user_id' in columns:
        op.drop_constraint('fk_jobs_user_id', 'jobs', type_='foreignkey')
        op.drop_index('ix_jobs_user_id', 'jobs')
        op.drop_column('jobs', 'user_id')
    
    # Remove title from recipients
    recipient_columns = [col['name'] for col in inspector.get_columns('recipients')]
    if 'title' in recipient_columns:
        op.drop_column('recipients', 'title')
    
    if inspector.has_table('users'):
        op.drop_index('ix_users_email', 'users')
        op.drop_table('users')
