from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta

from .config import get_settings


def hash_password(password: str, salt: str | None = None) -> str:
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 200_000).hex()
    return f"{salt}${digest}"


def verify_password(password: str, password_hash: str) -> bool:
    salt, stored_hash = password_hash.split("$", 1)
    candidate = hash_password(password, salt).split("$", 1)[1]
    return hmac.compare_digest(candidate, stored_hash)


def generate_session_token() -> str:
    return secrets.token_urlsafe(32)


def sign_session_token(token: str) -> str:
    secret = get_settings().secret_key.encode()
    signature = hmac.new(secret, token.encode(), hashlib.sha256).digest()
    return f"{token}.{base64.urlsafe_b64encode(signature).decode().rstrip('=')}"


def unsign_session_token(signed_token: str) -> str | None:
    try:
        token, encoded_sig = signed_token.rsplit(".", 1)
    except ValueError:
        return None
    padding = "=" * (-len(encoded_sig) % 4)
    expected_sig = hmac.new(get_settings().secret_key.encode(), token.encode(), hashlib.sha256).digest()
    actual_sig = base64.urlsafe_b64decode(encoded_sig + padding)
    if not hmac.compare_digest(expected_sig, actual_sig):
        return None
    return token


def session_expiry(days: int) -> datetime:
    return datetime.utcnow() + timedelta(days=days)

