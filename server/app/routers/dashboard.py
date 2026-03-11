from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import User
from ..schemas import DashboardSummary
from ..services.sync import dashboard_summary


router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(_: User = Depends(get_current_user), db: Session = Depends(get_db)) -> DashboardSummary:
    return DashboardSummary(**dashboard_summary(db))

