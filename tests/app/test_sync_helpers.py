from datetime import datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from server.app.database import Base
from server.app.models import ExpenseCategory, Transaction, TransactionDetail
from server.app.services.sync import dashboard_summary, normalize_transaction, parse_datetime


def test_parse_datetime_handles_iso_and_date():
    assert parse_datetime("2026-03-11T12:30:00.000Z") is not None
    assert parse_datetime("2026-03-11T11:55:35.000+0000") is not None
    assert parse_datetime("2026-03-11") is not None
    assert parse_datetime("invalid") is None


def test_normalize_transaction_sets_receipt_and_category_flags():
    normalized = normalize_transaction(
        {
            "id": "txn_1",
            "merchantName": "Coffee Shop",
            "creditCardDisplayName": "Primary Card",
            "creditCardLast4": "4242",
            "clearingBillingAmountCents": 599,
            "status": "CLEARED",
            "clearedAt": "2026-03-11T12:30:00.000Z",
            "attachmentsCount": 0,
            "receiptRequired": True,
            "expenseCategoryStatuses": ["Missing"],
        }
    )

    assert normalized["merchant_name"] == "Coffee Shop"
    assert normalized["receipt_missing"] is True
    assert normalized["missing_expense_categories"] is True
    assert normalized["direction"] == "debit"


def test_dashboard_summary_includes_recent_transactions_and_trends():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, future=True)

    with SessionLocal() as db:
        category = ExpenseCategory(
            id="cat_1",
            name="Travel",
            code="TRAVEL",
            active=True,
            required=False,
            free_text_allowed=False,
            raw_payload={},
            synced_at=datetime.utcnow(),
        )
        db.add(category)
        tx_one = Transaction(
            id="txn_1",
            merchant_name="Coffee Shop",
            amount_cents=599,
            direction="debit",
            status="CLEARED",
            occurred_at=datetime.utcnow() - timedelta(days=1),
            receipt_missing=True,
            attachments_count=0,
            missing_expense_categories=False,
            raw_payload={},
            synced_at=datetime.utcnow(),
        )
        tx_one.detail = TransactionDetail(
            transaction=tx_one,
            raw_payload={},
            expense_details=[{"categoryId": "cat_1"}],
            notes=None,
            refreshed_at=datetime.utcnow(),
        )
        tx_two = Transaction(
            id="txn_2",
            merchant_name="Train Ticket",
            amount_cents=2500,
            direction="debit",
            status="PENDING",
            occurred_at=datetime.utcnow(),
            receipt_missing=False,
            attachments_count=1,
            missing_expense_categories=True,
            raw_payload={},
            synced_at=datetime.utcnow(),
        )
        tx_two.detail = TransactionDetail(
            transaction=tx_two,
            raw_payload={},
            expense_details=[],
            notes=None,
            refreshed_at=datetime.utcnow(),
        )
        db.add_all([tx_one, tx_two])
        db.commit()

        summary = dashboard_summary(db)

    assert summary["transactionCount"] == 2
    assert len(summary["recentTransactions"]) == 2
    assert summary["recentTransactions"][0]["id"] == "txn_2"
    assert any(item["label"] == "Travel" for item in summary["topCategories"])
    assert any(item["label"] == "CLEARED" for item in summary["spendByStatus"])
    assert len(summary["spendByDay"]) >= 1
