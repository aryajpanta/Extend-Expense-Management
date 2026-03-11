from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .database import db_context
from .routers import auth, categories, dashboard, merchant_rules, settings as settings_router, sync, transactions
from .services.bootstrap import bootstrap_admin, migrate_database
from .services.extend_api import get_extend_client
from .services.sync import run_sync_cycle


async def sync_forever() -> None:
    settings = get_settings()
    while True:
        try:
            with db_context() as db:
                await run_sync_cycle(db, get_extend_client())
        except Exception:
            pass
        await asyncio.sleep(settings.sync_interval_minutes * 60)


@asynccontextmanager
async def lifespan(app: FastAPI):
    migrate_database()
    with db_context() as db:
        bootstrap_admin(db)
    try:
        with db_context() as db:
            await run_sync_cycle(db, get_extend_client())
    except Exception:
        pass
    app.state.sync_task = asyncio.create_task(sync_forever())
    yield
    app.state.sync_task.cancel()


def create_app() -> FastAPI:
    app_settings = get_settings()
    app = FastAPI(title=app_settings.app_name, lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=app_settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(auth.router, prefix=app_settings.api_prefix)
    app.include_router(dashboard.router, prefix=app_settings.api_prefix)
    app.include_router(sync.router, prefix=app_settings.api_prefix)
    app.include_router(transactions.router, prefix=app_settings.api_prefix)
    app.include_router(categories.router, prefix=app_settings.api_prefix)
    app.include_router(merchant_rules.router, prefix=app_settings.api_prefix)
    app.include_router(settings_router.router, prefix=app_settings.api_prefix)
    return app


app = create_app()
