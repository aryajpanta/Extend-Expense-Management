from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"


@dataclass(frozen=True)
class Settings:
    app_name: str
    api_prefix: str
    frontend_origin: str
    secret_key: str
    session_cookie_name: str
    session_days: int
    sync_interval_minutes: int
    sync_initial_days: int
    sync_incremental_days: int
    detail_freshness_minutes: int
    database_url: str
    app_admin_email: str
    app_admin_password: str
    extend_api_key: str
    extend_api_secret: str
    extend_env: str

    @property
    def has_extend_credentials(self) -> bool:
        return bool(self.extend_api_key and self.extend_api_secret)

    @property
    def masked_extend_key(self) -> str | None:
        if not self.extend_api_key:
            return None
        prefix = self.extend_api_key[:4]
        suffix = self.extend_api_key[-4:] if len(self.extend_api_key) > 8 else ""
        return f"{prefix}...{suffix}"


def get_settings() -> Settings:
    DATA_DIR.mkdir(exist_ok=True)
    db_path = os.getenv("APP_DB_PATH", str(DATA_DIR / "expense_manager.db"))
    return Settings(
        app_name="Extend Expense Manager",
        api_prefix="/api",
        frontend_origin=os.getenv("FRONTEND_ORIGIN", "http://localhost:3000"),
        secret_key=os.getenv("APP_SECRET_KEY", "dev-only-change-me"),
        session_cookie_name="expense_session",
        session_days=int(os.getenv("APP_SESSION_DAYS", "30")),
        sync_interval_minutes=int(os.getenv("APP_SYNC_INTERVAL_MINUTES", "15")),
        sync_initial_days=int(os.getenv("APP_SYNC_INITIAL_DAYS", "365")),
        sync_incremental_days=int(os.getenv("APP_SYNC_INCREMENTAL_DAYS", "90")),
        detail_freshness_minutes=int(os.getenv("APP_DETAIL_FRESHNESS_MINUTES", "15")),
        database_url=f"sqlite:///{db_path}",
        app_admin_email=os.getenv("APP_ADMIN_EMAIL", "owner@example.com"),
        app_admin_password=os.getenv("APP_ADMIN_PASSWORD", "change-me-now"),
        extend_api_key=os.getenv("EXTEND_API_KEY", ""),
        extend_api_secret=os.getenv("EXTEND_API_SECRET", ""),
        extend_env=os.getenv("ENV", "prod"),
    )

