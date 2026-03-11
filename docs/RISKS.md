# Risks

## Product risks

- If the transaction detail workflow stays dependent on raw IDs, the app will remain technically functional but practically awkward.
- If dashboard insights stay too shallow, the app may feel like a thin wrapper instead of a useful daily tool.

## Technical risks

- Startup sync failures are currently swallowed so the app can boot; that is pragmatic, but it can hide real integration issues.
- The backend uses `create_all()` rather than versioned migrations, which raises schema drift risk over time.
- Sync behavior depends on real Extend account data shape, which may vary across organizations and endpoints.
- Combining SDK and product code in one repo increases the chance of accidental cross-surface regressions.

## Operational risks

- If submodules are not initialized on a fresh clone, `.ai` workflows will appear broken.
- Local SQLite is correct for v1, but careless file handling could still cause backup or portability issues.

