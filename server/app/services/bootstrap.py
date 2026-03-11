from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import get_settings
from ..database import Base, engine
from ..models import User
from ..security import hash_password


def init_database() -> None:
    Base.metadata.create_all(bind=engine)


def bootstrap_admin(db: Session) -> None:
    settings = get_settings()
    existing = db.scalar(select(User).where(User.email == settings.app_admin_email))
    if existing is not None:
        return

    user = User(
        email=settings.app_admin_email,
        password_hash=hash_password(settings.app_admin_password),
    )
    db.add(user)
    db.commit()

