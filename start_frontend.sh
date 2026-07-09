#!/bin/bash
# Builds the frontend (if not already built) and serves frontend/dist as
# static files, passing the port directly on the command line. Reads
# FRONTEND_PORT from the project's single root .env, defaulting to 8005.
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

if [ -f .env ]; then
  set -a
  source .env
  set +a
fi

echo "Starting frontend on port ${FRONTEND_PORT:-8005}..."
exec python3 frontend/serve.py "${FRONTEND_PORT:-8005}"
