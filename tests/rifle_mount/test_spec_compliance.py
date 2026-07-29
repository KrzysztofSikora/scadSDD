"""Consistency between specs/rifle-mount/parameters.yaml, spec.md, and the code,
plus validation-report JSON structure.
"""

from __future__ import annotations

from pathlib import Path

from cad_project.exports import ExportOutcome
from cad_project.rendering import RenderOutcome
from cad_project.rifle_mount import parameters as p
from cad_project.rifle_mount.validation import build_report, error_report


def test_parameters_yaml_loads_and_has_required_ids():
    doc = p.load_parameters_yaml()
    ids = {entry["id"] for entry in doc["parameters"]}
    assert ids >= p._REQUIRED_PARAMETER_IDS


def test_spec_md_fenced_yaml_matches_parameters_yaml_exactly():
    machine_doc = p.load_parameters_yaml()
    spec_doc = p.load_spec_md_parameters()
    assert spec_doc == machine_doc


def test_project_metadata_matches_parameters_yaml():
    doc = p.load_parameters_yaml()
    assert doc["project"]["name"] == p.PROJECT_NAME
    assert doc["project"]["model_id"] == p.MODEL_ID
    assert doc["project"]["spec_version"] == p.SPEC_VERSION
    assert doc["project"]["units"] == p.UNITS


def test_module_constants_match_parameters_yaml_independently():
    doc = p.load_parameters_yaml()
    by_id = {entry["id"]: entry for entry in doc["parameters"]}
    assert by_id["thread_pitch"]["value"] == p.THREAD_PITCH_MM
    assert by_id["thread_major_diameter"]["value"] == p.THREAD_MAJOR_DIAMETER_MM
    assert by_id["rod_threaded_length"]["value"] == p.ROD_THREADED_LENGTH_MM
    assert by_id["u_arm_height"]["value"] == p.U_ARM_HEIGHT_MM
    assert by_id["mounting_plate_size"]["value"] == p.MOUNTING_PLATE_SIZE_MM


def test_validation_report_has_required_structure(built_result, tmp_path: Path):
    from cad_project.measurements import measure

    base_m = measure(built_result.base.part)
    arm_m = measure(built_result.arm.part)

    passed = ExportOutcome(status="passed", path=str(tmp_path / "x"))
    preview = RenderOutcome(status="passed", path=str(tmp_path / "x.png"))

    report = build_report(
        built_result, base_m, arm_m,
        (passed, passed, preview), (passed, passed, preview),
        include_rebuild_checks=False,
    )

    for key in ("status", "spec_version", "model_id", "parts", "checks", "exports"):
        assert key in report
    assert "base" in report["parts"] and "arm" in report["parts"]
    assert "base" in report["exports"] and "arm" in report["exports"]
    assert report["status"] in ("passed", "failed")
    for check in report["checks"]:
        for field in ("id", "description", "expected", "actual", "tolerance", "status"):
            assert field in check


def test_error_report_has_valid_structure_for_a_crash():
    report = error_report(RuntimeError("boom"), stage="all")
    assert report["status"] == "failed"
    assert report["checks"][0]["id"] == "no_unhandled_exceptions"
    assert "boom" in report["checks"][0]["actual"]
