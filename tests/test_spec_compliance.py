"""Consistency between specs/parameters.yaml, specs/spec.md, and the code,
plus validation-report JSON structure.

Per project policy this uses a real YAML parser on a clearly delimited
fenced code block — never a regex scraping Markdown prose — to compare the
human-readable spec against the machine parameter source.
"""

from __future__ import annotations

from pathlib import Path

from cad_project import parameters as p
from cad_project.exports import ExportOutcome
from cad_project.model import build_model
from cad_project.rendering import RenderOutcome
from cad_project.validation import build_report, error_report


def test_parameters_yaml_loads_and_has_required_ids():
    doc = p.load_parameters_yaml()
    ids = {entry["id"] for entry in doc["parameters"]}
    assert ids >= p._REQUIRED_PARAMETER_IDS


def test_spec_md_fenced_yaml_matches_parameters_yaml_exactly():
    """The human-readable spec.md must mirror parameters.yaml — checked structurally."""
    machine_doc = p.load_parameters_yaml()
    spec_doc = p.load_spec_md_parameters()
    assert spec_doc == machine_doc


def test_module_constants_match_parameters_yaml_independently():
    """Guard against parameters.py drifting from the YAML file it loads."""
    doc = p.load_parameters_yaml()
    by_id = {entry["id"]: entry for entry in doc["parameters"]}

    assert by_id["length"]["value"] == p.LENGTH_MM
    assert by_id["width"]["value"] == p.WIDTH_MM
    assert by_id["base_thickness"]["value"] == p.BASE_THICKNESS_MM
    assert by_id["hole_count"]["value"] == p.HOLE_COUNT
    assert by_id["hole_diameter"]["value"] == p.HOLE_DIAMETER_MM
    assert by_id["hole_edge_offset"]["value"] == p.HOLE_EDGE_OFFSET_MM
    assert by_id["fillet_radius"]["value"] == p.FILLET_RADIUS_MM
    assert by_id["material_density"]["value"] == p.MATERIAL_DENSITY_KG_MM3


def test_project_metadata_matches_parameters_yaml():
    doc = p.load_parameters_yaml()
    assert doc["project"]["name"] == p.PROJECT_NAME
    assert doc["project"]["model_id"] == p.MODEL_ID
    assert doc["project"]["spec_version"] == p.SPEC_VERSION
    assert doc["project"]["units"] == p.UNITS


def test_validation_report_has_required_top_level_keys(tmp_path: Path):
    result = build_model()
    from cad_project.measurements import measure

    measurements = measure(result.part)

    step = ExportOutcome(status="passed", path=str(tmp_path / "model.step"))
    stl = ExportOutcome(status="passed", path=str(tmp_path / "model.stl"))
    preview = RenderOutcome(status="passed", path=str(tmp_path / "model.png"))

    report = build_report(result, measurements, step, stl, preview, include_rebuild_checks=False)

    for key in ("status", "spec_version", "model_id", "model", "features", "checks", "exports"):
        assert key in report

    assert report["status"] in ("passed", "failed")
    assert isinstance(report["checks"], list) and report["checks"]
    for check in report["checks"]:
        for field in ("id", "description", "expected", "actual", "tolerance", "status"):
            assert field in check

    for export_key in ("step", "stl", "preview"):
        assert export_key in report["exports"]
        assert "status" in report["exports"][export_key]
        assert "path" in report["exports"][export_key]


def test_report_status_fails_when_a_geometry_check_fails(tmp_path: Path, monkeypatch):
    from cad_project.measurements import measure

    result = build_model()
    measurements = measure(result.part)

    # Force a bounding-box mismatch against the (unchanged) spec expectation.
    monkeypatch.setattr(p, "LENGTH_MM", 999.0)

    step = ExportOutcome(status="passed", path=str(tmp_path / "model.step"))
    stl = ExportOutcome(status="passed", path=str(tmp_path / "model.stl"))
    preview = RenderOutcome(status="passed", path=str(tmp_path / "model.png"))

    report = build_report(result, measurements, step, stl, preview, include_rebuild_checks=False)
    assert report["status"] == "failed"
    failing_ids = {c["id"] for c in report["checks"] if c["status"] == "failed"}
    assert "bounding_box_length" in failing_ids


def test_report_status_unaffected_by_preview_failure(tmp_path: Path):
    """Preview rendering failures must be reported but must not gate overall status."""
    from cad_project.measurements import measure

    result = build_model()
    measurements = measure(result.part)

    step = ExportOutcome(status="passed", path=str(tmp_path / "model.step"))
    stl = ExportOutcome(status="passed", path=str(tmp_path / "model.stl"))
    preview = RenderOutcome(status="failed", path=str(tmp_path / "model.png"), error="boom")

    report = build_report(result, measurements, step, stl, preview, include_rebuild_checks=False)
    assert report["status"] == "passed"
    assert report["exports"]["preview"]["status"] == "failed"
    assert "warnings" in report


def test_error_report_has_valid_structure_for_a_crash():
    report = error_report(RuntimeError("boom"), stage="all")
    assert report["status"] == "failed"
    assert report["checks"][0]["id"] == "no_unhandled_exceptions"
    assert "boom" in report["checks"][0]["actual"]
