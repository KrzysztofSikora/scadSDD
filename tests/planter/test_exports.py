"""Export (STEP/STL) and preview rendering tests for both parts.

Uses the shared session-scoped ``built_result`` fixture (conftest.py);
writes only into tmp_path, never into the tracked output/ tree.
"""

from __future__ import annotations

from pathlib import Path

from cad_project.exports import existing_export_outcome, export_step_file, export_stl_file
from cad_project.rendering import existing_preview_outcome, render_preview_png


def test_export_step_both_parts(built_result, tmp_path: Path):
    insert_path = tmp_path / "insert.step"
    reservoir_path = tmp_path / "reservoir.step"
    insert_outcome = export_step_file(built_result.insert.part, insert_path)
    reservoir_outcome = export_step_file(built_result.reservoir.part, reservoir_path)
    assert insert_outcome.status == "passed"
    assert reservoir_outcome.status == "passed"
    assert insert_path.stat().st_size > 0
    assert reservoir_path.stat().st_size > 0


def test_export_stl_both_parts(built_result, tmp_path: Path):
    insert_path = tmp_path / "insert.stl"
    reservoir_path = tmp_path / "reservoir.stl"
    insert_outcome = export_stl_file(built_result.insert.part, insert_path)
    reservoir_outcome = export_stl_file(built_result.reservoir.part, reservoir_path)
    assert insert_outcome.status == "passed"
    assert reservoir_outcome.status == "passed"
    assert insert_path.stat().st_size > 0
    assert reservoir_path.stat().st_size > 0


def test_step_export_is_deterministic_per_part(built_result, tmp_path: Path):
    first = tmp_path / "first.step"
    second = tmp_path / "second.step"
    export_step_file(built_result.insert.part, first)
    export_step_file(built_result.insert.part, second)
    assert first.read_bytes() == second.read_bytes()


def test_render_preview_both_parts(built_result, tmp_path: Path):
    insert_png = tmp_path / "insert.png"
    reservoir_png = tmp_path / "reservoir.png"
    insert_outcome = render_preview_png(built_result.insert.part, insert_png)
    reservoir_outcome = render_preview_png(built_result.reservoir.part, reservoir_png)
    assert insert_outcome.status == "passed"
    assert reservoir_outcome.status == "passed"
    assert insert_png.stat().st_size > 0
    assert reservoir_png.stat().st_size > 0


def test_existing_export_outcome_reports_missing_file(tmp_path: Path):
    outcome = existing_export_outcome(tmp_path / "missing.step", "insert STEP")
    assert outcome.status == "failed"
    assert "not found" in outcome.error


def test_existing_preview_outcome_reports_missing_file(tmp_path: Path):
    outcome = existing_preview_outcome(tmp_path / "missing.png")
    assert outcome.status == "failed"
