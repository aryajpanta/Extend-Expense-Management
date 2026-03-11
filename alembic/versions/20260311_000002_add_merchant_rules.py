"""Add merchant rules for auto categorization.

Revision ID: 20260311_000002
Revises: 20260311_000001
Create Date: 2026-03-11 00:00:02
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260311_000002"
down_revision = "20260311_000001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "merchant_rules",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("match_type", sa.String(length=32), nullable=False),
        sa.Column("pattern", sa.String(length=255), nullable=False),
        sa.Column("category_id", sa.String(length=64), sa.ForeignKey("expense_categories.id"), nullable=False),
        sa.Column("label_id", sa.String(length=64), sa.ForeignKey("expense_labels.id"), nullable=True),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_merchant_rules_match_type", "merchant_rules", ["match_type"], unique=False)
    op.create_index("ix_merchant_rules_pattern", "merchant_rules", ["pattern"], unique=False)
    op.create_index("ix_merchant_rules_category_id", "merchant_rules", ["category_id"], unique=False)
    op.create_index("ix_merchant_rules_label_id", "merchant_rules", ["label_id"], unique=False)
    op.create_index("ix_merchant_rules_priority", "merchant_rules", ["priority"], unique=False)
    op.create_index("ix_merchant_rules_active", "merchant_rules", ["active"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_merchant_rules_active", table_name="merchant_rules")
    op.drop_index("ix_merchant_rules_priority", table_name="merchant_rules")
    op.drop_index("ix_merchant_rules_label_id", table_name="merchant_rules")
    op.drop_index("ix_merchant_rules_category_id", table_name="merchant_rules")
    op.drop_index("ix_merchant_rules_pattern", table_name="merchant_rules")
    op.drop_index("ix_merchant_rules_match_type", table_name="merchant_rules")
    op.drop_table("merchant_rules")
