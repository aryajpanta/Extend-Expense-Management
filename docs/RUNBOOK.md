# Runbook

## First-time setup

1. `python3 -m venv .venv`
2. `.venv/bin/pip install '.[app,dev]'`
3. `cp server/.env.example .env` and fill in credentials
4. `cd web && cp .env.local.example .env.local && npm install`

## Run

- Backend: `PYTHONPATH=. .venv/bin/uvicorn server.app.main:app --reload`
- Frontend: `cd web && npm run dev`

## Verify

- `./tools/verify.sh`

