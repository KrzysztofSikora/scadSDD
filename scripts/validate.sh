#!/usr/bin/env bash
# Run validation against previously generated exports and print the report status.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_DIR="$REPO_ROOT/.venv"

if [ ! -x "$VENV_DIR/bin/python" ]; then
  echo "ERROR: virtual environment not found at $VENV_DIR. Run scripts/setup.sh first." >&2
  exit 1
fi

cd "$REPO_ROOT"
echo "==> Running validation (python -m cad_project.cli validate)"
STATUS=0
"$VENV_DIR/bin/python" -m cad_project.cli validate || STATUS=$?

REPORT="$REPO_ROOT/output/reports/validation-report.json"
if [ -f "$REPORT" ]; then
  echo "==> Report written to $REPORT"
fi

exit "$STATUS"
