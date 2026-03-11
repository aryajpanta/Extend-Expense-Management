# Project Map

## Top-level structure

- `extend/`: upstream Extend Python SDK
- `server/`: FastAPI backend for auth, sync, cache, and API routes
- `web/`: Next.js frontend for the personal expense manager
- `tests/`: SDK tests plus app-focused backend tests under `tests/app`
- `docs/`: project docs and app setup material
- `data/`: local SQLite path for the expense manager app
- `.ai/`: AI template submodule
- `tools/`: project-local helper scripts

## Working focus

- App product work usually lands in `server/`, `web/`, `docs/`, and `tests/app/`
- SDK compatibility or Extend integration fixes land in `extend/`

## Verification workflow

1. Backend checks via `tools/verify.sh`
2. Frontend production build via `web/npm run build`
3. Update `AGENT_MEMORY.md` only with durable learnings

