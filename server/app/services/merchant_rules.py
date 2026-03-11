from __future__ import annotations

import re
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from extend import ExtendClient

from ..models import ExpenseCategory, ExpenseLabel, MerchantRule, Transaction
from .merchant_intelligence import infer_suggested_category


GENERIC_CATEGORIES: list[dict[str, Any]] = [
    {"name": "Shopping", "code": "SHOPPING", "required": False, "active": True, "freeTextAllowed": False},
    {"name": "Dining", "code": "DINING", "required": False, "active": True, "freeTextAllowed": False},
    {"name": "Travel", "code": "TRAVEL", "required": False, "active": True, "freeTextAllowed": False},
    {"name": "Gas", "code": "GAS", "required": False, "active": True, "freeTextAllowed": False},
    {"name": "Groceries", "code": "GROCERIES", "required": False, "active": True, "freeTextAllowed": False},
    {"name": "Home", "code": "HOME", "required": False, "active": True, "freeTextAllowed": False},
    {"name": "Health", "code": "HEALTH", "required": False, "active": True, "freeTextAllowed": False},
    {"name": "Entertainment", "code": "ENTERTAINMENT", "required": False, "active": True, "freeTextAllowed": False},
    {"name": "Pets", "code": "PETS", "required": False, "active": True, "freeTextAllowed": False},
    {"name": "Transport", "code": "TRANSPORT", "required": False, "active": True, "freeTextAllowed": False},
    {"name": "Bills", "code": "BILLS", "required": False, "active": True, "freeTextAllowed": False},
    {"name": "Other", "code": "OTHER", "required": False, "active": True, "freeTextAllowed": False},
]


DEFAULT_VENDOR_RULES: list[dict[str, Any]] = [
    {"match_type": "contains", "pattern": "AMAZON", "category_code": "SHOPPING"},
    {"match_type": "contains", "pattern": "TARGET", "category_code": "SHOPPING"},
    {"match_type": "contains", "pattern": "WALMART", "category_code": "SHOPPING"},
    {"match_type": "contains", "pattern": "HOMEGOODS", "category_code": "HOME"},
    {"match_type": "contains", "pattern": "HOME DEPOT", "category_code": "HOME"},
    {"match_type": "contains", "pattern": "LOWES", "category_code": "HOME"},
    {"match_type": "contains", "pattern": "WHOLE FOODS", "category_code": "GROCERIES"},
    {"match_type": "contains", "pattern": "TRADER JOES", "category_code": "GROCERIES"},
    {"match_type": "contains", "pattern": "STOP SHOP", "category_code": "GROCERIES"},
    {"match_type": "contains", "pattern": "INSTACART", "category_code": "GROCERIES"},
    {"match_type": "contains", "pattern": "UBER", "category_code": "TRANSPORT"},
    {"match_type": "contains", "pattern": "LYFT", "category_code": "TRANSPORT"},
    {"match_type": "contains", "pattern": "SHELL", "category_code": "GAS"},
    {"match_type": "contains", "pattern": "EXXON", "category_code": "GAS"},
    {"match_type": "contains", "pattern": "CHEVRON", "category_code": "GAS"},
    {"match_type": "contains", "pattern": "PMUSA", "category_code": "GAS"},
    {"match_type": "contains", "pattern": "CVS", "category_code": "HEALTH"},
    {"match_type": "contains", "pattern": "WALGREENS", "category_code": "HEALTH"},
    {"match_type": "contains", "pattern": "NETFLIX", "category_code": "ENTERTAINMENT"},
    {"match_type": "contains", "pattern": "SPOTIFY", "category_code": "ENTERTAINMENT"},
    {"match_type": "contains", "pattern": "AMC", "category_code": "ENTERTAINMENT"},
    {"match_type": "contains", "pattern": "PETCO", "category_code": "PETS"},
    {"match_type": "contains", "pattern": "PETSMART", "category_code": "PETS"},
    {"match_type": "contains", "pattern": "VALUE PET VET", "category_code": "PETS"},
]


MCC_GROUP_CATEGORY_CODES: dict[str, str] = {
    "TRANSPORTATION": "TRANSPORT",
    "RESTAURANTS": "DINING",
    "DINING": "DINING",
    "GROCERY_STORES": "GROCERIES",
    "GROCERY": "GROCERIES",
    "GAS_STATIONS": "GAS",
    "HOME_IMPROVEMENT": "HOME",
    "ENTERTAINMENT": "ENTERTAINMENT",
    "HEALTH_CARE": "HEALTH",
    "PET_SHOPS": "PETS",
    "RETAIL": "SHOPPING",
    "SHOPPING": "SHOPPING",
}


def normalize_match_value(value: str | None) -> str:
    if not value:
        return ""
    normalized = re.sub(r"[^A-Z0-9]+", " ", value.upper())
    return re.sub(r"\s+", " ", normalized).strip()


