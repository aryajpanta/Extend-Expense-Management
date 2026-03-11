# Conventions

## Repo shape

- Keep the AI template isolated under `.ai`
- Keep project-specific instructions in root docs, not inside `.ai`
- Do not mix frontend-only tooling into the Python SDK package

## Backend

- FastAPI code lives under `server/app`
- Prefer explicit service-layer functions for Extend sync logic
- Maintain Python 3.9 compatibility for repo-wide Python code

## Frontend

- Next.js app code lives under `web/app`, `web/components`, and `web/lib`
- Preserve the current visual direction: clean personal workspace, inspired by Extend flow but not a clone

## Verification

- Default to `tools/verify.sh`
- If a change touches `web/`, ensure `npm run build` still passes
- If a change touches `server/` or `extend/`, ensure the backend pytest smoke set still passes

