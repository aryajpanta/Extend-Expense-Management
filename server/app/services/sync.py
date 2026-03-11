from __future__ import annotations

import asyncio
from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from extend import ExtendClient

from ..config import get_settings
from ..models import ExpenseCategory, ExpenseLabel, ReceiptAttachment, SyncRun, Transaction, TransactionDetail


sync_lock = asyncio.Lock()


def parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        if value.endswith("Z"):
            return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc).replace(tzinfo=None)
        return datetime.fromisoformat(value)
    except ValueError:
        try:
            return datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            return None


def first_present(payload: dict[str, Any], keys: list[str]) -> Any:
    for key in keys:
        value = payload.get(key)
        if value not in (None, ""):
            return value
    return None


def normalize_transaction(tx: dict[str, Any]) -> dict[str, Any]:
    amount = tx.get("clearingBillingAmountCents")
    if amount is None:
        amount = tx.get("authBillingAmountCents", 0)
    merchant_name = first_present(tx, ["merchantName", "merchantDescriptor", "merchant", "description"])
    card_display_name = first_present(
        tx,
        ["cardName", "virtualCardDisplayName", "creditCardDisplayName", "cardDisplayName"],
    )
    card_last4 = first_present(tx, ["last4", "cardLast4", "virtualCardLast4", "creditCardLast4"])
    occurred_at = parse_datetime(first_present(tx, ["clearedAt", "authedAt", "createdAt", "updatedAt"]))
    attachments_count = int(tx.get("attachmentsCount") or 0)
    receipt_missing = bool(tx.get("receiptRequired")) and attachments_count == 0
    expense_statuses = tx.get("expenseCategoryStatuses") or []
    missing_expense_categories = "Missing" in expense_statuses or bool(tx.get("missingExpenseCategories"))
    return {
        "id": tx["id"],
        "merchant_name": merchant_name,
        "merchant_descriptor": tx.get("merchantDescriptor"),
        "card_display_name": card_display_name,
        "card_last4": card_last4,
        "amount_cents": int(amount or 0),
        "direction": "credit" if int(amount or 0) < 0 else "debit",
        "status": tx.get("status"),
        "occurred_at": occurred_at,
        "receipt_missing": receipt_missing,
        "attachments_count": attachments_count,
        "missing_expense_categories": missing_expense_categories,
        "raw_payload": tx,
        "synced_at": datetime.utcnow(),
    }


def expense_details_from_payload(payload: dict[str, Any]) -> list[dict[str, Any]]:
    if "expenseDetails" in payload and isinstance(payload["expenseDetails"], list):
        return payload["expenseDetails"]
    if "expenseData" in payload and isinstance(payload["expenseData"], dict):
        details = payload["expenseData"].get("expenseDetails")
        if isinstance(details, list):
            return details
    return []


