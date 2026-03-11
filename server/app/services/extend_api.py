from __future__ import annotations

from fastapi import HTTPException, status

from extend import ExtendClient
from extend.auth import BasicAuth

from ..config import get_settings


def get_extend_client() -> ExtendClient:
    settings = get_settings()
    if not settings.has_extend_credentials:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Extend credentials are not configured",
        )

    return ExtendClient(auth=BasicAuth(settings.extend_api_key, settings.extend_api_secret))

