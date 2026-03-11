from server.app.services.sync import normalize_transaction, parse_datetime


def test_parse_datetime_handles_iso_and_date():
    assert parse_datetime("2026-03-11T12:30:00.000Z") is not None
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

