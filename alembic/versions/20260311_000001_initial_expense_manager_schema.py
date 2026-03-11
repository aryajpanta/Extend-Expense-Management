"""Initial expense manager schema.

Revision ID: 20260311_000001
Revises:
Create Date: 2026-03-11 00:00:01
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260311_000001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "sessions",
        sa.Column("id", sa.String(length=128), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_sessions_user_id", "sessions", ["user_id"], unique=False)
    op.create_index("ix_sessions_expires_at", "sessions", ["expires_at"], unique=False)

    op.create_table(
        "transactions",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("merchant_name", sa.String(length=255), nullable=True),
        sa.Column("merchant_descriptor", sa.String(length=255), nullable=True),
        sa.Column("card_display_name", sa.String(length=255), nullable=True),
        sa.Column("card_last4", sa.String(length=8), nullable=True),
        sa.Column("amount_cents", sa.Integer(), nullable=False),
        sa.Column("direction", sa.String(length=16), nullable=False),
        sa.Column("status", sa.String(length=64), nullable=True),
        sa.Column("occurred_at", sa.DateTime(), nullable=True),
        sa.Column("receipt_missing", sa.Boolean(), nullable=False),
        sa.Column("attachments_count", sa.Integer(), nullable=False),
        sa.Column("missing_expense_categories", sa.Boolean(), nullable=False),
        sa.Column("raw_payload", sa.JSON(), nullable=False),
        sa.Column("synced_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_transactions_amount_cents", "transactions", ["amount_cents"], unique=False)
    op.create_index("ix_transactions_card_display_name", "transactions", ["card_display_name"], unique=False)
    op.create_index("ix_transactions_merchant_name", "transactions", ["merchant_name"], unique=False)
    op.create_index("ix_transactions_missing_expense_categories", "transactions", ["missing_expense_categories"], unique=False)
    op.create_index("ix_transactions_occurred_at", "transactions", ["occurred_at"], unique=False)
    op.create_index("ix_transactions_receipt_missing", "transactions", ["receipt_missing"], unique=False)
    op.create_index("ix_transactions_status", "transactions", ["status"], unique=False)
    op.create_index("ix_transactions_synced_at", "transactions", ["synced_at"], unique=False)

    op.create_table(
        "transaction_details",
        sa.Column("transaction_id", sa.String(length=64), sa.ForeignKey("transactions.id"), primary_key=True),
        sa.Column("raw_payload", sa.JSON(), nullable=False),
        sa.Column("expense_details", sa.JSON(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("refreshed_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_transaction_details_refreshed_at", "transaction_details", ["refreshed_at"], unique=False)

    op.create_table(
        "receipt_attachments",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("transaction_id", sa.String(length=64), sa.ForeignKey("transactions.id"), nullable=False),
        sa.Column("content_type", sa.String(length=128), nullable=True),
        sa.Column("upload_type", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("url_original", sa.Text(), nullable=True),
        sa.Column("url_main", sa.Text(), nullable=True),
        sa.Column("url_thumbnail", sa.Text(), nullable=True),
        sa.Column("raw_payload", sa.JSON(), nullable=False),
    )
    op.create_index("ix_receipt_attachments_transaction_id", "receipt_attachments", ["transaction_id"], unique=False)

    op.create_table(
        "expense_categories",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("code", sa.String(length=128), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("required", sa.Boolean(), nullable=False),
        sa.Column("free_text_allowed", sa.Boolean(), nullable=True),
        sa.Column("raw_payload", sa.JSON(), nullable=False),
        sa.Column("synced_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_expense_categories_active", "expense_categories", ["active"], unique=False)
    op.create_index("ix_expense_categories_name", "expense_categories", ["name"], unique=False)

    op.create_table(
        "expense_labels",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("category_id", sa.String(length=64), sa.ForeignKey("expense_categories.id"), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("code", sa.String(length=128), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("raw_payload", sa.JSON(), nullable=False),
        sa.Column("synced_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_expense_labels_category_id", "expense_labels", ["category_id"], unique=False)
    op.create_index("ix_expense_labels_name", "expense_labels", ["name"], unique=False)

    op.create_table(
        "sync_runs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("transactions_fetched", sa.Integer(), nullable=False),
        sa.Column("transactions_upserted", sa.Integer(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
    )
    op.create_index("ix_sync_runs_started_at", "sync_runs", ["started_at"], unique=False)
    op.create_index("ix_sync_runs_status", "sync_runs", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_sync_runs_status", table_name="sync_runs")
    op.drop_index("ix_sync_runs_started_at", table_name="sync_runs")
    op.drop_table("sync_runs")

    op.drop_index("ix_expense_labels_name", table_name="expense_labels")
    op.drop_index("ix_expense_labels_category_id", table_name="expense_labels")
    op.drop_table("expense_labels")

    op.drop_index("ix_expense_categories_name", table_name="expense_categories")
    op.drop_index("ix_expense_categories_active", table_name="expense_categories")
    op.drop_table("expense_categories")

    op.drop_index("ix_receipt_attachments_transaction_id", table_name="receipt_attachments")
    op.drop_table("receipt_attachments")

    op.drop_index("ix_transaction_details_refreshed_at", table_name="transaction_details")
    op.drop_table("transaction_details")

    op.drop_index("ix_transactions_synced_at", table_name="transactions")
    op.drop_index("ix_transactions_status", table_name="transactions")
    op.drop_index("ix_transactions_receipt_missing", table_name="transactions")
    op.drop_index("ix_transactions_occurred_at", table_name="transactions")
    op.drop_index("ix_transactions_missing_expense_categories", table_name="transactions")
    op.drop_index("ix_transactions_merchant_name", table_name="transactions")
    op.drop_index("ix_transactions_card_display_name", table_name="transactions")
    op.drop_index("ix_transactions_amount_cents", table_name="transactions")
    op.drop_table("transactions")

    op.drop_index("ix_sessions_expires_at", table_name="sessions")
    op.drop_index("ix_sessions_user_id", table_name="sessions")
    op.drop_table("sessions")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

