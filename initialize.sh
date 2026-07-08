#!/bin/bash
# Installs project dependencies only:
#   - backend: creates backend/venv (if missing) and pip-installs requirements.txt
#   - frontend: npm-installs package.json
#
# Does not touch any .env/config files, does not build the frontend, and
# does not start any services. See start_backend.sh / start_frontend.sh for that.
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "==> Backend: virtual environment + Python dependencies"
cd "$PROJECT_DIR/backend"

if [ ! -d venv ]; then
  python3 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate

echo "==> Frontend: npm dependencies"
cd "$PROJECT_DIR/frontend"
npm install

echo
echo "Dependencies installed."
