#!/bin/bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR/app"

if [ ! -d "$PROJECT_DIR/venv" ]; then
  echo "Virtual environment not found. Run ./scripts/initialize.sh first."
  exit 1
fi

source "$PROJECT_DIR/venv/bin/activate"
exec uvicorn main_new:app --host 0.0.0.0 --port 8000
