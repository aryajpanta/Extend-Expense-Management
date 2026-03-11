# Agent Memory

Durable project knowledge only.

- The app is a single-user personal expense manager built on top of the Extend SDK in the same repo.
- The active backend is FastAPI under `server/`.
- The active frontend is Next.js under `web/`.
- The SDK under `extend/` must remain usable on Python 3.9 in this environment.
- The `.ai` directory is a git submodule pointing to `aryajpanta/ai-agent-template`.
- Use `PYTHONPATH=. .venv/bin/pytest tests/app tests/test_client.py -q` for the backend smoke test set.
- Use `npm run build` inside `web/` as the frontend verification baseline.

