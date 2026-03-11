# Task Queue

## Active

- Finish the expense manager MVP so the app is genuinely usable day to day for reviewing transactions, fixing category assignments, and tracking missing receipts.

## Next Up

- Replace transaction detail raw category/label text inputs with fetched category and label selectors
- Add category label listing, creation, and editing flows in the frontend
- Add Alembic migrations and remove direct dependency on `Base.metadata.create_all()`
- Add transaction filters to the frontend list page that map to the backend query interface
- Add login/session UX guards so unauthenticated users are redirected cleanly to `/login`
- Add meaningful dashboard charts or trend summaries instead of only static top lists

## After That

- Add Playwright end-to-end tests for login, sync, transactions, receipts, and categories
- Add better sync observability in settings and dashboard
- Add richer search and saved views
- Add export/backup support for the local cache

## Deferred

- Multi-user auth
- Cloud-first deployment concerns
- Broad Extend account-management surfaces like people, cards, and enterprise settings

