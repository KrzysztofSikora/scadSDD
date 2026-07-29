"""File export for STEP and STL. Never called at import time.

Exporting is always explicit — triggered by the CLI or a script — so that
importing ``cad_project`` (e.g. in tests) never touches the filesystem.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from build123d import Part, export_step, export_stl

from cad_project.parameters import REPO_ROOT

# Fixed timestamp so repeated STEP exports of the same geometry are
# byte-identical; see specs/decisions.md ("Determinizm eksportu STEP").
_FIXED_STEP_TIMESTAMP = datetime(2000, 1, 1)

STEP_PATH: Path = REPO_ROOT / "output" / "step" / "model.step"
STL_PATH: Path = REPO_ROOT / "output" / "stl" / "model.stl"


@dataclass(frozen=True)
class ExportOutcome:
    """Result of a single export attempt, ready to embed in a report."""

    status: str  # "passed" | "failed"
    path: str
    error: str | None = None


def _run_export(path: Path, export_fn) -> ExportOutcome:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        export_fn(path)
    except Exception as exc:  # noqa: BLE001 - deliberately captured for the report
        return ExportOutcome(status="failed", path=str(path), error=str(exc))
    if not path.exists() or path.stat().st_size == 0:
        return ExportOutcome(
            status="failed",
            path=str(path),
            error="Export function returned without raising, but the output "
            "file is missing or empty.",
        )
    return ExportOutcome(status="passed", path=str(path))


def export_step_file(part: Part, path: Path = STEP_PATH) -> ExportOutcome:
    """Export ``part`` to STEP at ``path``."""
    return _run_export(
        path,
        lambda p: export_step(part, p, timestamp=_FIXED_STEP_TIMESTAMP),
    )


def export_stl_file(part: Part, path: Path = STL_PATH) -> ExportOutcome:
    """Export ``part`` to STL (binary) at ``path``."""
    return _run_export(path, lambda p: export_stl(part, p))


def existing_export_outcome(path: Path, label: str) -> ExportOutcome:
    """Check whether a previously exported file exists, without exporting.

    Used by ``cad_project.cli validate`` (which reports on artifacts without
    regenerating them) as opposed to ``export``/``all`` (which perform a
    fresh export).
    """
    if path.exists() and path.stat().st_size > 0:
        return ExportOutcome(status="passed", path=str(path))
    return ExportOutcome(
        status="failed",
        path=str(path),
        error=f"{label} file not found at {path}. Run `export` or `all` first.",
    )
