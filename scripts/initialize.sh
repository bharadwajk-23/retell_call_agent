#!/bin/bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$PROJECT_DIR"

if [ ! -d "$PROJECT_DIR/venv" ]; then
  python3 -m venv venv
fi

source "$PROJECT_DIR/venv/bin/activate"
pip install -r requirements.txt

cd "$PROJECT_DIR/frontend"
npm install
npm run build

echo "Initialization complete."
echo "Use ./scripts/start-service.sh to start the app."
