"""Command-line entry point for the rifle mount pipeline.

Same command vocabulary as ``cad_project.cli`` (the bracket): build,
export, render, validate, all, clean — but operating on **two** physical
parts (base + arm) and their own output tree, ``output/rifle-mount/``.
Run as ``python -m cad_project.rifle_mount.cli <command>``.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys

from cad_project.exports import existing_export_outcome, export_step_file, export_stl_file
from cad_project.measurements import measure
from cad_project.rendering import existing_preview_outcome, render_preview_png
from cad_project.rifle_mount import parameters as p
from cad_project.rifle_mount.model import build_model
from cad_project.rifle_mount.validation import REPORT_PATH, build_report, error_report

OUTPUT_ROOT = p.REPO_ROOT / "output" / "rifle-mount"
BASE_STEP_PATH = OUTPUT_ROOT / "step" / "base.step"
ARM_STEP_PATH = OUTPUT_ROOT / "step" / "arm.step"
BASE_STL_PATH = OUTPUT_ROOT / "stl" / "base.stl"
ARM_STL_PATH = OUTPUT_ROOT / "stl" / "arm.stl"
BASE_PREVIEW_PATH = OUTPUT_ROOT / "previews" / "base.png"
ARM_PREVIEW_PATH = OUTPUT_ROOT / "previews" / "arm.png"
LOG_PATH = OUTPUT_ROOT / "logs" / "build.log"

logger = logging.getLogger("cad_project.rifle_mount")


def _setup_logging() -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    file_handler = logging.FileHandler(LOG_PATH, mode="w", encoding="utf-8")
    stream_handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    for handler in (file_handler, stream_handler):
        handler.setFormatter(formatter)
        logger.addHandler(handler)


def _write_report(report: dict) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    logger.info("Validation report written to %s", REPORT_PATH)


def cmd_build(_args: argparse.Namespace) -> int:
    logger.info("Building '%s' (spec version %s)... (thread sweeps take ~20-30s)", p.MODEL_ID, p.SPEC_VERSION)
    result = build_model()
    base_m = measure(result.base.part)
    arm_m = measure(result.arm.part)
    logger.info(
        "Base OK: solid_count=%d bbox=(%.1f, %.1f, %.1f) volume=%.1f mm^3",
        base_m.solid_count, base_m.bounding_box_mm.x_mm, base_m.bounding_box_mm.y_mm,
        base_m.bounding_box_mm.z_mm, base_m.volume_mm3,
    )
    logger.info(
        "Arm OK: solid_count=%d bbox=(%.1f, %.1f, %.1f) volume=%.1f mm^3",
        arm_m.solid_count, arm_m.bounding_box_mm.x_mm, arm_m.bounding_box_mm.y_mm,
        arm_m.bounding_box_mm.z_mm, arm_m.volume_mm3,
    )
    return 0


def cmd_export(_args: argparse.Namespace) -> int:
    logger.info("Building model for export...")
    result = build_model()
    base_step = export_step_file(result.base.part, BASE_STEP_PATH)
    arm_step = export_step_file(result.arm.part, ARM_STEP_PATH)
    base_stl = export_stl_file(result.base.part, BASE_STL_PATH)
    arm_stl = export_stl_file(result.arm.part, ARM_STL_PATH)
    for label, outcome in (
        ("base STEP", base_step), ("arm STEP", arm_step),
        ("base STL", base_stl), ("arm STL", arm_stl),
    ):
        logger.info("%s export: %s -> %s", label, outcome.status, outcome.path)
    ok = all(o.status == "passed" for o in (base_step, arm_step, base_stl, arm_stl))
    return 0 if ok else 1


def cmd_render(_args: argparse.Namespace) -> int:
    logger.info("Building model for preview rendering...")
    result = build_model()
    base_outcome = render_preview_png(result.base.part, BASE_PREVIEW_PATH)
    arm_outcome = render_preview_png(result.arm.part, ARM_PREVIEW_PATH)
    for label, outcome in (("base", base_outcome), ("arm", arm_outcome)):
        if outcome.status == "passed":
            logger.info("Preview (%s) rendered: %s", label, outcome.path)
        else:
            logger.error("Preview (%s) rendering failed: %s", label, outcome.error)
    ok = base_outcome.status == "passed" and arm_outcome.status == "passed"
    return 0 if ok else 1


def cmd_validate(_args: argparse.Namespace) -> int:
    logger.info("Building and measuring model for validation...")
    result = build_model()
    base_m = measure(result.base.part)
    arm_m = measure(result.arm.part)

    base_exports = (
        existing_export_outcome(BASE_STEP_PATH, "base STEP"),
        existing_export_outcome(BASE_STL_PATH, "base STL"),
        existing_preview_outcome(BASE_PREVIEW_PATH),
    )
    arm_exports = (
        existing_export_outcome(ARM_STEP_PATH, "arm STEP"),
        existing_export_outcome(ARM_STL_PATH, "arm STL"),
        existing_preview_outcome(ARM_PREVIEW_PATH),
    )

    report = build_report(result, base_m, arm_m, base_exports, arm_exports)
    _write_report(report)
    logger.info("Validation status: %s", report["status"])
    for check in report["checks"]:
        if check["status"] != "passed":
            logger.warning("Check failed: %s - %s", check["id"], check.get("message", ""))
    return 0 if report["status"] == "passed" else 1


def cmd_all(_args: argparse.Namespace) -> int:
    logger.info("Running full pipeline (build -> measure -> validate -> export -> render -> report)...")
    result = build_model()
    base_m = measure(result.base.part)
    arm_m = measure(result.arm.part)

    base_step = export_step_file(result.base.part, BASE_STEP_PATH)
    arm_step = export_step_file(result.arm.part, ARM_STEP_PATH)
    base_stl = export_stl_file(result.base.part, BASE_STL_PATH)
    arm_stl = export_stl_file(result.arm.part, ARM_STL_PATH)
    for label, outcome in (
        ("base STEP", base_step), ("arm STEP", arm_step),
        ("base STL", base_stl), ("arm STL", arm_stl),
    ):
        logger.info("%s export: %s -> %s", label, outcome.status, outcome.path)

    base_preview = render_preview_png(result.base.part, BASE_PREVIEW_PATH)
    arm_preview = render_preview_png(result.arm.part, ARM_PREVIEW_PATH)
    for label, preview_outcome in (("base", base_preview), ("arm", arm_preview)):
        if preview_outcome.status == "passed":
            logger.info("Preview (%s) rendered: %s", label, preview_outcome.path)
        else:
            logger.warning(
                "Preview (%s) failed (does not block STEP/STL): %s", label, preview_outcome.error
            )

    report = build_report(
        result, base_m, arm_m,
        (base_step, base_stl, base_preview),
        (arm_step, arm_stl, arm_preview),
    )
    _write_report(report)
    logger.info("Validation status: %s", report["status"])
    for check in report["checks"]:
        if check["status"] != "passed":
            logger.warning("Check failed: %s - %s", check["id"], check.get("message", ""))
    return 0 if report["status"] == "passed" else 1


def cmd_clean(_args: argparse.Namespace) -> int:
    removed = 0
    for sub in ("step", "stl", "previews", "reports", "logs"):
        target_dir = OUTPUT_ROOT / sub
        if not target_dir.exists():
            continue
        for entry in target_dir.iterdir():
            if entry.name == ".gitkeep":
                continue
            entry.unlink()
            removed += 1
    print(f"Removed {removed} generated file(s) under {OUTPUT_ROOT}.")
    return 0


def _run_with_error_report(stage: str, fn, args: argparse.Namespace) -> int:
    try:
        return fn(args)
    except Exception as exc:  # noqa: BLE001 - surfaced to the user and the report
        logger.exception("Unhandled exception during stage '%s'", stage)
        if stage in ("validate", "all"):
            _write_report(error_report(exc, stage))
        return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m cad_project.rifle_mount.cli",
        description="Spec-driven CAD pipeline for the magnetic rifle barrel mount.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("build", help="Build both parts and report basic geometry facts.")
    subparsers.add_parser("export", help="Build and export STEP + STL for both parts.")
    subparsers.add_parser("render", help="Build and render isometric PNG previews for both parts.")
    subparsers.add_parser("validate", help="Validate against the spec and write the JSON report.")
    subparsers.add_parser("all", help="Run the full pipeline end to end.")
    subparsers.add_parser("clean", help="Remove generated files under output/rifle-mount/.")
    return parser


_COMMANDS = {
    "build": cmd_build,
    "export": cmd_export,
    "render": cmd_render,
    "validate": cmd_validate,
    "all": cmd_all,
    "clean": cmd_clean,
}


def main(argv: list[str] | None = None) -> int:
    _setup_logging()
    parser = build_parser()
    args = parser.parse_args(argv)
    handler = _COMMANDS[args.command]
    return _run_with_error_report(args.command, handler, args)


if __name__ == "__main__":
    sys.exit(main())