def merchant_rule_response(rule: MerchantRule) -> dict[str, Any]:
    return {
        "id": rule.id,
        "matchType": rule.match_type,
        "pattern": rule.pattern,
        "categoryId": rule.category_id,
        "labelId": rule.label_id,
        "priority": rule.priority,
        "active": rule.active,
        "categoryName": rule.category.name,
        "labelName": rule.label.name if rule.label else None,
    }


async def seed_generic_categories_in_extend(db: Session, client: ExtendClient) -> int:
    existing_codes = {
        category.code.upper(): category
        for category in db.scalars(select(ExpenseCategory)).all()
    }
    created = 0
    for item in GENERIC_CATEGORIES:
        if item["code"].upper() in existing_codes:
            continue
        await client.expense_data.create_expense_category(
            name=item["name"],
            code=item["code"],
            required=item["required"],
            active=item["active"],
            free_text_allowed=item["freeTextAllowed"],
        )
        created += 1
    return created


def seed_default_merchant_rules(db: Session) -> int:
    categories_by_code = {
        category.code.upper(): category
        for category in db.scalars(select(ExpenseCategory)).all()
    }
    existing = {
        (rule.match_type, rule.pattern, rule.category_id, rule.label_id)
        for rule in db.scalars(select(MerchantRule)).all()
    }
    created = 0
    for item in DEFAULT_VENDOR_RULES:
        category = categories_by_code.get(item["category_code"].upper())
        if category is None:
            continue
        pattern = normalize_match_value(item["pattern"])
        key = (item["match_type"], pattern, category.id, None)
        if key in existing:
            continue
        db.add(
            MerchantRule(
                match_type=item["match_type"],
                pattern=pattern,
                category_id=category.id,
                label_id=None,
                priority=100,
                active=True,
            )
        )
        existing.add(key)
        created += 1
    db.commit()
    return created


def merchant_candidates(payload: dict[str, Any]) -> list[str]:
    raw_candidates = [
        payload.get("merchantName"),
        payload.get("merchantDescriptor"),
        payload.get("mccDescription"),
    ]
    candidates = [normalize_match_value(value) for value in raw_candidates if value]
    return [candidate for candidate in candidates if candidate]


def build_assignment_for_payload(db: Session, payload: dict[str, Any]) -> tuple[str, str | None] | None:
    candidates = merchant_candidates(payload)
    rules = db.scalars(
        select(MerchantRule)
        .where(MerchantRule.active.is_(True))
        .order_by(MerchantRule.priority.asc(), MerchantRule.id.asc())
    ).all()

    for rule in rules:
        pattern = rule.pattern
        if rule.match_type == "exact" and any(candidate == pattern for candidate in candidates):
            return rule.category_id, rule.label_id
        if rule.match_type == "contains" and any(pattern in candidate for candidate in candidates):
            return rule.category_id, rule.label_id

    suggested_category_name, _ = infer_suggested_category(payload)
    if suggested_category_name:
        target = normalize_match_value(suggested_category_name)
        aliases = {
            "TRANSIT": ["TRANSPORT", "TRANSPORTATION"],
            "SOFTWARE": ["SUBSCRIPTIONS", "SOFTWARE SERVICES", "SAAS"],
            "GAS": ["FUEL"],
        }
        categories = db.scalars(select(ExpenseCategory).where(ExpenseCategory.active.is_(True))).all()
        for category in categories:
            normalized_name = normalize_match_value(category.name)
            normalized_code = normalize_match_value(category.code)
            if normalized_name == target or normalized_code == target:
                return category.id, None
            if normalized_name in aliases.get(target, []) or normalized_code in aliases.get(target, []):
                return category.id, None

    mcc_group = normalize_match_value(payload.get("mccGroupKey") or payload.get("mccGroup"))
    fallback_code = MCC_GROUP_CATEGORY_CODES.get(mcc_group)
    if not fallback_code:
        return None

    fallback_category = db.scalar(select(ExpenseCategory).where(ExpenseCategory.code == fallback_code))
    if fallback_category is None:
        return None
    return fallback_category.id, None


def transaction_needs_assignment(transaction: Transaction) -> bool:
    return not bool(transaction.detail and transaction.detail.expense_details)


async def auto_assign_transaction_expense_data(
    db: Session,
    client: ExtendClient,
    transactions: list[Transaction],
    upsert_transaction: Any,
) -> int:
    updates = 0
    for transaction in transactions:
        if not transaction_needs_assignment(transaction):
            continue
        assignment = build_assignment_for_payload(db, transaction.raw_payload or {})
        if assignment is None:
            continue
        category_id, label_id = assignment
        payload = {"expenseDetails": [{"categoryId": category_id}]}
        if label_id:
            payload["expenseDetails"][0]["labelId"] = label_id
        try:
            response = await client.transactions.update_transaction_expense_data(transaction.id, payload)
        except Exception:
            continue
        upsert_transaction(db, response.get("transaction", response))
        updates += 1
    if updates:
        db.commit()
    return updates
