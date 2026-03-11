# Project Agent Guide

This repository uses the reusable agent system in [`.ai/`](/Users/aryajpanta/Extend-Python/extend-python/.ai), but all project-specific instructions live in the root files of this repo.

## Read Order

1. [`.ai/agent/AGENTS.md`](/Users/aryajpanta/Extend-Python/extend-python/.ai/agent/AGENTS.md)
2. [`.ai/agent/RULES.md`](/Users/aryajpanta/Extend-Python/extend-python/.ai/agent/RULES.md)
3. [agent/COMMANDS.md](/Users/aryajpanta/Extend-Python/extend-python/agent/COMMANDS.md)
4. [docs/PROJECT_CONTEXT.md](/Users/aryajpanta/Extend-Python/extend-python/docs/PROJECT_CONTEXT.md)
5. [docs/ARCHITECTURE.md](/Users/aryajpanta/Extend-Python/extend-python/docs/ARCHITECTURE.md)
6. [docs/REQUIREMENTS.md](/Users/aryajpanta/Extend-Python/extend-python/docs/REQUIREMENTS.md)
7. [TASK_QUEUE.md](/Users/aryajpanta/Extend-Python/extend-python/TASK_QUEUE.md)

## What This Repo Is

- An Extend SDK repo with preserved upstream history
- A personal expense manager app layered into the same repository
- A local/self-hosted, single-user web app
- A repo that now has three active surfaces:
  - [extend/](/Users/aryajpanta/Extend-Python/extend-python/extend): SDK and Extend integration layer
  - [server/](/Users/aryajpanta/Extend-Python/extend-python/server): FastAPI backend and SQLite cache
  - [web/](/Users/aryajpanta/Extend-Python/extend-python/web): Next.js frontend

## Operating Rules For This Repo

- Keep the [`.ai/`](/Users/aryajpanta/Extend-Python/extend-python/.ai) submodule isolated. Do not edit template files there unless intentionally updating the submodule pointer.
- Put durable project-specific knowledge in [AGENT_MEMORY.md](/Users/aryajpanta/Extend-Python/extend-python/AGENT_MEMORY.md).
- Put concrete work intake in [TASK_QUEUE.md](/Users/aryajpanta/Extend-Python/extend-python/TASK_QUEUE.md).
- Prefer implementing app behavior in `server/` and `web/` rather than bending the SDK to fit app-only concerns.
- Only touch `extend/` when fixing real SDK issues, compatibility problems, or Extend API integration gaps.
- Maintain Python 3.9 compatibility for Python code in this repo.
- Use [tools/verify.sh](/Users/aryajpanta/Extend-Python/extend-python/tools/verify.sh) before closing meaningful work.

## Current Product Direction

- Preserve the flow familiarity of Extend, especially the transaction-list-first workflow
- Do not replicate Extend’s full enterprise scope
- Prioritize:
  - dashboard usefulness
  - transaction detail cleanup
  - receipt handling
  - expense categorization
  - local reliability

## Current Gaps Agents Should Expect

- The backend still uses `create_all()` instead of migrations
- The transaction detail page still uses raw category and label IDs instead of dropdowns
- The category UI is only partially implemented
- Playwright coverage has not been added yet

