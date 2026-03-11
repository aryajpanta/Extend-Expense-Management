# Commands

## Clone

- `git clone --recurse-submodules git@github.com:aryajpanta/Extend-Expense-Management.git`

## Install

- `python3 -m venv .venv`
- `.venv/bin/pip install '.[app,dev]'`
- `cp server/.env.example .env`
- `cd web && cp .env.local.example .env.local && npm install`

## Backend dev

- `PYTHONPATH=. .venv/bin/uvicorn server.app.main:app --reload`

## Frontend dev

- `cd web && npm run dev`

## Backend tests

- `PYTHONPATH=. .venv/bin/pytest tests/app tests/test_client.py -q`

## Frontend build

- `cd web && npm run build`

## Verify

- `./tools/verify.sh`

## Git

- `git submodule update --init --recursive`

