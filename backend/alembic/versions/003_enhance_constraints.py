"""Add enhanced constraints and indexes for data integrity

Revision ID: 003
Revises: 002
Create Date: 2025-11-12 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add constraints and indexes for data integrity."""
    
    # Add indexes to users table for better query performance
    op.create_index("ix_users_is_active", "users", ["is_active"], unique=False)
    op.create_index("ix_users_created_at", "users", ["created_at"], unique=False)
    
    # Add indexes to payments table for better query performance
    op.create_index("ix_payments_user_id_created_at", "payments", ["user_id", "created_at"], unique=False)
    op.create_index("ix_payments_status_created_at", "payments", ["status", "created_at"], unique=False)
    
    # Note: Constraints are already defined in the table definitions
    # SQLite doesn't support adding constraints after table creation without batch mode
    # These will be enforced through the ORM model definitions


def downgrade() -> None:
    """Remove constraints and indexes."""
    
    # Drop indexes in reverse order
    op.drop_index("ix_payments_status_created_at", table_name="payments")
    op.drop_index("ix_payments_user_id_created_at", table_name="payments")
    
    op.drop_index("ix_users_created_at", table_name="users")
    op.drop_index("ix_users_is_active", table_name="users")
