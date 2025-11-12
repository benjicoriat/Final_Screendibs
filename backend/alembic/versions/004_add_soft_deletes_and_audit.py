"""Migration 004: Add soft deletes, audit fields, and audit log table.

Revision ID: 004
Revises: 003
Create Date: 2024-11-12

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema."""
    # Add columns to users table
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('deleted_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('created_by', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('updated_by', sa.Integer(), nullable=True))
        batch_op.create_index('ix_users_deleted_at', ['deleted_at'])

    # Add columns to payments table
    with op.batch_alter_table('payments', schema=None) as batch_op:
        batch_op.add_column(sa.Column('deleted_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('created_by', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('updated_by', sa.Integer(), nullable=True))
        batch_op.create_index('ix_payments_deleted_at', ['deleted_at'])

    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('entity_type', sa.String(50), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(20), nullable=False),
        sa.Column('changes', sa.Text(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('reason', sa.String(255), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_audit_logs_entity', 'audit_logs', ['entity_type', 'entity_id'])
    op.create_index('ix_audit_logs_created_at', 'audit_logs', ['created_at'])
    op.create_index('ix_audit_logs_user_id', 'audit_logs', ['user_id'])
    op.create_index('ix_audit_logs_action', 'audit_logs', ['action'])
    op.create_index('ix_audit_logs_id', 'audit_logs', ['id'])


def downgrade() -> None:
    """Downgrade database schema."""
    # Drop audit_logs table
    op.drop_table('audit_logs')
    
    # Remove columns from payments table
    with op.batch_alter_table('payments', schema=None) as batch_op:
        batch_op.drop_index('ix_payments_deleted_at')
        batch_op.drop_column('updated_by')
        batch_op.drop_column('created_by')
        batch_op.drop_column('deleted_at')

    # Remove columns from users table
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index('ix_users_deleted_at')
        batch_op.drop_column('updated_by')
        batch_op.drop_column('created_by')
        batch_op.drop_column('deleted_at')
