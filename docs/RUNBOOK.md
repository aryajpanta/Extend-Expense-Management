# Runbook

## Clone

```bash
git clone --recurse-submodules git@github.com:aryajpanta/Extend-Expense-Management.git
cd Extend-Expense-Management
```

If already cloned:

```bash
git submodule update --init --recursive
```

## First-time setup

```bash
python3 -m venv .venv
.venv/bin/pip install '.[app,dev]'
cp server/.env.example .env
cd web
cp .env.local.example .env.local
npm install
cd ..
```

## Required configuration

Fill `.env` with:

- `APP_ADMIN_EMAIL`
- `APP_ADMIN_PASSWORD`
- `APP_SECRET_KEY`
- `EXTEND_API_KEY`
- `EXTEND_API_SECRET`
- optional `ENV=stage|prod`

## Run the app

Backend:

```bash
PYTHONPATH=. .venv/bin/alembic upgrade head
PYTHONPATH=. .venv/bin/uvicorn server.app.main:app --reload
```

Frontend:

```bash
cd web
npm run dev
```

## Verify

```bash
./tools/verify.sh
```
