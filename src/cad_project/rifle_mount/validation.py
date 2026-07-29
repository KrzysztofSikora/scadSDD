"""Explicit, rule-based validation for the two-part rifle mount.

Mirrors ``cad_project.validation`` (the bracket) in spirit — every check is
self-contained (id, description, expected, actual, tolerance, status,
message) — but the report covers **two independent parts** (base + arm),
since this model does not produce a single solid (see
specs/rifle-mount/constraints.md).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any

from cad_project.exports import ExportOutcome
from cad_project.measurements import Measurements
from cad_project.rendering import RenderOutcome
from cad_project.rifle_mount import parameters as p
from cad_project.rifle_mount.model import ArmFeatures, BaseFeatures, RifleMountResult, build_model

PASSED = "passed"
FAILED = "failed"

REPORT_PATH = p.REPO_ROOT / "output" / "rifle-mount" / "reports" / "validation-report.json"


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


def _base_feature_checks(features: BaseFeatures) -> list[ValidationCheck]:
    checks = [
        ValidationCheck(
            id="magnet_count",
            description="Liczba magnesów zgodna ze specyfikacją.",
            expected=p.MAGNET_COUNT,
            actual=features.magnet_count,
            tolerance=0,
            status=PASSED if features.magnet_count == p.MAGNET_COUNT else FAILED,
            message=""
            if features.magnet_count == p.MAGNET_COUNT
            else f"Expected {p.MAGNET_COUNT} magnets, got {features.magnet_count}.",
        ),
        _dimension_check(
            "magnet_diameter",
            "Średnica magnesów zgodna ze specyfikacją.",
            p.MAGNET_DIAMETER_MM,
            features.magnet_diameter_mm,
            p.tolerance_for("magnet_diameter"),
        ),
        _dimension_check(
            "mounting_plate_size",
            "Wymiar płyty mocującej zgodny ze specyfikacją.",
            p.MOUNTING_PLATE_SIZE_MM,
            features.plate_size_mm,
            p.tolerance_for("mounting_plate_size"),
        ),
    ]
    return checks


def _arm_feature_checks(features: ArmFeatures) -> list[ValidationCheck]:
    return [
        _dimension_check(
            "u_internal_width",
            "Prześwit chwytu U zgodny ze specyfikacją.",
            p.U_INTERNAL_WIDTH_MM,
            features.u_internal_width_mm,
            p.tolerance_for("u_internal_width"),
        ),
        _dimension_check(
            "collar_diameter",
            "Średnica kołnierza oporowego zgodna ze specyfikacją.",
            p.COLLAR_DIAMETER_MM,
            features.collar_diameter_mm,
            p.tolerance_for("collar_diameter"),
        ),
        _dimension_check(
            "rod_threaded_length",
            "Długość gwintowanej części trzpienia zgodna ze specyfikacją.",
            p.ROD_THREADED_LENGTH_MM,
            features.rod_threaded_length_mm,
            p.tolerance_for("rod_threaded_length"),
        ),
    ]


def _thread_compatibility_check(base: BaseFeatures, arm: ArmFeatures) -> ValidationCheck:
    """Internal (base) and external (arm) thread must share pitch/diameter/angle.

    This is checked from the explicit ``ThreadFeatures`` metadata each part
    reports it was built with — not re-derived by inspecting the helical
    solid topology, which is far more complex than the bracket's simple
    cylindrical holes (see specs/rifle-mount/constraints.md).
    """
    ok = base.thread == arm.thread
    return ValidationCheck(
        id="thread_compatibility",
        description="Gwint wewnętrzny (base) i zewnętrzny (arm) mają identyczne parametry.",
        expected=base.thread.__dict__,
        actual=arm.thread.__dict__,
        tolerance=None,
        status=PASSED if ok else FAILED,
        message="" if ok else "Thread parameters differ between base and arm.",
    )


def _thread_engagement_range_check() -> ValidationCheck:
    """Recompute the fixed-offset/engagement derivation from specs/rifle-mount/decisions.md.

    The U cradle is centered on the rod axis, so the Z-offset from the
    collar to the barrel center is u_wall_thickness + u_internal_width/2
    (the slot's own center), not barrel_diameter_reference/2 — see
    "U cradle coaxial alignment fix" in decisions.md.
    """
    fixed_offset = (
        p.MOUNTING_PLATE_THICKNESS_MM
        + p.NUT_BOSS_LENGTH_MM
        + p.COLLAR_LENGTH_MM
        + p.U_WALL_THICKNESS_MM
        + p.U_INTERNAL_WIDTH_MM / 2
    )
    exposed_max = p.WALL_TO_BARREL_CENTER_MAX_MM - fixed_offset
    min_engagement_at_max_extension = p.ROD_THREADED_LENGTH_MM - exposed_max
    ok = min_engagement_at_max_extension >= p.THREAD_ENGAGEMENT_LENGTH_MM
    return ValidationCheck(
        id="thread_engagement_at_max_extension",
        description=(
            "Zazębienie gwintu przy maksymalnym wysunięciu (140mm) nie spada "
            "poniżej thread_engagement_length."
        ),
        expected=f">= {p.THREAD_ENGAGEMENT_LENGTH_MM}",
        actual=min_engagement_at_max_extension,
        tolerance=None,
        status=PASSED if ok else FAILED,
        message=""
        if ok
        else (
            f"Engagement at max extension ({min_engagement_at_max_extension:.2f} mm) is below "
            f"thread_engagement_length ({p.THREAD_ENGAGEMENT_LENGTH_MM} mm)."
        ),
    )


def rebuild_check() -> tuple[ValidationCheck, RifleMountResult | None]:
    """Rebuild both parts and verify success — see cad_project.validation for the pattern.

    Note: this doubles build time (~20-30s extra on typical hardware,
    dominated by the helical thread sweeps) — see
    specs/rifle-mount/decisions.md.
    """
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


def determinism_check(first: RifleMountResult, second: RifleMountResult) -> ValidationCheck:
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
        same_part(first.base, second.base)
        and same_part(first.arm, second.arm)
        and first.base.features == second.base.features
        and first.arm.features == second.arm.features
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
    result: RifleMountResult,
    base_measurements: Measurements,
    arm_measurements: Measurements,
    base_exports: tuple[ExportOutcome, ExportOutcome, RenderOutcome],
    arm_exports: tuple[ExportOutcome, ExportOutcome, RenderOutcome],
    *,
    include_rebuild_checks: bool = True,
) -> dict[str, Any]:
    checks: list[ValidationCheck] = []
    checks.extend(_solid_checks("base", base_measurements))
    checks.extend(_solid_checks("arm", arm_measurements))
    checks.extend(_base_feature_checks(result.base.features))
    checks.extend(_arm_feature_checks(result.arm.features))
    checks.append(_thread_compatibility_check(result.base.features, result.arm.features))
    checks.append(_thread_engagement_range_check())

    if include_rebuild_checks:
        rebuild_result, second = rebuild_check()
        checks.append(rebuild_result)
        if second is not None:
            checks.append(determinism_check(result, second))

    base_step, base_stl, base_preview = base_exports
    arm_step, arm_stl, arm_preview = arm_exports

    for label, outcome in (
        ("base_export_step_exists", base_step),
        ("base_export_stl_exists", base_stl),
        ("arm_export_step_exists", arm_step),
        ("arm_export_stl_exists", arm_stl),
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
            "base": {
                "model": _part_measurements_dict(base_measurements),
                "features": {
                    "magnet_count": result.base.features.magnet_count,
                    "magnet_diameter_mm": result.base.features.magnet_diameter_mm,
                    "magnet_positions_mm": [
                        list(pos) for pos in result.base.features.magnet_positions_mm
                    ],
                    "nut_boss_outer_diameter_mm": result.base.features.nut_boss_outer_diameter_mm,
                    "thread": result.base.features.thread.__dict__,
                },
            },
            "arm": {
                "model": _part_measurements_dict(arm_measurements),
                "features": {
                    "rod_threaded_length_mm": result.arm.features.rod_threaded_length_mm,
                    "collar_diameter_mm": result.arm.features.collar_diameter_mm,
                    "u_internal_width_mm": result.arm.features.u_internal_width_mm,
                    "u_arm_length_mm": result.arm.features.u_arm_length_mm,
                    "thread": result.arm.features.thread.__dict__,
                },
            },
        },
        "checks": [c.as_dict() for c in checks],
        "exports": {
            "base": _exports_entry(base_step, base_stl, base_preview),
            "arm": _exports_entry(arm_step, arm_stl, arm_preview),
        },
    }

    warnings = []
    if base_preview.status != PASSED:
        warnings.append(f"Base preview rendering failed (reported independently): {base_preview.error}")
    if arm_preview.status != PASSED:
        warnings.append(f"Arm preview rendering failed (reported independently): {arm_preview.error}")
    if warnings:
        report["warnings"] = warnings

    return report


def error_report(exc: Exception, stage: str) -> dict[str, Any]:
    return {
        "status": FAILED,
        "spec_version": p.SPEC_VERSION,
        "model_id": p.MODEL_ID,
        "generated_at": datetime.now(UTC).isoformat(),
        "parts": None,
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
            "base": {
                "step": {"status": "skipped", "path": ""},
                "stl": {"status": "skipped", "path": ""},
                "preview": {"status": "skipped", "path": ""},
            },
            "arm": {
                "step": {"status": "skipped", "path": ""},
                "stl": {"status": "skipped", "path": ""},
                "preview": {"status": "skipped", "path": ""},
            },
        },
    }
