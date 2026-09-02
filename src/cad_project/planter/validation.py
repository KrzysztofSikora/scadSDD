"""Explicit, rule-based validation for the two-part self-watering planter.

Mirrors ``cad_project.rifle_mount.validation`` in spirit — every check is
self-contained (id, description, expected, actual, tolerance, status,
message) — but the report covers **two independent parts** (insert +
reservoir), since this model does not produce a single solid (see
specs/planter/constraints.md).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any

from cad_project.exports import ExportOutcome
from cad_project.measurements import Measurements
from cad_project.planter import parameters as p
from cad_project.planter.model import (
    InsertFeatures,
    PlanterResult,
    ReservoirFeatures,
    build_model,
)
from cad_project.rendering import RenderOutcome

PASSED = "passed"
FAILED = "failed"

REPORT_PATH = p.REPO_ROOT / "output" / "planter" / "reports" / "validation-report.json"


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


def _solid_checks(prefix: str, measurements: Measurements) -> list[ValidationCheck]:
    return [
        ValidationCheck(
            id=f"{prefix}_solid_count",
            description=f"Część '{prefix}' składa się z dokładnie jednej bryły.",
            expected=1,
            actual=measurements.solid_count,
            tolerance=0,
            status=PASSED if measurements.solid_count == 1 else FAILED,
            message=""
            if measurements.solid_count == 1
            else f"Expected exactly 1 solid for '{prefix}', found {measurements.solid_count}.",
        ),
        ValidationCheck(
            id=f"{prefix}_geometry_valid",
            description=f"Bryła '{prefix}' przechodzi test poprawności OCCT.",
            expected=True,
            actual=measurements.is_valid,
            tolerance=None,
            status=PASSED if measurements.is_valid else FAILED,
            message="" if measurements.is_valid else f"'{prefix}' failed OCCT validity test.",
        ),
        ValidationCheck(
            id=f"{prefix}_volume_positive",
            description=f"Bryła '{prefix}' ma dodatnią objętość.",
            expected="> 0",
            actual=measurements.volume_mm3,
            tolerance=None,
            status=PASSED if measurements.volume_mm3 > 0 else FAILED,
            message="" if measurements.volume_mm3 > 0 else f"'{prefix}' volume is zero or negative.",
        ),
    ]


def _insert_feature_checks(features: InsertFeatures) -> list[ValidationCheck]:
    return [
        _dimension_check(
            "insert_top_outer_diameter",
            "Średnica górna wkładu zgodna ze specyfikacją.",
            p.INSERT_TOP_OUTER_DIAMETER_MM,
            features.top_outer_diameter_mm,
            p.tolerance_for("insert_top_outer_diameter"),
        ),
        _dimension_check(
            "insert_bottom_outer_diameter",
            "Średnica dolna wkładu zgodna ze specyfikacją.",
            p.INSERT_BOTTOM_OUTER_DIAMETER_MM,
            features.bottom_outer_diameter_mm,
            p.tolerance_for("insert_bottom_outer_diameter"),
        ),
        _dimension_check(
            "insert_body_height",
            "Wysokość wkładu zgodna ze specyfikacją.",
            p.INSERT_BODY_HEIGHT_MM,
            features.body_height_mm,
            p.tolerance_for("insert_body_height"),
        ),
        ValidationCheck(
            id="drainage_hole_count",
            description="Liczba otworów drenażowych zgodna ze specyfikacją.",
            expected=p.DRAINAGE_HOLE_COUNT,
            actual=features.drainage_hole_count,
            tolerance=0,
            status=PASSED if features.drainage_hole_count == p.DRAINAGE_HOLE_COUNT else FAILED,
            message=""
            if features.drainage_hole_count == p.DRAINAGE_HOLE_COUNT
            else f"Expected {p.DRAINAGE_HOLE_COUNT} drainage holes, got {features.drainage_hole_count}.",
        ),
        ValidationCheck(
            id="pattern_flute_count",
            description="Liczba żłobień wzoru ścianki zgodna ze specyfikacją.",
            expected=p.PATTERN_FLUTE_COUNT,
            actual=features.pattern_flute_count,
            tolerance=0,
            status=PASSED if features.pattern_flute_count == p.PATTERN_FLUTE_COUNT else FAILED,
            message=""
            if features.pattern_flute_count == p.PATTERN_FLUTE_COUNT
            else f"Expected {p.PATTERN_FLUTE_COUNT} flutes, got {features.pattern_flute_count}.",
        ),
        _dimension_check(
            "capillary_tube_outer_diameter",
            "Średnica zewnętrzna rdzenia kapilarnego zgodna ze specyfikacją.",
            p.CAPILLARY_TUBE_OUTER_DIAMETER_MM,
            features.capillary_tube_outer_diameter_mm,
            p.tolerance_for("capillary_tube_outer_diameter"),
        ),
    ]


def _reservoir_feature_checks(features: ReservoirFeatures) -> list[ValidationCheck]:
    return [
        _dimension_check(
            "reservoir_mouth_inner_diameter",
            "Wewnętrzna średnica zbiornika zgodna ze specyfikacją.",
            p.RESERVOIR_MOUTH_INNER_DIAMETER_MM,
            features.mouth_inner_diameter_mm,
            p.tolerance_for("reservoir_mouth_inner_diameter"),
        ),
        _dimension_check(
            "reservoir_cavity_depth",
            "Głębokość komory zbiornika zgodna ze specyfikacją.",
            p.RESERVOIR_CAVITY_DEPTH_MM,
            features.cavity_depth_mm,
            p.tolerance_for("reservoir_cavity_depth"),
        ),
        ValidationCheck(
            id="reservoir_foot_count",
            description="Liczba nóżek zbiornika zgodna ze specyfikacją.",
            expected=p.RESERVOIR_FOOT_COUNT,
            actual=features.foot_count,
            tolerance=0,
            status=PASSED if features.foot_count == p.RESERVOIR_FOOT_COUNT else FAILED,
            message=""
            if features.foot_count == p.RESERVOIR_FOOT_COUNT
            else f"Expected {p.RESERVOIR_FOOT_COUNT} feet, got {features.foot_count}.",
        ),
    ]


def _fit_check(insert: InsertFeatures, reservoir: ReservoirFeatures) -> ValidationCheck:
    """Spigot (derived from reservoir_mouth_inner_diameter) must slip inside
    the reservoir's mouth with a positive, bounded clearance — recomputes
    the same derivation as ``check_engineering_preconditions`` directly
    from the built parts' reported dimensions, not just from the raw
    parameters, so a feature-metadata bug would also be caught here."""
    spigot_od = reservoir.mouth_inner_diameter_mm - 2 * p.FIT_CLEARANCE_MM
    ok = 0 < spigot_od < insert.bottom_outer_diameter_mm
    return ValidationCheck(
        id="spigot_fits_reservoir_mouth",
        description="Spódnica wkładu mieści się (na wcisk) w gardzieli zbiornika.",
        expected="0 < spigot_outer_diameter < insert_bottom_outer_diameter",
        actual=spigot_od,
        tolerance=None,
        status=PASSED if ok else FAILED,
        message="" if ok else f"Derived spigot_outer_diameter ({spigot_od:.2f} mm) out of range.",
    )


def rebuild_check() -> tuple[ValidationCheck, PlanterResult | None]:
    try:
        second = build_model()
    except Exception as exc:  # noqa: BLE001 - deliberately captured for the report
        return (
            ValidationCheck(
                id="rebuild_succeeds",
                description="Oba elementy dają się odbudować bez błędu.",
                expected="no exception",
                actual=f"{type(exc).__name__}: {exc}",
                tolerance=None,
                status=FAILED,
                message="Rebuilding raised an unhandled exception.",
            ),
            None,
        )
    return (
        ValidationCheck(
            id="rebuild_succeeds",
            description="Oba elementy dają się odbudować bez błędu.",
            expected="no exception",
            actual="no exception",
            tolerance=None,
            status=PASSED,
        ),
        second,
    )


def determinism_check(first: PlanterResult, second: PlanterResult) -> ValidationCheck:
    from cad_project.measurements import measure

    def same_part(a, b) -> bool:
        ma, mb = measure(a.part), measure(b.part)
        return (
            ma.solid_count == mb.solid_count
            and abs(ma.volume_mm3 - mb.volume_mm3) < 1e-6
            and abs(ma.surface_area_mm2 - mb.surface_area_mm2) < 1e-6
            and ma.bounding_box_mm == mb.bounding_box_mm
        )

    same = (
        same_part(first.insert, second.insert)
        and same_part(first.reservoir, second.reservoir)
        and first.insert.features == second.insert.features
        and first.reservoir.features == second.reservoir.features
    )
    return ValidationCheck(
        id="rebuild_deterministic",
        description="Dwa niezależne budowania dają identyczne pomiary i cechy dla obu części.",
        expected="identical",
        actual="identical" if same else "differs",
        tolerance=None,
        status=PASSED if same else FAILED,
        message="" if same else "Rebuilt parts differ from the first build.",
    )


def _part_measurements_dict(measurements: Measurements) -> dict[str, Any]:
    return {
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
    }


def _exports_entry(step: ExportOutcome, stl: ExportOutcome, preview: RenderOutcome) -> dict[str, Any]:
    def entry(outcome: ExportOutcome | RenderOutcome) -> dict[str, Any]:
        d: dict[str, Any] = {"status": outcome.status, "path": outcome.path}
        if outcome.error:
            d["error"] = outcome.error
        return d

    return {"step": entry(step), "stl": entry(stl), "preview": entry(preview)}


def build_report(
    result: PlanterResult,
    insert_measurements: Measurements,
    reservoir_measurements: Measurements,
    insert_exports: tuple[ExportOutcome, ExportOutcome, RenderOutcome],
    reservoir_exports: tuple[ExportOutcome, ExportOutcome, RenderOutcome],
    *,
    include_rebuild_checks: bool = True,
) -> dict[str, Any]:
    checks: list[ValidationCheck] = []
    checks.extend(_solid_checks("insert", insert_measurements))
    checks.extend(_solid_checks("reservoir", reservoir_measurements))
    checks.extend(_insert_feature_checks(result.insert.features))
    checks.extend(_reservoir_feature_checks(result.reservoir.features))
    checks.append(_fit_check(result.insert.features, result.reservoir.features))

    if include_rebuild_checks:
        rebuild_result, second = rebuild_check()
        checks.append(rebuild_result)
        if second is not None:
            checks.append(determinism_check(result, second))

    insert_step, insert_stl, insert_preview = insert_exports
    reservoir_step, reservoir_stl, reservoir_preview = reservoir_exports

    for label, outcome in (
        ("insert_export_step_exists", insert_step),
        ("insert_export_stl_exists", insert_stl),
        ("reservoir_export_step_exists", reservoir_step),
        ("reservoir_export_stl_exists", reservoir_stl),
    ):
        checks.append(
            ValidationCheck(
                id=label,
                description=f"{label.replace('_', ' ')} succeeded and produced a non-empty file.",
                expected=PASSED,
                actual=outcome.status,
                tolerance=None,
                status=outcome.status,
                message=outcome.error or "",
            )
        )

    overall_status = PASSED if all(c.status == PASSED for c in checks) else FAILED

    report: dict[str, Any] = {
        "status": overall_status,
        "spec_version": p.SPEC_VERSION,
        "model_id": p.MODEL_ID,
        "generated_at": datetime.now(UTC).isoformat(),
        "parts": {
            "insert": {
                "model": _part_measurements_dict(insert_measurements),
                "features": {
                    "top_outer_diameter_mm": result.insert.features.top_outer_diameter_mm,
                    "bottom_outer_diameter_mm": result.insert.features.bottom_outer_diameter_mm,
                    "body_height_mm": result.insert.features.body_height_mm,
                    "drainage_hole_count": result.insert.features.drainage_hole_count,
                    "pattern_flute_count": result.insert.features.pattern_flute_count,
                },
            },
            "reservoir": {
                "model": _part_measurements_dict(reservoir_measurements),
                "features": {
                    "mouth_inner_diameter_mm": result.reservoir.features.mouth_inner_diameter_mm,
                    "cavity_depth_mm": result.reservoir.features.cavity_depth_mm,
                    "foot_count": result.reservoir.features.foot_count,
                },
            },
        },
        "checks": [c.as_dict() for c in checks],
        "exports": {
            "insert": _exports_entry(insert_step, insert_stl, insert_preview),
            "reservoir": _exports_entry(reservoir_step, reservoir_stl, reservoir_preview),
        },
    }
    return report


def error_report(exc: Exception, stage: str) -> dict[str, Any]:
    return {
        "status": FAILED,
        "spec_version": p.SPEC_VERSION,
        "model_id": p.MODEL_ID,
        "generated_at": datetime.now(UTC).isoformat(),
        "stage": stage,
        "checks": [
            ValidationCheck(
                id="no_unhandled_exceptions",
                description="Pipeline nie zgłasza nieobsłużonych wyjątków.",
                expected="no exception",
                actual=f"{type(exc).__name__}: {exc}",
                tolerance=None,
                status=FAILED,
                message=f"Unhandled exception during stage '{stage}'.",
            ).as_dict()
        ],
    }
