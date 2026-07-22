#!/bin/bash
# Starts the FastAPI backend directly with uvicorn, using backend/venv and
# the project's single root .env for HOST/PORT. Local dev only — always runs
# with --reload.
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

# Stay at the project root (not backend/) so `backend.app.main:app` resolves
# as a package import; only the venv itself is backend-specific.
cd "$PROJECT_DIR"
source backend/venv/bin/activate

echo "Starting backend on ${HOST:-0.0.0.0}:${PORT:-8006}..."

# exec replaces this shell with uvicorn so process managers (systemd, etc.)
# can signal/restart it directly instead of the wrapper script.
exec uvicorn backend.app.main:app --host "${HOST:-0.0.0.0}" --port "${PORT:-8006}" --reload