def receipt_payloads_from_transaction(payload: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ["receiptAttachments", "attachments", "receipts"]:
        value = payload.get(key)
        if isinstance(value, list):
            return value
    return []


def upsert_transaction(db: Session, tx_payload: dict[str, Any]) -> Transaction:
    data = normalize_transaction(tx_payload)
    tx = db.get(Transaction, data["id"])
    if tx is None:
        tx = Transaction(id=data["id"])
        db.add(tx)
    for key, value in data.items():
        setattr(tx, key, value)

    detail = tx.detail or TransactionDetail(transaction=tx)
    detail.raw_payload = tx_payload
    detail.expense_details = expense_details_from_payload(tx_payload)
    detail.notes = tx_payload.get("notes")
    detail.refreshed_at = datetime.utcnow()
    db.add(detail)

    existing_receipts = {receipt.id: receipt for receipt in tx.receipts}
    current_receipt_ids: set[str] = set()
    for receipt_payload in receipt_payloads_from_transaction(tx_payload):
        receipt_id = receipt_payload.get("id")
        if not receipt_id:
            continue
        current_receipt_ids.add(receipt_id)
        receipt = existing_receipts.get(receipt_id) or ReceiptAttachment(id=receipt_id, transaction=tx)
        urls = receipt_payload.get("urls") or {}
        receipt.content_type = receipt_payload.get("contentType")
        receipt.upload_type = receipt_payload.get("uploadType")
        receipt.created_at = parse_datetime(receipt_payload.get("createdAt"))
        receipt.url_original = urls.get("original")
        receipt.url_main = urls.get("main")
        receipt.url_thumbnail = urls.get("thumbnail")
        receipt.raw_payload = receipt_payload
        db.add(receipt)

    for receipt_id, receipt in existing_receipts.items():
        if receipt_id not in current_receipt_ids:
            db.delete(receipt)

    return tx


async def refresh_expense_categories(db: Session, client: ExtendClient) -> None:
    response = await client.expense_data.get_expense_categories()
    category_payloads = response.get("expenseCategories", [])
    seen_category_ids: set[str] = set()
    seen_label_ids: set[str] = set()

    for payload in category_payloads:
        category_id = payload["id"]
        seen_category_ids.add(category_id)
        category = db.get(ExpenseCategory, category_id) or ExpenseCategory(id=category_id)
        category.name = payload["name"]
        category.code = payload["code"]
        category.active = bool(payload.get("active", True))
        category.required = bool(payload.get("required", False))
        category.free_text_allowed = payload.get("freeTextAllowed")
        category.raw_payload = payload
        category.synced_at = datetime.utcnow()
        db.add(category)

        labels_response = await client.expense_data.get_expense_category_labels(category_id)
        for label_payload in labels_response.get("expenseLabels", []):
            label_id = label_payload["id"]
            seen_label_ids.add(label_id)
            label = db.get(ExpenseLabel, label_id) or ExpenseLabel(id=label_id)
            label.category_id = category_id
            label.name = label_payload["name"]
            label.code = label_payload["code"]
            label.active = bool(label_payload.get("active", True))
            label.raw_payload = label_payload
            label.synced_at = datetime.utcnow()
            db.add(label)

    if seen_category_ids:
        for category in db.scalars(select(ExpenseCategory)).all():
            if category.id not in seen_category_ids:
                db.delete(category)
    if seen_label_ids:
        for label in db.scalars(select(ExpenseLabel)).all():
            if label.id not in seen_label_ids:
                db.delete(label)


async def sync_transactions(db: Session, client: ExtendClient, days_back: int) -> tuple[int, int]:
    since = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    fetched = 0
    upserted = 0
    page = 1
    per_page = 100

    while True:
        response = await client.transactions.get_transactions(
            page=page,
            per_page=per_page,
            from_date=since,
            sort_field="-date",
        )
        report = response.get("report", response)
        items = report.get("transactions", [])
        if not items:
            break
        fetched += len(items)
        for item in items:
            upsert_transaction(db, item)
            upserted += 1
        db.commit()

        pagination = report.get("pagination", response.get("pagination", {}))
        page_item_count = pagination.get("pageItemCount", len(items))
        total_items = pagination.get("totalItems")
        if len(items) < per_page:
            break
        if total_items is not None and page * per_page >= total_items:
            break
        if page_item_count == 0:
            break
        page += 1

    return fetched, upserted


async def run_sync_cycle(db: Session, client: ExtendClient, force_full: bool = False) -> SyncRun:
    async with sync_lock:
        completed_runs = db.scalar(select(func.count()).select_from(SyncRun).where(SyncRun.status == "completed")) or 0
        settings = get_settings()
        days_back = settings.sync_initial_days if force_full or completed_runs == 0 else settings.sync_incremental_days
        sync_run = SyncRun(status="running")
        db.add(sync_run)
        db.commit()
        db.refresh(sync_run)

        try:
            transactions_fetched, transactions_upserted = await sync_transactions(db, client, days_back)
            await refresh_expense_categories(db, client)
            sync_run.status = "completed"
            sync_run.transactions_fetched = transactions_fetched
            sync_run.transactions_upserted = transactions_upserted
            sync_run.finished_at = datetime.utcnow()
            db.add(sync_run)
            db.commit()
            db.refresh(sync_run)
            return sync_run
        except Exception as exc:
            sync_run.status = "failed"
            sync_run.error_message = str(exc)
            sync_run.finished_at = datetime.utcnow()
            db.add(sync_run)
            db.commit()
            db.refresh(sync_run)
            raise


async def ensure_fresh_transaction_detail(db: Session, client: ExtendClient, transaction_id: str) -> Transaction:
    settings = get_settings()
    tx = db.get(Transaction, transaction_id)
    if tx is None:
        payload = await client.transactions.get_transaction(transaction_id)
        item = payload.get("transaction", payload)
        tx = upsert_transaction(db, item)
        db.commit()
        db.refresh(tx)
        return tx

    freshness_cutoff = datetime.utcnow() - timedelta(minutes=settings.detail_freshness_minutes)
    if tx.detail is None or tx.detail.refreshed_at < freshness_cutoff:
        payload = await client.transactions.get_transaction(transaction_id)
        item = payload.get("transaction", payload)
        tx = upsert_transaction(db, item)
        db.commit()
        db.refresh(tx)
    return tx


def latest_sync_run(db: Session) -> SyncRun | None:
    return db.scalar(select(SyncRun).order_by(desc(SyncRun.started_at)).limit(1))


def dashboard_summary(db: Session) -> dict[str, Any]:
    transactions = db.scalars(select(Transaction)).all()
    total_spend = sum(max(tx.amount_cents, 0) for tx in transactions)
    top_merchants_counter: Counter[str] = Counter()
    top_categories_counter: Counter[str] = Counter()

    for tx in transactions:
        if tx.merchant_name:
            top_merchants_counter[tx.merchant_name] += max(tx.amount_cents, 0)
        details = tx.detail.expense_details if tx.detail else []
        for detail in details:
            category_id = detail.get("categoryId")
            label_id = detail.get("labelId")
            label = db.get(ExpenseLabel, label_id) if label_id else None
            category = db.get(ExpenseCategory, category_id) if category_id else None
            label_name = label.name if label else (category.name if category else "Unlabeled")
            top_categories_counter[label_name] += max(tx.amount_cents, 0)

    latest = latest_sync_run(db)
    return {
        "totalSpendCents": total_spend,
        "transactionCount": len(transactions),
        "receiptMissingCount": sum(1 for tx in transactions if tx.receipt_missing),
        "missingCategoryCount": sum(1 for tx in transactions if tx.missing_expense_categories),
        "topMerchants": [
            {"label": label, "amountCents": amount}
            for label, amount in top_merchants_counter.most_common(5)
        ],
        "topCategories": [
            {"label": label, "amountCents": amount}
            for label, amount in top_categories_counter.most_common(5)
        ],
        "lastSyncAt": latest.finished_at if latest else None,
    }
