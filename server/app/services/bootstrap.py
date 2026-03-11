from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import ROOT_DIR, get_settings
from ..models import User
from ..security import hash_password


def migrate_database() -> None:
    alembic_config = Config(str(ROOT_DIR / "alembic.ini"))
    alembic_config.set_main_option("script_location", str(ROOT_DIR / "alembic"))
    alembic_config.set_main_option("sqlalchemy.url", get_settings().database_url)
    command.upgrade(alembic_config, "head")


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
