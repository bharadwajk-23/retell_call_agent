#!/bin/bash
# Starts the FastAPI backend directly with uvicorn, using backend/venv and
# the project's single root .env for HOST/PORT/ENV.
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ ! -d "$PROJECT_DIR/backend/venv" ]; then
  echo "backend/venv not found. Run ./initialize.sh first." >&2
  exit 1
fi

if [ ! -f "$PROJECT_DIR/.env" ]; then
  echo ".env not found. Copy .env.example to .env and fill in your values." >&2
  exit 1
fi

set -a
source "$PROJECT_DIR/.env"
set +a

cd "$PROJECT_DIR/backend"
source venv/bin/activate

RELOAD_FLAG=()
if [ "${ENV:-development}" != "production" ]; then
  RELOAD_FLAG=(--reload)
fi

echo "Starting backend on ${HOST:-0.0.0.0}:${PORT:-8006}..."

# exec replaces this shell with uvicorn so process managers (systemd, etc.)
# can signal/restart it directly instead of the wrapper script.
exec uvicorn app.main:app --host "${HOST:-0.0.0.0}" --port "${PORT:-8006}" "${RELOAD_FLAG[@]}"
