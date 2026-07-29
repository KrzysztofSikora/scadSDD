#!/usr/bin/env bash
# Run the full spec-driven CAD pipeline (build, measure, validate, export, render, report).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_DIR="$REPO_ROOT/.venv"

if [ ! -x "$VENV_DIR/bin/python" ]; then
  echo "ERROR: virtual environment not found at $VENV_DIR. Run scripts/setup.sh first." >&2
  exit 1
fi

cd "$REPO_ROOT"
echo "==> Running full pipeline (python -m cad_project.cli all)"
"$VENV_DIR/bin/python" -m cad_project.cli all
