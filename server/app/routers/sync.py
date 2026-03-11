from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import User
from ..schemas import SyncRunResponse
from ..services.extend_api import get_extend_client
from ..services.sync import latest_sync_run, run_sync_cycle


router = APIRouter(prefix="/sync", tags=["sync"])


@router.get("/status", response_model=Optional[SyncRunResponse])
def get_sync_status(_: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Optional[SyncRunResponse]:
    latest = latest_sync_run(db)
    if latest is None:
        return None
    return SyncRunResponse(
        id=latest.id,
        status=latest.status,
        startedAt=latest.started_at,
        finishedAt=latest.finished_at,
        transactionsFetched=latest.transactions_fetched,
        transactionsUpserted=latest.transactions_upserted,
        errorMessage=latest.error_message,
    )


@router.post("/run", response_model=SyncRunResponse)
async def run_sync(_: User = Depends(get_current_user), db: Session = Depends(get_db)) -> SyncRunResponse:
    latest = await run_sync_cycle(db, get_extend_client())
    return SyncRunResponse(
        id=latest.id,
        status=latest.status,
        startedAt=latest.started_at,
        finishedAt=latest.finished_at,
        transactionsFetched=latest.transactions_fetched,
        transactionsUpserted=latest.transactions_upserted,
        errorMessage=latest.error_message,
    )
