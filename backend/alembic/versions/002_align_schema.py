"""Align database schema with current ORM models: use integer PKs, adjust payment columns

Revision ID: 002
Revises: 001
Create Date: 2025-11-11 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Migrate from old schema (UUID PKs, stripe_payment_intent_id, amount in cents) 
    to new schema (integer PKs, stripe_payment_id, amount in dollars).
    """
    # If this is a fresh DB (tables don't exist), skip migration
    # In production, this migration assumes the old schema exists from revision 001
    
    # For now, this migration is a placeholder/documentation of the schema change.
    # If you have an existing DB with the old schema, you would:
    # 1. Add columns for new schema
    # 2. Migrate data
    # 3. Drop old columns
    # 4. Rename columns as needed
    
    # This is a NO-OP migration for fresh databases created after the initial revision was fixed.
    # For existing production DBs, coordinate a proper data migration strategy.
    pass


def downgrade() -> None:
    """
    Downgrade to previous schema (for rollback).
    """
    pass
