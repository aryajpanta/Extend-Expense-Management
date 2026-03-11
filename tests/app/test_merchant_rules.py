from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from server.app.database import Base
from server.app.models import ExpenseCategory, MerchantRule, Transaction, TransactionDetail
from server.app.services.merchant_rules import (
    build_assignment_for_payload,
    normalize_match_value,
    seed_default_merchant_rules,
)


def make_session() -> Session:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, future=True)()


def test_normalize_match_value_collapses_vendor_name():
    assert normalize_match_value("Amazon.com   Marketplace") == "AMAZON COM MARKETPLACE"
    assert normalize_match_value("PMUSA 730022 / Rowayton") == "PMUSA 730022 ROWAYTON"


def test_build_assignment_for_payload_uses_merchant_rule():
    db = make_session()
    category = ExpenseCategory(
        id="cat_shopping",
        name="Shopping",
        code="SHOPPING",
        active=True,
        required=False,
        free_text_allowed=False,
        raw_payload={},
        synced_at=datetime.utcnow(),
    )
    db.add(category)
    db.flush()
    db.add(
        MerchantRule(
            match_type="contains",
            pattern="AMAZON",
            category_id=category.id,
            priority=100,
            active=True,
        )
    )
    db.commit()

    assignment = build_assignment_for_payload(
        db,
        {
            "merchantName": "Amazon Marketplace",
            "mccGroupKey": "RETAIL",
        },
    )

    assert assignment == ("cat_shopping", None)


def test_build_assignment_for_payload_falls_back_to_mcc_group():
    db = make_session()
    category = ExpenseCategory(
        id="cat_transport",
        name="Transport",
        code="TRANSPORT",
        active=True,
        required=False,
        free_text_allowed=False,
        raw_payload={},
        synced_at=datetime.utcnow(),
    )
    db.add(category)
    db.commit()

    assignment = build_assignment_for_payload(
        db,
        {
            "merchantName": "Unknown Vendor",
            "mccGroupKey": "TRANSPORTATION",
        },
    )

    assert assignment == ("cat_transport", None)


def test_seed_default_merchant_rules_creates_rules_for_existing_generic_categories():
    db = make_session()
    db.add_all(
        [
            ExpenseCategory(
                id="cat_shopping",
                name="Shopping",
                code="SHOPPING",
                active=True,
                required=False,
                free_text_allowed=False,
                raw_payload={},
                synced_at=datetime.utcnow(),
            ),
            ExpenseCategory(
                id="cat_home",
                name="Home",
                code="HOME",
                active=True,
                required=False,
                free_text_allowed=False,
                raw_payload={},
                synced_at=datetime.utcnow(),
            ),
        ]
    )
    db.commit()

    created = seed_default_merchant_rules(db)

    assert created >= 2
    assert db.query(MerchantRule).count() >= 2
