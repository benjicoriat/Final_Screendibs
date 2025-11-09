"""create initial tables

Revision ID: 001
Revises: 
Create Date: 2023-11-08 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Create users table (align with ORM models: integer PK and nullable optional fields)
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('full_name', sa.String(255), nullable=True),
        sa.Column('hashed_password', sa.String(255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()')),
    )

    # Create books table
    op.create_table(
        'books',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('author', sa.String(255), nullable=False),
        sa.Column('year', sa.Integer(), nullable=True),
        sa.Column('genre', sa.String(100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('cover_image_url', sa.String(512), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()')),
    )

    # Create reports table
    op.create_table(
        'reports',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('book_id', sa.String(36), sa.ForeignKey('books.id'), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('download_url', sa.String(512), nullable=True),
    )

    # Create payments table (align with ORM models: integer PK, float amount in dollars, stripe_payment_id)
    op.create_table(
        'payments',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('stripe_payment_id', sa.String(255), unique=True, nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),  # Amount in dollars
        sa.Column('currency', sa.String(3), nullable=False, server_default='usd'),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('pdf_sent', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('plan_type', sa.String(50), nullable=True),
        sa.Column('book_title', sa.String(255), nullable=True),
        sa.Column('book_author', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()')),
    )

    # Create indexes
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_books_title'), 'books', ['title'])
    op.create_index(op.f('ix_books_author'), 'books', ['author'])
    op.create_index(op.f('ix_reports_user_id'), 'reports', ['user_id'])
    op.create_index(op.f('ix_reports_book_id'), 'reports', ['book_id'])
    op.create_index(op.f('ix_payments_user_id'), 'payments', ['user_id'])
    op.create_index(op.f('ix_payments_stripe_payment_id'), 'payments', ['stripe_payment_id'], unique=True)

def downgrade() -> None:
    op.drop_table('payments')
    op.drop_table('reports')
    op.drop_table('books')
    op.drop_table('users')