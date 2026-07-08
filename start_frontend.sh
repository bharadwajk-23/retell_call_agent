#!/bin/bash
# Builds the frontend (if not already built) and serves frontend/dist as
# static files. Reads FRONTEND_PORT from the project's single root .env,
# defaulting to 8005 if it isn't set there.
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR/frontend"

if [ ! -d node_modules ]; then
  echo "frontend/node_modules not found. Run ./initialize.sh first." >&2
  exit 1
fi

if [ ! -d dist ]; then
  echo "No production build found — building frontend..."
  npm run build
fi

cd "$PROJECT_DIR"

FRONTEND_PORT=$(grep -E '^\s*FRONTEND_PORT\s*=' .env 2>/dev/null | head -1 | cut -d'=' -f2 | tr -d ' \r')
FRONTEND_PORT=${FRONTEND_PORT:-8005}

echo "Starting frontend on port ${FRONTEND_PORT}..."
FRONTEND_PORT="$FRONTEND_PORT" exec python3 frontend/serve.py
