#!/usr/bin/env bash
# Open generated STEP model(s) in FreeCAD (optional external viewer).
#
# Usage: scripts/view.sh [step-file ...]
#   No args -> opens the mounting bracket's output/step/model.step.
#
# FreeCAD is NOT a pipeline dependency: build/export/validate/render all work
# without it. This script only launches an interactive viewer for a human to
# inspect the given STEP file(s).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

if [ "$#" -gt 0 ]; then
  STEP_FILES=("$@")
else
  STEP_FILES=("$REPO_ROOT/output/step/model.step")
fi

for f in "${STEP_FILES[@]}"; do
  if [ ! -f "$f" ]; then
    echo "ERROR: $f not found. Run 'make all' (or the relevant 'export' command) first." >&2
    exit 1
  fi
done

FLATPAK_APP_ID="org.freecad.FreeCAD"

# 1. Native binary on PATH.
for candidate in freecad freecad-cli FreeCAD; do
  if command -v "$candidate" >/dev/null 2>&1; then
    echo "==> Opening ${STEP_FILES[*]} in FreeCAD ($candidate)..."
    exec "$candidate" "${STEP_FILES[@]}"
  fi
done

# 2. Flatpak install (user or system scope).
if command -v flatpak >/dev/null 2>&1 && flatpak list --columns=application 2>/dev/null | grep -qx "$FLATPAK_APP_ID"; then
  echo "==> Opening ${STEP_FILES[*]} in FreeCAD (flatpak: $FLATPAK_APP_ID)..."
  exec flatpak run "$FLATPAK_APP_ID" "${STEP_FILES[@]}"
fi

cat >&2 <<EOF
ERROR: FreeCAD is not installed (checked PATH and flatpak).

Install it with one of:
  sudo apt update && sudo apt install freecad          # Debian/Ubuntu/Mint
  flatpak install --user -y flathub $FLATPAK_APP_ID    # Flatpak, no sudo needed
  # or download the AppImage from https://www.freecad.org/downloads.php
    (no root needed, then run it directly instead of this script)

FreeCAD is an optional viewer only; it is not required to build, export,
validate, or render this project.
EOF
exit 1
