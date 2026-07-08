#!/bin/bash
# Starts the FastAPI backend using backend/venv and the project's single
# root .env (see backend/app/config/settings.py).
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

cd "$PROJECT_DIR/backend"
source venv/bin/activate

PORT="$(grep -E '^PORT=' "$PROJECT_DIR/.env" | tail -1 | cut -d'=' -f2 | tr -d ' \r')"
echo "Starting backend on port ${PORT:-8006}..."

# exec replaces this shell with uvicorn so process managers (systemd, etc.)
# can signal/restart it directly instead of the wrapper script.
exec python3 -m app.main
