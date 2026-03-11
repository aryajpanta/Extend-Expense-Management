# Decisions

- Preserve full Extend history in this repository rather than starting from a fresh repo.
- Keep Extend as `upstream` and the personal repo as `origin`.
- Integrate the AI template as a `.ai` git submodule rather than copying template files into the app tree.
- Build the product as FastAPI plus Next.js inside the same repo as the SDK.
- Keep the app single-user and local/self-hosted first.
- Use SQLite for the first version.
- Keep the visual language inspired by Extend flow patterns but not visually identical to Extend.
- Treat `extend/` as an SDK boundary, not the default place for app feature work.
