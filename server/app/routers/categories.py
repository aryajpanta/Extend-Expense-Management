from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import ExpenseCategory, ExpenseLabel, User
from ..schemas import (
    CreateExpenseCategoryRequest,
    CreateExpenseLabelRequest,
    ExpenseCategoryResponse,
    ExpenseLabelResponse,
    UpdateExpenseCategoryRequest,
    UpdateExpenseLabelRequest,
)
from ..services.extend_api import get_extend_client


router = APIRouter(prefix="/expense-categories", tags=["expense-categories"])


def to_category_response(category: ExpenseCategory) -> ExpenseCategoryResponse:
    return ExpenseCategoryResponse(
        id=category.id,
        name=category.name,
        code=category.code,
        active=category.active,
        required=category.required,
        freeTextAllowed=category.free_text_allowed,
    )


def to_label_response(label: ExpenseLabel) -> ExpenseLabelResponse:
    return ExpenseLabelResponse(
        id=label.id,
        categoryId=label.category_id,
        name=label.name,
        code=label.code,
        active=label.active,
    )


@router.get("", response_model=list[ExpenseCategoryResponse])
def list_categories(_: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[ExpenseCategoryResponse]:
    categories = db.scalars(select(ExpenseCategory).order_by(ExpenseCategory.name)).all()
    return [to_category_response(category) for category in categories]


@router.post("", response_model=ExpenseCategoryResponse)
async def create_category(
    payload: CreateExpenseCategoryRequest,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ExpenseCategoryResponse:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Creating Extend expense categories from this app is disabled.",
    )


@router.patch("/{category_id}", response_model=ExpenseCategoryResponse)
async def update_category(
    category_id: str,
    payload: UpdateExpenseCategoryRequest,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ExpenseCategoryResponse:
    response = await get_extend_client().expense_data.update_expense_category(
        category_id=category_id,
        name=payload.name,
        active=payload.active,
        required=payload.required,
        free_text_allowed=payload.freeTextAllowed,
    )
    item = response.get("expenseCategory", response)
    category = db.get(ExpenseCategory, category_id) or ExpenseCategory(id=category_id)
    category.name = item["name"]
    category.code = item["code"]
    category.active = bool(item.get("active", True))
    category.required = bool(item.get("required", False))
    category.free_text_allowed = item.get("freeTextAllowed")
    category.raw_payload = item
    db.add(category)
    db.commit()
    db.refresh(category)
    return to_category_response(category)


@router.get("/{category_id}/labels", response_model=list[ExpenseLabelResponse])
def list_labels(
    category_id: str,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ExpenseLabelResponse]:
    labels = db.scalars(
        select(ExpenseLabel).where(ExpenseLabel.category_id == category_id).order_by(ExpenseLabel.name)
    ).all()
    return [to_label_response(label) for label in labels]


@router.post("/{category_id}/labels", response_model=ExpenseLabelResponse)
async def create_label(
    category_id: str,
    payload: CreateExpenseLabelRequest,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ExpenseLabelResponse:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Creating Extend expense labels from this app is disabled.",
    )


@router.patch("/{category_id}/labels/{label_id}", response_model=ExpenseLabelResponse)
async def update_label(
    category_id: str,
    label_id: str,
    payload: UpdateExpenseLabelRequest,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ExpenseLabelResponse:
    response = await get_extend_client().expense_data.update_expense_category_label(
        category_id=category_id,
        label_id=label_id,
        name=payload.name,
        active=payload.active,
    )
    item = response.get("expenseLabel", response)
    label = db.get(ExpenseLabel, label_id) or ExpenseLabel(id=label_id)
    label.category_id = category_id
    label.name = item["name"]
    label.code = item["code"]
    label.active = bool(item.get("active", True))
    label.raw_payload = item
    db.add(label)
    db.commit()
    db.refresh(label)
    return to_label_response(label)
