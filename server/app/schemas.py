from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class SessionResponse(BaseModel):
    authenticated: bool
    userEmail: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class TopBucket(BaseModel):
    label: str
    amountCents: int


class DashboardSummary(BaseModel):
    totalSpendCents: int
    transactionCount: int
    receiptMissingCount: int
    missingCategoryCount: int
    topMerchants: list[TopBucket]
    topCategories: list[TopBucket]
    lastSyncAt: Optional[datetime]


class TransactionListItem(BaseModel):
    id: str
    merchantName: Optional[str] = None
    merchantDescriptor: Optional[str] = None
    cardDisplayName: Optional[str] = None
    cardLast4: Optional[str] = None
    amountCents: int
    direction: str
    status: Optional[str] = None
    occurredAt: Optional[datetime] = None
    receiptMissing: bool
    attachmentsCount: int
    missingExpenseCategories: bool


class ReceiptAttachmentResponse(BaseModel):
    id: str
    contentType: Optional[str] = None
    uploadType: Optional[str] = None
    createdAt: Optional[datetime] = None
    urlOriginal: Optional[str] = None
    urlMain: Optional[str] = None
    urlThumbnail: Optional[str] = None


class ExpenseAssignment(BaseModel):
    categoryId: str
    labelId: Optional[str] = None


class TransactionDetailResponse(TransactionListItem):
    rawExtendPayload: dict[str, Any]
    receipts: list[ReceiptAttachmentResponse]
    expenseDetails: list[ExpenseAssignment]
    notes: Optional[str] = None
    lastRefreshedAt: Optional[datetime] = None


class TransactionListResponse(BaseModel):
    items: list[TransactionListItem]
    total: int
    page: int
    perPage: int


class ExpenseCategoryResponse(BaseModel):
    id: str
    name: str
    code: str
    active: bool
    required: bool
    freeTextAllowed: Optional[bool] = None


class ExpenseLabelResponse(BaseModel):
    id: str
    categoryId: str
    name: str
    code: str
    active: bool


class CreateExpenseCategoryRequest(BaseModel):
    name: str
    code: str
    required: bool
    active: bool = True
    freeTextAllowed: Optional[bool] = None


class UpdateExpenseCategoryRequest(BaseModel):
    name: Optional[str] = None
    active: Optional[bool] = None
    required: Optional[bool] = None
    freeTextAllowed: Optional[bool] = None


class CreateExpenseLabelRequest(BaseModel):
    name: str
    code: str
    active: bool = True


class UpdateExpenseLabelRequest(BaseModel):
    name: Optional[str] = None
    active: Optional[bool] = None


class UpdateExpenseDataRequest(BaseModel):
    expenseDetails: list[ExpenseAssignment]


class SyncRunResponse(BaseModel):
    id: int
    status: str
    startedAt: datetime
    finishedAt: Optional[datetime] = None
    transactionsFetched: int
    transactionsUpserted: int
    errorMessage: Optional[str] = None


class SettingsResponse(BaseModel):
    extendEnvironment: str
    hasExtendCredentials: bool
    maskedExtendKey: Optional[str] = None
    latestSync: Optional[SyncRunResponse] = None
