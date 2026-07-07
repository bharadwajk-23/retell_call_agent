#!/bin/bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR/frontend"

if [ ! -d "$PROJECT_DIR/venv" ]; then
  echo "Virtual environment not found at $PROJECT_DIR/venv"
  exit 1
fi

npm install
npm run build
