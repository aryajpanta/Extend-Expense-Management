from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    sessions: Mapped[list["Session"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime, index=True)

    user: Mapped[User] = relationship(back_populates="sessions")


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    merchant_name: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    merchant_descriptor: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    card_display_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    card_last4: Mapped[Optional[str]] = mapped_column(String(8), nullable=True)
    amount_cents: Mapped[int] = mapped_column(Integer, default=0, index=True)
    direction: Mapped[str] = mapped_column(String(16), default="debit")
    status: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    occurred_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, index=True)
    receipt_missing: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    attachments_count: Mapped[int] = mapped_column(Integer, default=0)
    missing_expense_categories: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    suggested_category_name: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, index=True)
    suggested_category_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    raw_payload: Mapped[dict] = mapped_column(JSON, default=dict)
    synced_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    detail: Mapped[Optional["TransactionDetail"]] = relationship(
        back_populates="transaction",
        cascade="all, delete-orphan",
        uselist=False,
    )
    receipts: Mapped[list["ReceiptAttachment"]] = relationship(
        back_populates="transaction",
        cascade="all, delete-orphan",
    )


class TransactionDetail(Base):
    __tablename__ = "transaction_details"

    transaction_id: Mapped[str] = mapped_column(ForeignKey("transactions.id"), primary_key=True)
    raw_payload: Mapped[dict] = mapped_column(JSON, default=dict)
    expense_details: Mapped[list] = mapped_column(JSON, default=list)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    refreshed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    transaction: Mapped[Transaction] = relationship(back_populates="detail")


class ReceiptAttachment(Base):
    __tablename__ = "receipt_attachments"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    transaction_id: Mapped[str] = mapped_column(ForeignKey("transactions.id"), index=True)
    content_type: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    upload_type: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    url_original: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    url_main: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    url_thumbnail: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    raw_payload: Mapped[dict] = mapped_column(JSON, default=dict)

    transaction: Mapped[Transaction] = relationship(back_populates="receipts")


class ExpenseCategory(Base):
    __tablename__ = "expense_categories"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    code: Mapped[str] = mapped_column(String(128))
    active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    required: Mapped[bool] = mapped_column(Boolean, default=False)
    free_text_allowed: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    raw_payload: Mapped[dict] = mapped_column(JSON, default=dict)
    synced_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    labels: Mapped[list["ExpenseLabel"]] = relationship(back_populates="category", cascade="all, delete-orphan")


class ExpenseLabel(Base):
    __tablename__ = "expense_labels"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    category_id: Mapped[str] = mapped_column(ForeignKey("expense_categories.id"), index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    code: Mapped[str] = mapped_column(String(128))
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    raw_payload: Mapped[dict] = mapped_column(JSON, default=dict)
    synced_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    category: Mapped[ExpenseCategory] = relationship(back_populates="labels")


class MerchantRule(Base):
    __tablename__ = "merchant_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    match_type: Mapped[str] = mapped_column(String(32), index=True)
    pattern: Mapped[str] = mapped_column(String(255), index=True)
    category_id: Mapped[str] = mapped_column(ForeignKey("expense_categories.id"), index=True)
    label_id: Mapped[Optional[str]] = mapped_column(ForeignKey("expense_labels.id"), nullable=True, index=True)
    priority: Mapped[int] = mapped_column(Integer, default=100, index=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    category: Mapped[ExpenseCategory] = relationship()
    label: Mapped[Optional[ExpenseLabel]] = relationship()


class SyncRun(Base):
    __tablename__ = "sync_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    status: Mapped[str] = mapped_column(String(32), index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    transactions_fetched: Mapped[int] = mapped_column(Integer, default=0)
    transactions_upserted: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
