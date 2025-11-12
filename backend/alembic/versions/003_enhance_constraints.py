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
    
    # Add constraints to users table
    op.create_check_constraint(
        "ck_users_email_not_empty",
        "users",
        "email != ''",
    )
    
    # Add indexes to users table for better query performance
    op.create_index("ix_users_is_active", "users", ["is_active"])
    op.create_index("ix_users_created_at", "users", ["created_at"])
    
    # Modify payments table to add constraints (if not already present)
    # Add constraint for positive amount
    op.create_check_constraint(
        "ck_payments_amount_positive",
        "payments",
        "amount > 0",
    )
    
    # Add constraint for non-empty book title
    op.create_check_constraint(
        "ck_payments_book_title_not_empty",
        "payments",
        "book_title != ''",
    )
    
    # Add constraint for non-empty book author
    op.create_check_constraint(
        "ck_payments_book_author_not_empty",
        "payments",
        "book_author != ''",
    )
    
    # Add indexes to payments table for better query performance
    op.create_index("ix_payments_user_id_created_at", "payments", ["user_id", "created_at"])
    op.create_index("ix_payments_status_created_at", "payments", ["status", "created_at"])
    op.create_index("ix_payments_stripe_payment_id", "payments", ["stripe_payment_id"], unique=True)
    
    # Ensure nullable columns are properly set
    with op.batch_alter_table("payments", schema=None) as batch_op:
        batch_op.alter_column("currency", nullable=False)
        batch_op.alter_column("status", nullable=False)
        batch_op.alter_column("pdf_sent", nullable=False)


def downgrade() -> None:
    """Remove constraints and indexes."""
    
    # Drop constraints and indexes in reverse order
    op.drop_index("ix_payments_stripe_payment_id", table_name="payments")
    op.drop_index("ix_payments_status_created_at", table_name="payments")
    op.drop_index("ix_payments_user_id_created_at", table_name="payments")
    
    op.drop_constraint("ck_payments_book_author_not_empty", "payments")
    op.drop_constraint("ck_payments_book_title_not_empty", "payments")
    op.drop_constraint("ck_payments_amount_positive", "payments")
    
    op.drop_index("ix_users_created_at", table_name="users")
    op.drop_index("ix_users_is_active", table_name="users")
    op.drop_constraint("ck_users_email_not_empty", "users")
    
    with op.batch_alter_table("payments", schema=None) as batch_op:
        batch_op.alter_column("pdf_sent", nullable=True)
        batch_op.alter_column("status", nullable=True)
        batch_op.alter_column("currency", nullable=True)
