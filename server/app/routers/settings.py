from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..config import get_settings
from ..database import get_db
from ..deps import get_current_user
from ..models import User
from ..schemas import SettingsResponse, SyncRunResponse
from ..services.sync import latest_sync_run


router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=SettingsResponse)
def get_settings_payload(_: User = Depends(get_current_user), db: Session = Depends(get_db)) -> SettingsResponse:
    settings = get_settings()
    latest = latest_sync_run(db)
    latest_payload = None
    if latest is not None:
        latest_payload = SyncRunResponse(
            id=latest.id,
            status=latest.status,
            startedAt=latest.started_at,
            finishedAt=latest.finished_at,
            transactionsFetched=latest.transactions_fetched,
            transactionsUpserted=latest.transactions_upserted,
            errorMessage=latest.error_message,
        )
    return SettingsResponse(
        extendEnvironment=settings.extend_env,
        hasExtendCredentials=settings.has_extend_credentials,
        maskedExtendKey=settings.masked_extend_key,
        latestSync=latest_payload,
    )

