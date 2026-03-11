# Architecture

## Components

- Extend SDK
  - `extend/`
  - Handles authenticated API access to Extend
- App backend
  - `server/app`
  - FastAPI routes, session auth, SQLite persistence, sync service, and data normalization
- App frontend
  - `web/`
  - Next.js UI using browser-side fetches against the FastAPI API

## Data flow

1. User signs into the local app
2. Frontend calls FastAPI using session cookies
3. Backend reads/writes SQLite cache
4. Backend syncs or mutates data against Extend via the local SDK
5. Frontend renders cached data and mutation results

## Integration note

The SDK remains embedded in the same repo, but app-specific logic should stay outside `extend/` unless a real SDK bug or compatibility fix is required.

