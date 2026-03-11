from __future__ import annotations

import httpx

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from ..database import get_db
from ..deps import get_current_user
from ..models import ExpenseCategory, ExpenseLabel, MerchantRule, User
from ..schemas import (
    CreateMerchantRuleRequest,
    MerchantRuleResponse,
    MerchantRuleSeedResponse,
    UpdateMerchantRuleRequest,
)
from ..services.extend_api import get_extend_client
from ..services.merchant_rules import (
    merchant_rule_response,
    normalize_match_value,
    seed_default_merchant_rules,
    seed_generic_categories_in_extend,
)
from ..services.sync import auto_assign_categorization_rules, refresh_expense_categories


router = APIRouter(prefix="/merchant-rules", tags=["merchant-rules"])


def get_rule_or_404(db: Session, rule_id: int) -> MerchantRule:
    rule = db.scalar(
        select(MerchantRule)
        .options(joinedload(MerchantRule.category), joinedload(MerchantRule.label))
        .where(MerchantRule.id == rule_id)
    )
    if rule is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Merchant rule not found")
    return rule


@router.get("", response_model=list[MerchantRuleResponse])
def list_rules(_: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[MerchantRuleResponse]:
    rules = db.scalars(
        select(MerchantRule)
        .options(joinedload(MerchantRule.category), joinedload(MerchantRule.label))
        .order_by(MerchantRule.priority.asc(), MerchantRule.id.asc())
    ).unique().all()
    return [MerchantRuleResponse(**merchant_rule_response(rule)) for rule in rules]


@router.post("", response_model=MerchantRuleResponse)
def create_rule(
    payload: CreateMerchantRuleRequest,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MerchantRuleResponse:
    category = db.get(ExpenseCategory, payload.categoryId)
    if category is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category does not exist")
    label = db.get(ExpenseLabel, payload.labelId) if payload.labelId else None
    if payload.labelId and label is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Label does not exist")
    rule = MerchantRule(
        match_type=payload.matchType.lower(),
        pattern=normalize_match_value(payload.pattern),
        category_id=payload.categoryId,
        label_id=payload.labelId,
        priority=payload.priority,
        active=payload.active,
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    rule = get_rule_or_404(db, rule.id)
    return MerchantRuleResponse(**merchant_rule_response(rule))


@router.patch("/{rule_id}", response_model=MerchantRuleResponse)
def update_rule(
    rule_id: int,
    payload: UpdateMerchantRuleRequest,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MerchantRuleResponse:
    rule = get_rule_or_404(db, rule_id)
    if payload.categoryId:
        category = db.get(ExpenseCategory, payload.categoryId)
        if category is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category does not exist")
        rule.category_id = payload.categoryId
    if payload.labelId is not None:
        label = db.get(ExpenseLabel, payload.labelId) if payload.labelId else None
        if payload.labelId and label is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Label does not exist")
        rule.label_id = payload.labelId
    if payload.matchType is not None:
        rule.match_type = payload.matchType.lower()
    if payload.pattern is not None:
        rule.pattern = normalize_match_value(payload.pattern)
    if payload.priority is not None:
        rule.priority = payload.priority
    if payload.active is not None:
        rule.active = payload.active
    db.add(rule)
    db.commit()
    rule = get_rule_or_404(db, rule.id)
    return MerchantRuleResponse(**merchant_rule_response(rule))


@router.post("/seed-defaults", response_model=MerchantRuleSeedResponse)
async def seed_defaults(
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MerchantRuleSeedResponse:
    client = get_extend_client()
    try:
        categories_created = await seed_generic_categories_in_extend(db, client)
        await refresh_expense_categories(db, client)
        rules_created = seed_default_merchant_rules(db)
        await auto_assign_categorization_rules(db, client)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == status.HTTP_402_PAYMENT_REQUIRED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Extend rejected expense category creation for this account. Use existing Extend categories or switch to local-only categorization.",
            ) from exc
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Extend category seeding failed with {exc.response.status_code}.",
        ) from exc

    return MerchantRuleSeedResponse(
        categoriesCreated=categories_created,
        rulesCreated=rules_created,
        categoriesTotal=len(db.scalars(select(ExpenseCategory)).all()),
        rulesTotal=len(db.scalars(select(MerchantRule)).all()),
    )
