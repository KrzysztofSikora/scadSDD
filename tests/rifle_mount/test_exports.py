"""Export (STEP/STL) and preview rendering tests for both parts.

Uses the shared session-scoped ``built_result`` fixture (conftest.py) so
these tests don't trigger extra full model builds; writes only into
tmp_path, never into the tracked output/ tree.
"""

from __future__ import annotations

from pathlib import Path

from cad_project.exports import existing_export_outcome, export_step_file, export_stl_file
from cad_project.rendering import existing_preview_outcome, render_preview_png


def test_export_step_both_parts(built_result, tmp_path: Path):
    base_path = tmp_path / "base.step"
    arm_path = tmp_path / "arm.step"
    base_outcome = export_step_file(built_result.base.part, base_path)
    arm_outcome = export_step_file(built_result.arm.part, arm_path)
    assert base_outcome.status == "passed"
    assert arm_outcome.status == "passed"
    assert base_path.stat().st_size > 0
    assert arm_path.stat().st_size > 0


def test_export_stl_both_parts(built_result, tmp_path: Path):
    base_path = tmp_path / "base.stl"
    arm_path = tmp_path / "arm.stl"
    base_outcome = export_stl_file(built_result.base.part, base_path)
    arm_outcome = export_stl_file(built_result.arm.part, arm_path)
    assert base_outcome.status == "passed"
    assert arm_outcome.status == "passed"
    assert base_path.stat().st_size > 0
    assert arm_path.stat().st_size > 0


def test_step_export_is_deterministic_per_part(built_result, tmp_path: Path):
    first = tmp_path / "first.step"
    second = tmp_path / "second.step"
    export_step_file(built_result.base.part, first)
    export_step_file(built_result.base.part, second)
    assert first.read_bytes() == second.read_bytes()


def test_render_preview_both_parts(built_result, tmp_path: Path):
    base_png = tmp_path / "base.png"
    arm_png = tmp_path / "arm.png"
    base_outcome = render_preview_png(built_result.base.part, base_png)
    arm_outcome = render_preview_png(built_result.arm.part, arm_png)
    assert base_outcome.status == "passed"
    assert arm_outcome.status == "passed"
    assert base_png.stat().st_size > 0
    assert arm_png.stat().st_size > 0


def test_existing_export_outcome_reports_missing_file(tmp_path: Path):
    outcome = existing_export_outcome(tmp_path / "missing.step", "base STEP")
    assert outcome.status == "failed"
    assert "not found" in outcome.error


def test_existing_preview_outcome_reports_missing_file(tmp_path: Path):
    outcome = existing_preview_outcome(tmp_path / "missing.png")
    assert outcome.status == "failed"
