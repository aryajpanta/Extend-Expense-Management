# Expense Atlas

This repo now contains a personal expense management app on top of the Extend SDK.

## Structure

- `server/`: FastAPI backend with auth, local cache, and Extend sync logic
- `web/`: Next.js frontend
- `data/`: SQLite database location for local use
- `extend/`: original Extend SDK package used by the backend

## Backend setup

1. Create a Python virtual environment.
2. Install the SDK plus app dependencies:
   `pip install -e ".[app,dev]"`
3. Copy `server/.env.example` to `.env` or export the variables manually.
4. Run the API:
   `uvicorn server.app.main:app --reload`

## Frontend setup

1. Copy `web/.env.local.example` to `web/.env.local`.
2. Install frontend dependencies inside `web/`:
   `npm install`
3. Run the app:
   `npm run dev`

## Notes

- The backend bootstraps one admin user from `APP_ADMIN_EMAIL` and `APP_ADMIN_PASSWORD`.
- The first sync attempts to backfill the last 365 days of transactions.
- The backend runs a recurring background sync every 15 minutes after startup.
- Virtual-card workflows are intentionally not surfaced in the UI.

