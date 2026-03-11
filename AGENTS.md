# Project Agent Guide

Use the AI workflow assets from the [`.ai`](/Users/aryajpanta/Extend-Python/extend-python/.ai) submodule as the reusable system of record.

Before making changes in this repo:

1. Read [`.ai/agent/AGENTS.md`](/Users/aryajpanta/Extend-Python/extend-python/.ai/agent/AGENTS.md)
2. Read [`.ai/agent/RULES.md`](/Users/aryajpanta/Extend-Python/extend-python/.ai/agent/RULES.md)
3. Read [agent/COMMANDS.md](/Users/aryajpanta/Extend-Python/extend-python/agent/COMMANDS.md)
4. Read [docs/PROJECT_CONTEXT.md](/Users/aryajpanta/Extend-Python/extend-python/docs/PROJECT_CONTEXT.md)
5. Read [docs/ARCHITECTURE.md](/Users/aryajpanta/Extend-Python/extend-python/docs/ARCHITECTURE.md)
6. Read [docs/REQUIREMENTS.md](/Users/aryajpanta/Extend-Python/extend-python/docs/REQUIREMENTS.md)

Working expectations for this repo:

- Treat [server/](/Users/aryajpanta/Extend-Python/extend-python/server) and [web/](/Users/aryajpanta/Extend-Python/extend-python/web) as the active app surfaces.
- Treat [extend/](/Users/aryajpanta/Extend-Python/extend-python/extend) as the upstream SDK layer. Avoid unnecessary churn there.
- Keep the `.ai` submodule isolated. Do not edit template files inside `.ai` unless you intentionally want to update the pinned template revision.
- Put project-specific guidance in root files like [AGENT_MEMORY.md](/Users/aryajpanta/Extend-Python/extend-python/AGENT_MEMORY.md), [TASK_QUEUE.md](/Users/aryajpanta/Extend-Python/extend-python/TASK_QUEUE.md), and the docs under [docs/](/Users/aryajpanta/Extend-Python/extend-python/docs).
- Use [tools/verify.sh](/Users/aryajpanta/Extend-Python/extend-python/tools/verify.sh) as the default verification entry point before closing work.

