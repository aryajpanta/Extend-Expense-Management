from __future__ import annotations

import re
from typing import Any


RESEARCHED_MERCHANT_RULES: list[dict[str, str]] = [
    {
        "pattern": "AMAZON",
        "category": "Shopping",
        "reason": "Amazon is an online retail marketplace, so charges fit a general shopping bucket.",
        "source": "https://www.amazon.com/",
    },
    {
        "pattern": "TJMAXX",
        "category": "Shopping",
        "reason": "T.J.Maxx is a discount apparel and home fashions retailer.",
        "source": "https://www.tjx.com/company/our-brands",
    },
    {
        "pattern": "HOMEGOODS",
        "category": "Home",
        "reason": "HomeGoods sells home decor, furnishings, and kitchen/home items.",
        "source": "https://www.homegoods.com/",
    },
    {
        "pattern": "VALUE PET VET",
        "category": "Pets",
        "reason": "Value Pet Vet provides veterinary care, so this fits a pets category.",
        "source": "https://valuepetvet.com/",
    },
    {
        "pattern": "WALTER AI",
        "category": "Software",
        "reason": "Walter is an AI writing/productivity service, so this fits software and subscriptions.",
        "source": "https://walterwrites.ai/",
    },
    {
        "pattern": "PMUSA",
        "category": "Gas",
        "reason": "PMUSA transactions are fuel-station style merchant descriptors and fit gas/fuel spending.",
        "source": "https://www.bp.com/",
    },
    {
        "pattern": "CITGO",
        "category": "Gas",
        "reason": "CITGO is a gas station and fuel brand.",
        "source": "https://www.citgo.com/",
    },
    {
        "pattern": "MTA",
        "category": "Transit",
        "reason": "MTA/OMNY is public transit fare payment in New York.",
        "source": "https://new.mta.info/fares/omny",
    },
]


MCC_GROUP_FALLBACKS: dict[str, tuple[str, str]] = {
    "TRANSPORTATION": ("Transit", "Card-network MCC group indicates transportation."),
    "RESTAURANTS": ("Dining", "Card-network MCC group indicates restaurants or dining."),
    "DINING": ("Dining", "Card-network MCC group indicates restaurants or dining."),
    "GROCERY_STORES": ("Groceries", "Card-network MCC group indicates grocery spending."),
    "GROCERY": ("Groceries", "Card-network MCC group indicates grocery spending."),
    "GAS_STATIONS": ("Gas", "Card-network MCC group indicates fuel purchases."),
    "HEALTH_CARE": ("Health", "Card-network MCC group indicates healthcare."),
    "PET_SHOPS": ("Pets", "Card-network MCC group indicates pet-related spending."),
    "RETAIL": ("Shopping", "Card-network MCC group indicates general retail shopping."),
    "HOME_IMPROVEMENT": ("Home", "Card-network MCC group indicates home spending."),
}


def normalize_merchant_text(value: str | None) -> str:
    if not value:
        return ""
    normalized = re.sub(r"[^A-Z0-9]+", " ", value.upper())
    return re.sub(r"\s+", " ", normalized).strip()


def infer_suggested_category(payload: dict[str, Any]) -> tuple[str | None, str | None]:
    candidates = [
        normalize_merchant_text(payload.get("merchantName")),
        normalize_merchant_text(payload.get("merchantDescriptor")),
        normalize_merchant_text(payload.get("mccDescription")),
    ]
    for rule in RESEARCHED_MERCHANT_RULES:
        if any(rule["pattern"] in candidate for candidate in candidates if candidate):
            return rule["category"], rule["reason"]

    mcc_group = normalize_merchant_text(payload.get("mccGroupKey") or payload.get("mccGroup"))
    fallback = MCC_GROUP_FALLBACKS.get(mcc_group)
    if fallback:
        return fallback
    return None, None
