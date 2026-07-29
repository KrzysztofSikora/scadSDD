"""Export (STEP/STL) and preview rendering tests.

These write to a temporary directory (never into output/) so the test
suite never depends on, or clobbers, real pipeline output.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from cad_project.exports import existing_export_outcome, export_step_file, export_stl_file
from cad_project.model import build_model
from cad_project.rendering import existing_preview_outcome, render_preview_png


@pytest.fixture(scope="module")
def built_part():
    return build_model().part


def test_export_step_creates_nonempty_file(built_part, tmp_path: Path):
    target = tmp_path / "model.step"
    outcome = export_step_file(built_part, target)
    assert outcome.status == "passed"
    assert target.exists()
    assert target.stat().st_size > 0


def test_export_stl_creates_nonempty_file(built_part, tmp_path: Path):
    target = tmp_path / "model.stl"
    outcome = export_stl_file(built_part, target)
    assert outcome.status == "passed"
    assert target.exists()
    assert target.stat().st_size > 0


def test_step_export_is_deterministic(built_part, tmp_path: Path):
    """Repeated STEP exports of the same solid must be byte-identical (fixed timestamp)."""
    first = tmp_path / "first.step"
    second = tmp_path / "second.step"
    export_step_file(built_part, first)
    export_step_file(built_part, second)
    assert first.read_bytes() == second.read_bytes()


def test_existing_export_outcome_reports_missing_file(tmp_path: Path):
    missing = tmp_path / "does-not-exist.step"
    outcome = existing_export_outcome(missing, "STEP")
    assert outcome.status == "failed"
    assert "not found" in outcome.error


def test_existing_export_outcome_reports_present_file(tmp_path: Path):
    present = tmp_path / "present.step"
    present.write_text("dummy")
    outcome = existing_export_outcome(present, "STEP")
    assert outcome.status == "passed"


def test_render_preview_creates_nonempty_png(built_part, tmp_path: Path):
    target = tmp_path / "model.png"
    outcome = render_preview_png(built_part, target)
    assert outcome.status == "passed"
    assert target.exists()
    assert target.stat().st_size > 0


def test_render_preview_failure_is_reported_not_raised(built_part, tmp_path: Path, monkeypatch):
    """Rendering errors must be captured into a failed RenderOutcome, never raised."""

    def _boom(*_args, **_kwargs):
        raise RuntimeError("simulated renderer failure")

    monkeypatch.setattr("cad_project.rendering._render", _boom)
    outcome = render_preview_png(built_part, tmp_path / "model.png")
    assert outcome.status == "failed"
    assert "simulated renderer failure" in outcome.error


def test_existing_preview_outcome_reports_missing_file(tmp_path: Path):
    outcome = existing_preview_outcome(tmp_path / "missing.png")
    assert outcome.status == "failed"
