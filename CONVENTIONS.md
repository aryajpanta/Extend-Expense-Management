# Conventions

## Repository boundaries

- Keep `.ai` isolated as a submodule.
- Keep project-specific agent instructions in root docs, not in `.ai`.
- Keep app-only logic out of `extend/` unless a real SDK-level change is required.

## Backend conventions

- Put API route code in `server/app/routers/`.
- Put non-trivial business and sync logic in `server/app/services/`.
- Keep schema, auth, persistence, and sync concerns clearly separated.
- Preserve Python 3.9 compatibility in backend and SDK code.
- Prefer explicit normalization functions over hidden model magic when adapting Extend payloads.

## Frontend conventions

- Keep page entry points in `web/app/`.
- Keep shared UI in `web/components/`.
- Keep API helper code and shared formatters in `web/lib/`.
- Maintain the existing visual direction:
  - calm personal workspace
  - left-rail navigation
  - Extend-inspired transaction workflow
  - not an Extend branding clone

## Product conventions

- Optimize for one-user clarity over generic admin flexibility.
- Favor quick transaction review and cleanup workflows.
- Use local cache speed, but keep Extend as the source of truth for remote mutations.

## Verification conventions

- Run `./tools/verify.sh` before closing meaningful work.
- If changing backend or SDK behavior, run the backend smoke tests.
- If changing frontend code, ensure `cd web && npm run build` still passes.

