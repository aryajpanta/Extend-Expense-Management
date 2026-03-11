from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, File, Query, UploadFile
from sqlalchemy import asc, desc, func, or_, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import ReceiptAttachment, Transaction, User
from ..schemas import (
    ReceiptAttachmentResponse,
    TransactionDetailResponse,
    TransactionListItem,
    TransactionListResponse,
    UpdateExpenseDataRequest,
)
from ..services.extend_api import get_extend_client
from ..services.sync import parse_datetime
from ..services.sync import ensure_fresh_transaction_detail, upsert_transaction


router = APIRouter(prefix="/transactions", tags=["transactions"])


def to_list_item(tx: Transaction) -> TransactionListItem:
    return TransactionListItem(
        id=tx.id,
        merchantName=tx.merchant_name,
        merchantDescriptor=tx.merchant_descriptor,
        cardDisplayName=tx.card_display_name,
        cardLast4=tx.card_last4,
        amountCents=tx.amount_cents,
        direction=tx.direction,
        status=tx.status,
        occurredAt=tx.occurred_at,
        receiptMissing=tx.receipt_missing,
        attachmentsCount=tx.attachments_count,
        missingExpenseCategories=tx.missing_expense_categories,
        suggestedCategoryName=tx.suggested_category_name,
        suggestedCategoryReason=tx.suggested_category_reason,
    )


def to_detail_response(tx: Transaction) -> TransactionDetailResponse:
    receipts = [
        ReceiptAttachmentResponse(
            id=receipt.id,
            contentType=receipt.content_type,
            uploadType=receipt.upload_type,
            createdAt=receipt.created_at,
            urlOriginal=receipt.url_original,
            urlMain=receipt.url_main,
            urlThumbnail=receipt.url_thumbnail,
        )
        for receipt in tx.receipts
    ]
    expense_details = tx.detail.expense_details if tx.detail else []
    return TransactionDetailResponse(
        **to_list_item(tx).model_dump(),
        rawExtendPayload=tx.detail.raw_payload if tx.detail else tx.raw_payload,
        receipts=receipts,
        expenseDetails=expense_details,
        notes=tx.detail.notes if tx.detail else None,
        lastRefreshedAt=tx.detail.refreshed_at if tx.detail else tx.synced_at,
    )


@router.get("", response_model=TransactionListResponse)
def list_transactions(
    _user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=25, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[str] = None,
    receipt_missing: Optional[bool] = None,
    missing_expense_categories: Optional[bool] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    sort: str = "-date",
) -> TransactionListResponse:
    query = select(Transaction)
    if search:
        pattern = f"%{search}%"
        query = query.where(
            or_(
                Transaction.merchant_name.ilike(pattern),
                Transaction.card_display_name.ilike(pattern),
                Transaction.merchant_descriptor.ilike(pattern),
            )
        )
    if status:
        query = query.where(Transaction.status == status.upper())
    if receipt_missing is not None:
        query = query.where(Transaction.receipt_missing == receipt_missing)
    if missing_expense_categories is not None:
        query = query.where(Transaction.missing_expense_categories == missing_expense_categories)
    if from_date:
        parsed_from = parse_datetime(from_date)
        if parsed_from is not None:
            query = query.where(Transaction.occurred_at >= parsed_from)
    if to_date:
        parsed_to = parse_datetime(to_date)
        if parsed_to is not None:
            query = query.where(Transaction.occurred_at <= parsed_to)

    sort_map = {
        "date": Transaction.occurred_at,
        "-date": Transaction.occurred_at,
        "merchant": Transaction.merchant_name,
        "-merchant": Transaction.merchant_name,
        "amount": Transaction.amount_cents,
        "-amount": Transaction.amount_cents,
    }
    column = sort_map.get(sort, Transaction.occurred_at)
    query = query.order_by(desc(column) if sort.startswith("-") else asc(column))

    items = db.scalars(query.offset((page - 1) * per_page).limit(per_page)).all()
    total = db.scalar(select(func.count()).select_from(query.order_by(None).subquery())) or 0
    return TransactionListResponse(
        items=[to_list_item(item) for item in items],
        total=total,
        page=page,
        perPage=per_page,
    )


@router.get("/{transaction_id}", response_model=TransactionDetailResponse)
async def get_transaction_detail(
    transaction_id: str,
    _user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TransactionDetailResponse:
    tx = await ensure_fresh_transaction_detail(db, get_extend_client(), transaction_id)
    return to_detail_response(tx)


@router.patch("/{transaction_id}/expense-data", response_model=TransactionDetailResponse)
async def update_transaction_expense_data(
    transaction_id: str,
    payload: UpdateExpenseDataRequest,
    _user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TransactionDetailResponse:
    client = get_extend_client()
    response = await client.transactions.update_transaction_expense_data(
        transaction_id,
        {"expenseDetails": [item.model_dump() for item in payload.expenseDetails]},
    )
    tx = upsert_transaction(db, response.get("transaction", response))
    db.commit()
    db.refresh(tx)
    return to_detail_response(tx)


@router.post("/{transaction_id}/receipts", response_model=ReceiptAttachmentResponse)
async def upload_receipt(
    transaction_id: str,
    file: UploadFile = File(...),
    _user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReceiptAttachmentResponse:
    client = get_extend_client()
    upload_response = await client.receipt_attachments.create_receipt_attachment(file.file, transaction_id=transaction_id)
    attachment_payload = upload_response.get("receiptAttachment", upload_response)
    tx = await ensure_fresh_transaction_detail(db, client, transaction_id)
    receipt = db.get(ReceiptAttachment, attachment_payload["id"])
    if receipt is None:
        tx = await ensure_fresh_transaction_detail(db, client, transaction_id)
        receipt = db.get(ReceiptAttachment, attachment_payload["id"])
    return ReceiptAttachmentResponse(
        id=receipt.id,
        contentType=receipt.content_type,
        uploadType=receipt.upload_type,
        createdAt=receipt.created_at,
        urlOriginal=receipt.url_original,
        urlMain=receipt.url_main,
        urlThumbnail=receipt.url_thumbnail,
    )
