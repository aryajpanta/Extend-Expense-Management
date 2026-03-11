# Commands

## Install

- `python3 -m venv .venv`
- `.venv/bin/pip install '.[app,dev]'`
- `cd web && npm install`

## Backend dev

- `PYTHONPATH=. .venv/bin/uvicorn server.app.main:app --reload`

## Frontend dev

- `cd web && npm run dev`

## Tests

- `PYTHONPATH=. .venv/bin/pytest tests/app tests/test_client.py -q`

## Build

- `cd web && npm run build`

## Verify

- `./tools/verify.sh`

