# Architecture

## System overview

The repository has three main runtime layers:

1. SDK layer
   - `extend/`
   - Wraps Extend API endpoints and auth
2. App backend
   - `server/app/`
   - Owns local auth, SQLite persistence, sync orchestration, normalization, and app-facing APIs
3. App frontend
   - `web/`
   - Owns the browser UI and calls the FastAPI backend with session cookies

## Backend responsibilities

- bootstrap one admin user from env
- manage signed cookie sessions
- sync transactions and expense metadata from Extend into SQLite
- refresh transaction details on demand when stale
- proxy expense-data and receipt mutations to Extend
- expose app-friendly API endpoints for the frontend

## Frontend responsibilities

- render dashboard, transactions, categories, and settings
- keep the app usable with local cached data
- trigger syncs and mutations through the backend
- preserve the transaction-review workflow shape from Extend without cloning its styling

## Persistence model

- SQLite is the local source for fast reads
- Extend remains the remote source of truth
- Transaction summaries, details, receipts, expense categories, expense labels, and sync runs are cached locally

## Sync model

- startup sync on app boot
- recurring background sync every 15 minutes
- first sync backfills a larger date window
- later syncs use a rolling incremental window
- transaction detail is refreshed live if the local cached detail is stale

## Current technical debt

- schema creation still uses `create_all()` rather than Alembic migrations
- category/label selection UX is not yet backed by rich frontend selectors
- dashboard visualizations are still minimal

