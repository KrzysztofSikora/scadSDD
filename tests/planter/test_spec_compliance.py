"""Consistency between specs/planter/parameters.yaml, spec.md, and the code,
plus validation-report JSON structure.
"""

from __future__ import annotations

from pathlib import Path

from cad_project.exports import ExportOutcome
from cad_project.planter import parameters as p
from cad_project.planter.validation import build_report, error_report
from cad_project.rendering import RenderOutcome


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
    assert by_id["insert_top_outer_diameter"]["value"] == p.INSERT_TOP_OUTER_DIAMETER_MM
    assert by_id["reservoir_mouth_inner_diameter"]["value"] == p.RESERVOIR_MOUTH_INNER_DIAMETER_MM
    assert by_id["pattern_flute_count"]["value"] == p.PATTERN_FLUTE_COUNT
    assert by_id["capillary_tube_outer_diameter"]["value"] == p.CAPILLARY_TUBE_OUTER_DIAMETER_MM


def test_validation_report_has_required_structure(built_result, tmp_path: Path):
    from cad_project.measurements import measure

    insert_m = measure(built_result.insert.part)
    reservoir_m = measure(built_result.reservoir.part)

    passed = ExportOutcome(status="passed", path=str(tmp_path / "x"))
    preview = RenderOutcome(status="passed", path=str(tmp_path / "x.png"))

    report = build_report(
        built_result, insert_m, reservoir_m,
        (passed, passed, preview), (passed, passed, preview),
        include_rebuild_checks=False,
    )

    for key in ("status", "spec_version", "model_id", "parts", "checks", "exports"):
        assert key in report
    assert "insert" in report["parts"] and "reservoir" in report["parts"]
    assert "insert" in report["exports"] and "reservoir" in report["exports"]
    assert report["status"] in ("passed", "failed")
    for check in report["checks"]:
        for field in ("id", "description", "expected", "actual", "tolerance", "status"):
            assert field in check


def test_error_report_has_valid_structure_for_a_crash():
    report = error_report(RuntimeError("boom"), stage="all")
    assert report["status"] == "failed"
    assert report["checks"][0]["id"] == "no_unhandled_exceptions"
    assert "boom" in report["checks"][0]["actual"]
