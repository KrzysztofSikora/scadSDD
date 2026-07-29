#!/usr/bin/env bash
# Create (if needed) and populate the local .venv with runtime + dev dependencies.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_DIR="$REPO_ROOT/.venv"

cd "$REPO_ROOT"

if [ ! -d "$VENV_DIR" ]; then
  echo "==> Creating virtual environment at $VENV_DIR"
  python3 -m venv "$VENV_DIR"
else
  echo "==> Reusing existing virtual environment at $VENV_DIR"
fi

PIP="$VENV_DIR/bin/pip"

echo "==> Upgrading pip"
"$PIP" install --upgrade pip

echo "==> Installing project (editable) with dev extras"
"$PIP" install -e ".[dev]"

echo "==> Setup complete. Activate with: source .venv/bin/activate"
