#!/usr/bin/env bash
set -euo pipefail

echo "VERIFY: backend tests"
PYTHONPATH=. .venv/bin/pytest tests/app tests/test_client.py -q

echo "VERIFY: frontend build"
(
  cd web
  npm run build
)
