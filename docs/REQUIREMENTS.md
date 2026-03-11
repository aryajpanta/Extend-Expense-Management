# Requirements

## Functional requirements

- The app must support a single local admin login.
- The app must show a dashboard with spend and sync visibility.
- The app must list transactions from the local cache.
- The app must show transaction detail and refresh stale detail when needed.
- The app must allow receipt uploads for a transaction through the backend.
- The app must allow expense category assignment updates for a transaction.
- The app must cache Extend expense categories and labels locally.
- The app must allow manual sync from the UI.
- The app must run a recurring background sync.

## Non-functional requirements

- The app must keep Extend credentials backend-only.
- The app must stay compatible with the current local Python 3.9 runtime.
- The repo must preserve Extend upstream history.
- The AI template repo must remain isolated as a submodule, not copied into app code.
- Local verification must stay simple and repeatable through one project command.

## UX requirements

- The transaction list must remain a primary workflow surface.
- The interface should feel lighter and more personal than Extend’s default UI.
- The user should be able to identify missing receipts and missing categories quickly.

