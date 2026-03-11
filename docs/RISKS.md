# Risks

- Backend currently bootstraps the DB schema with `create_all()` instead of versioned migrations.
- Transaction detail editing still uses raw category/label IDs in the UI and needs better affordances.
- Sync behavior depends on real Extend API responses that may vary by account shape.
- The repo now mixes SDK and app concerns, so careless edits can break one while working on the other.

