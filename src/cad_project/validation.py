"""Explicit, rule-based validation of the built model against the spec.

Every check is a self-contained rule that produces an identifier, a human
description, the expected value, the actual value, the tolerance applied,
a pass/fail status, and an error message when it fails. Nothing here
adjusts a tolerance or an expected value to make a check pass — those come
from ``specs/parameters.yaml`` only.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any

from cad_project import parameters as p
from cad_project.exports import ExportOutcome
from cad_project.measurements import Measurements, count_cylindrical_faces_near_radius
from cad_project.model import ModelFeatures, ModelResult, build_model
from cad_project.rendering import RenderOutcome

PASSED = "passed"
FAILED = "failed"

REPORT_PATH = p.REPO_ROOT / "output" / "reports" / "validation-report.json"


@dataclass(frozen=True)
class ValidationCheck:
    id: str
    description: str
    expected: Any
    actual: Any
    tolerance: Any
    status: str
    message: str = ""

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _dimension_check(
    check_id: str, description: str, expected: float, actual: float, tolerance: float
) -> ValidationCheck:
    ok = abs(actual - expected) <= tolerance
    return ValidationCheck(
        id=check_id,
        description=description,
        expected=expected,
        actual=actual,
        tolerance=tolerance,
        status=PASSED if ok else FAILED,
        message="" if ok else f"Expected {expected} +/- {tolerance}, got {actual}.",
    )


def run_geometry_checks(measurements: Measurements, features: ModelFeatures) -> list[ValidationCheck]:
    """Checks that depend only on the measured solid and its declared features."""
    checks: list[ValidationCheck] = []

    checks.append(
        ValidationCheck(
            id="solid_count",
            description="Model composed of exactly one solid.",
            expected=1,
            actual=measurements.solid_count,
            tolerance=0,
            status=PASSED if measurements.solid_count == 1 else FAILED,
            message=""
            if measurements.solid_count == 1
            else f"Expected exactly 1 solid, found {measurements.solid_count}.",
        )
    )

    checks.append(
        ValidationCheck(
            id="geometry_valid",
            description="Solid passes OCCT validity check (no empty/negative geometry).",
            expected=True,
            actual=measurements.is_valid,
            tolerance=None,
            status=PASSED if measurements.is_valid else FAILED,
            message="" if measurements.is_valid else "Solid failed OCCT BRepCheck validity test.",
        )
    )

    checks.append(
        _dimension_check(
            "bounding_box_length",
            "Bounding box X (length) matches specification.",
            p.LENGTH_MM,
            measurements.bounding_box_mm.x_mm,
            p.tolerance_for("length"),
        )
    )
    checks.append(
        _dimension_check(
            "bounding_box_width",
            "Bounding box Y (width) matches specification.",
            p.WIDTH_MM,
            measurements.bounding_box_mm.y_mm,
            p.tolerance_for("width"),
        )
    )
    checks.append(
        _dimension_check(
            "bounding_box_thickness",
            "Bounding box Z (thickness) matches specification.",
            p.BASE_THICKNESS_MM,
            measurements.bounding_box_mm.z_mm,
            p.tolerance_for("base_thickness"),
        )
    )

    checks.append(
        ValidationCheck(
            id="volume_positive",
            description="Solid has strictly positive volume.",
            expected="> 0",
            actual=measurements.volume_mm3,
            tolerance=None,
            status=PASSED if measurements.volume_mm3 > 0 else FAILED,
            message="" if measurements.volume_mm3 > 0 else "Volume is zero or negative.",
        )
    )

    checks.append(
        ValidationCheck(
            id="hole_count",
            description="Number of mounting holes matches specification (from build features).",
            expected=p.HOLE_COUNT,
            actual=features.hole_count,
            tolerance=0,
            status=PASSED if features.hole_count == p.HOLE_COUNT else FAILED,
            message=""
            if features.hole_count == p.HOLE_COUNT
            else f"Expected {p.HOLE_COUNT} holes, build produced {features.hole_count}.",
        )
    )

    checks.append(
        _dimension_check(
            "hole_diameter",
            "Mounting hole diameter matches specification (from build features).",
            p.HOLE_DIAMETER_MM,
            features.hole_diameter_mm,
            p.tolerance_for("hole_diameter"),
        )
    )

    return checks


def topology_cross_check(model_result: ModelResult) -> dict[str, Any]:
    """Best-effort, explicitly informational topological cross-check.

    See ``specs/constraints.md``: this is not used to gate pass/fail status
    because cylindrical-face counting cannot reliably distinguish "hole"
    from "some other cylindrical feature" in general.
    """
    radius = p.HOLE_DIAMETER_MM / 2
    observed = count_cylindrical_faces_near_radius(model_result.part, radius)
    matches_features = observed == model_result.features.hole_count
    return {
        "note": (
            "Best-effort topological cross-check, informational only — not "
            "authoritative. See specs/constraints.md."
        ),
        "cylindrical_faces_near_hole_radius": observed,
        "matches_declared_hole_count": matches_features,
    }


def rebuild_check() -> tuple[ValidationCheck, ModelResult | None]:
    """Rebuild the model from scratch and verify it succeeds and is deterministic.

    This satisfies two Definition-of-Done requirements at once: "możliwość
    ponownego zbudowania modelu" and "brak nieobsłużonych wyjątków" for the
    rebuild path. Any exception here is caught and turned into a failed
    check rather than propagating.
    """
    try:
        second = build_model()
    except Exception as exc:  # noqa: BLE001 - deliberately captured for the report
        return (
            ValidationCheck(
                id="rebuild_succeeds",
                description="Model can be rebuilt from the same parameters without error.",
                expected="no exception",
                actual=f"{type(exc).__name__}: {exc}",
                tolerance=None,
                status=FAILED,
                message="Rebuilding the model raised an unhandled exception.",
            ),
            None,
        )
    return (
        ValidationCheck(
            id="rebuild_succeeds",
            description="Model can be rebuilt from the same parameters without error.",
            expected="no exception",
            actual="no exception",
            tolerance=None,
            status=PASSED,
        ),
        second,
    )


def determinism_check(first: ModelResult, second: ModelResult) -> ValidationCheck:
    from cad_project.measurements import measure

    m1 = measure(first.part)
    m2 = measure(second.part)
    same = (
        m1.solid_count == m2.solid_count
        and abs(m1.volume_mm3 - m2.volume_mm3) < 1e-6
        and abs(m1.surface_area_mm2 - m2.surface_area_mm2) < 1e-6
        and m1.bounding_box_mm == m2.bounding_box_mm
        and first.features == second.features
    )
    return ValidationCheck(
        id="rebuild_deterministic",
        description="Two independent builds produce identical measurements and features.",
        expected="identical",
        actual="identical" if same else "differs",
        tolerance=None,
        status=PASSED if same else FAILED,
        message="" if same else "Rebuilt model differs from the first build.",
    )


def _exports_section(
    step: ExportOutcome, stl: ExportOutcome, preview: RenderOutcome
) -> dict[str, Any]:
    def entry(outcome: ExportOutcome | RenderOutcome) -> dict[str, Any]:
        d = {"status": outcome.status, "path": outcome.path}
        if outcome.error:
            d["error"] = outcome.error
        return d

    return {"step": entry(step), "stl": entry(stl), "preview": entry(preview)}


def build_report(
    model_result: ModelResult,
    measurements: Measurements,
    step_outcome: ExportOutcome,
    stl_outcome: ExportOutcome,
    preview_outcome: RenderOutcome,
    *,
    include_rebuild_checks: bool = True,
) -> dict[str, Any]:
    """Assemble the full validation report as a JSON-serializable dict."""
    checks = run_geometry_checks(measurements, model_result.features)

    if include_rebuild_checks:
        rebuild_result, second_build = rebuild_check()
        checks.append(rebuild_result)
        if second_build is not None:
            checks.append(determinism_check(model_result, second_build))

    checks.append(
        ValidationCheck(
            id="export_step_exists",
            description="STEP export succeeded and produced a non-empty file.",
            expected=PASSED,
            actual=step_outcome.status,
            tolerance=None,
            status=step_outcome.status,
            message=step_outcome.error or "",
        )
    )
    checks.append(
        ValidationCheck(
            id="export_stl_exists",
            description="STL export succeeded and produced a non-empty file.",
            expected=PASSED,
            actual=stl_outcome.status,
            tolerance=None,
            status=stl_outcome.status,
            message=stl_outcome.error or "",
        )
    )

    # Preview/render status is reported but intentionally does not gate the
    # overall pass/fail status — see specs/constraints.md and
    # src/cad_project/rendering.py.
    gating_checks = checks
    overall_status = PASSED if all(c.status == PASSED for c in gating_checks) else FAILED

    report: dict[str, Any] = {
        "status": overall_status,
        "spec_version": p.SPEC_VERSION,
        "model_id": p.MODEL_ID,
        "generated_at": datetime.now(UTC).isoformat(),
        "model": {
            "solid_count": measurements.solid_count,
            "is_valid": measurements.is_valid,
            "volume_mm3": measurements.volume_mm3,
            "surface_area_mm2": measurements.surface_area_mm2,
            "bounding_box_mm": {
                "x": measurements.bounding_box_mm.x_mm,
                "y": measurements.bounding_box_mm.y_mm,
                "z": measurements.bounding_box_mm.z_mm,
            },
            "mass_kg": measurements.mass_kg,
        },
        "features": {
            "hole_count": model_result.features.hole_count,
            "hole_diameter_mm": model_result.features.hole_diameter_mm,
            "hole_positions_mm": [list(pos) for pos in model_result.features.hole_positions_mm],
        },
        "topology_cross_check": topology_cross_check(model_result),
        "checks": [c.as_dict() for c in checks],
        "exports": _exports_section(step_outcome, stl_outcome, preview_outcome),
    }
    if preview_outcome.status != PASSED:
        report["warnings"] = [
            f"Preview rendering failed and is reported independently: "
            f"{preview_outcome.error}"
        ]
    return report


def error_report(exc: Exception, stage: str) -> dict[str, Any]:
    """Build a minimal failed report when an unhandled exception stops the pipeline early.

    Used by the CLI so that a crash still produces a valid, inspectable JSON
    report instead of nothing at all.
    """
    return {
        "status": FAILED,
        "spec_version": p.SPEC_VERSION,
        "model_id": p.MODEL_ID,
        "generated_at": datetime.now(UTC).isoformat(),
        "model": None,
        "features": None,
        "topology_cross_check": None,
        "checks": [
            ValidationCheck(
                id="no_unhandled_exceptions",
                description=f"Pipeline stage '{stage}' completes without raising.",
                expected="no exception",
                actual=f"{type(exc).__name__}: {exc}",
                tolerance=None,
                status=FAILED,
                message=f"Unhandled exception during '{stage}': {exc}",
            ).as_dict()
        ],
        "exports": {
            "step": {"status": "skipped", "path": ""},
            "stl": {"status": "skipped", "path": ""},
            "preview": {"status": "skipped", "path": ""},
        },
    }
