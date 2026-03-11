# Project Context

This repository started as the official Extend Python SDK and now also contains a personal expense management app.

## Product

- Single-user
- Web-only
- Local/self-hosted first
- Uses Extend as the external source of truth for transactions, receipts, and expense data

## Main runtime surfaces

- `extend/`: Extend API SDK
- `server/`: local backend that syncs Extend data into SQLite and exposes app APIs
- `web/`: local frontend for login, dashboard, transactions, categories, and settings

## Current constraints

- Python runtime in this environment is 3.9
- The app should not depend on direct frontend access to Extend credentials
- Virtual-card workflows are intentionally not a product priority for the app

