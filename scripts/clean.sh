#!/usr/bin/env bash
# Remove generated files under output/ (keeps .gitkeep markers) and Python caches.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_DIR="$REPO_ROOT/.venv"

cd "$REPO_ROOT"

if [ -x "$VENV_DIR/bin/python" ]; then
  "$VENV_DIR/bin/python" -m cad_project.cli clean
else
  echo "==> No venv found, removing output files directly"
  find output -type f ! -name ".gitkeep" -delete
fi

echo "==> Removing Python caches"
find . -type d \( -name "__pycache__" -o -name ".pytest_cache" -o -name ".ruff_cache" \) \
  -not -path "./.venv/*" -exec rm -rf {} + 2>/dev/null || true

echo "==> Clean complete."
