# Project Map

## Top-level directories

- `.ai/`
  - AI template submodule
  - reusable agent workflows and templates
- `agent/`
  - project-specific command surface for agents
- `data/`
  - local SQLite target path
- `docs/`
  - project-specific product, architecture, and runbook docs
- `extend/`
  - upstream Extend Python SDK
- `server/`
  - FastAPI backend for auth, sync, cache, and API routes
- `tests/`
  - SDK tests plus app backend smoke tests in `tests/app`
- `tools/`
  - project-local helper commands like `verify.sh`
- `web/`
  - Next.js frontend

## High-value files

- [server/app/main.py](/Users/aryajpanta/Extend-Python/extend-python/server/app/main.py)
  - FastAPI app creation and startup sync behavior
- [server/app/services/sync.py](/Users/aryajpanta/Extend-Python/extend-python/server/app/services/sync.py)
  - Extend sync, normalization, detail refresh, and dashboard aggregation
- [server/app/models.py](/Users/aryajpanta/Extend-Python/extend-python/server/app/models.py)
  - SQLite schema via SQLAlchemy models
- [web/app/dashboard/page.tsx](/Users/aryajpanta/Extend-Python/extend-python/web/app/dashboard/page.tsx)
  - dashboard entry point
- [web/app/transactions/page.tsx](/Users/aryajpanta/Extend-Python/extend-python/web/app/transactions/page.tsx)
  - transaction list entry point
- [web/app/transactions/[id]/page.tsx](/Users/aryajpanta/Extend-Python/extend-python/web/app/transactions/[id]/page.tsx)
  - transaction detail, receipt upload, and expense-data mutation UI
- [tools/verify.sh](/Users/aryajpanta/Extend-Python/extend-python/tools/verify.sh)
  - default verification entry point

## Change boundaries

- App product changes:
  - usually `server/`, `web/`, `docs/`, `tests/app/`
- SDK/API compatibility fixes:
  - `extend/`
- AI workflow customization:
  - root docs, `agent/`, `tools/`
- Template updates:
  - update the `.ai` submodule pointer, do not edit `.ai` files directly

