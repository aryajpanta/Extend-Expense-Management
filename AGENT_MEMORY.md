# Agent Memory

Store durable, reusable knowledge only.

## Product truths

- This app is for one user only right now.
- The deployment target is local/self-hosted first, not multi-tenant SaaS.
- The UI should borrow Extend flow patterns, especially around transactions, but should not become a visual clone.
- Virtual-card management is not a product priority for this app.

## Repository truths

- `origin` is the personal GitHub repo: `aryajpanta/Extend-Expense-Management`
- `upstream` remains the original Extend SDK repo
- `.ai` is a git submodule pointing to `aryajpanta/ai-agent-template`
- Root docs are project-owned; `.ai` contents are template-owned

## Technical truths

- Backend: FastAPI in `server/app`
- Frontend: Next.js App Router in `web/`
- Local cache DB: SQLite in `data/expense_manager.db`
- Extend credentials are backend-only and come from env vars
- Repo-wide Python must stay compatible with Python 3.9 in this environment

## Verification truths

- Backend smoke tests:
  - `PYTHONPATH=. .venv/bin/pytest tests/app tests/test_client.py -q`
- Frontend verification baseline:
  - `cd web && npm run build`
- Combined verification:
  - `./tools/verify.sh`

## Implementation truths already learned

- Do not use Python 3.10+ union syntax (`str | None`) in repo Python code if it will be imported under Python 3.9.
- Do not use `match` statements in repo Python code while the local runtime remains 3.9.
- Browser-authenticated frontend pages should fetch from the FastAPI API client-side so cookies are naturally included.
- The FastAPI app currently performs a startup sync and background incremental sync; failures are swallowed during startup so the app can still boot without blocking.

