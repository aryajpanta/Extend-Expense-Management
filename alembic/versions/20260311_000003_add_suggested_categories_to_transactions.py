"""Add suggested merchant categories to transactions.

Revision ID: 20260311_000003
Revises: 20260311_000002
Create Date: 2026-03-11 00:00:03
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260311_000003"
down_revision = "20260311_000002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("transactions") as batch_op:
        batch_op.add_column(sa.Column("suggested_category_name", sa.String(length=128), nullable=True))
        batch_op.add_column(sa.Column("suggested_category_reason", sa.Text(), nullable=True))
        batch_op.create_index("ix_transactions_suggested_category_name", ["suggested_category_name"], unique=False)


def downgrade() -> None:
    with op.batch_alter_table("transactions") as batch_op:
        batch_op.drop_index("ix_transactions_suggested_category_name")
        batch_op.drop_column("suggested_category_reason")
        batch_op.drop_column("suggested_category_name")
