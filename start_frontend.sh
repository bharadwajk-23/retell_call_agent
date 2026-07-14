#!/bin/bash
# Serves frontend/dist with uvicorn (see frontend/serve.py), using
# frontend/venv. Reads FRONTEND_PORT from the project's single root .env,
# defaulting to 8005. Does NOT run `npm run build` — vite.config.js was
# removed, so rebuild manually (with a base-path config restored) before
# relying on this for anything other than the dist/ already checked in.
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR/frontend"

if [ ! -d dist ]; then
  echo "frontend/dist not found — nothing to serve. Build it first." >&2
  exit 1
fi

if [ ! -d venv ]; then
  echo "frontend/venv not found. Run ./initialize.sh first." >&2
  exit 1
fi

cd "$PROJECT_DIR"

if [ -f .env ]; then
  set -a
  source .env
  set +a
fi

cd "$PROJECT_DIR/frontend"
source venv/bin/activate

echo "Starting frontend on port ${FRONTEND_PORT:-8005}..."
exec uvicorn serve:app --host 0.0.0.0 --port "${FRONTEND_PORT:-8005}"
