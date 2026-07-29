"""Command-line entry point for the spec-driven CAD pipeline.

Commands
--------
build      Build the model in-memory and report basic geometry facts.
export     Build the model and export STEP + STL.
render     Build the model and render the isometric PNG preview.
validate   Build, measure, run validation checks, and check for existing
           exports (without regenerating them). Writes the JSON report.
all        Build, measure, validate, export STEP, export STL, render the
           preview, and write the JSON report — the full pipeline.
clean      Remove generated files under output/ (keeps .gitkeep markers).

Exit codes: 0 on success (validation "passed" for `validate`/`all`), 1 on
any failure. This lets CI or a shell script chain commands with `&&`.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys

from cad_project import parameters as p
from cad_project.exports import (
    STEP_PATH,
    STL_PATH,
    existing_export_outcome,
    export_step_file,
    export_stl_file,
)
from cad_project.measurements import measure
from cad_project.model import build_model
from cad_project.rendering import PREVIEW_PATH, existing_preview_outcome, render_preview_png
from cad_project.validation import REPORT_PATH, build_report, error_report

LOG_PATH = p.REPO_ROOT / "output" / "logs" / "build.log"

logger = logging.getLogger("cad_project")


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
    logger.info("Building model '%s' (spec version %s)...", p.MODEL_ID, p.SPEC_VERSION)
    result = build_model()
    measurements = measure(result.part)
    logger.info(
        "Build OK: solid_count=%d bounding_box=(%.3f, %.3f, %.3f) mm volume=%.3f mm^3",
        measurements.solid_count,
        measurements.bounding_box_mm.x_mm,
        measurements.bounding_box_mm.y_mm,
        measurements.bounding_box_mm.z_mm,
        measurements.volume_mm3,
    )
    return 0


def cmd_export(_args: argparse.Namespace) -> int:
    logger.info("Building model for export...")
    result = build_model()
    step_outcome = export_step_file(result.part, STEP_PATH)
    logger.info("STEP export: %s -> %s", step_outcome.status, step_outcome.path)
    stl_outcome = export_stl_file(result.part, STL_PATH)
    logger.info("STL export: %s -> %s", stl_outcome.status, stl_outcome.path)
    ok = step_outcome.status == "passed" and stl_outcome.status == "passed"
    if not ok:
        logger.error("Export failed. STEP error=%s STL error=%s", step_outcome.error, stl_outcome.error)
    return 0 if ok else 1


def cmd_render(_args: argparse.Namespace) -> int:
    logger.info("Building model for preview rendering...")
    result = build_model()
    outcome = render_preview_png(result.part, PREVIEW_PATH)
    if outcome.status == "passed":
        logger.info("Preview rendered: %s", outcome.path)
        return 0
    logger.error("Preview rendering failed (reported independently): %s", outcome.error)
    return 1


def cmd_validate(_args: argparse.Namespace) -> int:
    logger.info("Building and measuring model for validation...")
    result = build_model()
    measurements = measure(result.part)

    step_outcome = existing_export_outcome(STEP_PATH, "STEP")
    stl_outcome = existing_export_outcome(STL_PATH, "STL")
    preview_outcome = existing_preview_outcome(PREVIEW_PATH)

    report = build_report(result, measurements, step_outcome, stl_outcome, preview_outcome)
    _write_report(report)
    logger.info("Validation status: %s", report["status"])
    for check in report["checks"]:
        if check["status"] != "passed":
            logger.warning("Check failed: %s - %s", check["id"], check.get("message", ""))
    return 0 if report["status"] == "passed" else 1


def cmd_all(_args: argparse.Namespace) -> int:
    logger.info("Running full pipeline (build -> measure -> validate -> export -> render -> report)...")
    result = build_model()
    measurements = measure(result.part)

    step_outcome = export_step_file(result.part, STEP_PATH)
    logger.info("STEP export: %s -> %s", step_outcome.status, step_outcome.path)

    stl_outcome = export_stl_file(result.part, STL_PATH)
    logger.info("STL export: %s -> %s", stl_outcome.status, stl_outcome.path)

    preview_outcome = render_preview_png(result.part, PREVIEW_PATH)
    if preview_outcome.status == "passed":
        logger.info("Preview rendered: %s", preview_outcome.path)
    else:
        logger.warning(
            "Preview rendering failed (does not block STEP/STL): %s", preview_outcome.error
        )

    report = build_report(result, measurements, step_outcome, stl_outcome, preview_outcome)
    _write_report(report)
    logger.info("Validation status: %s", report["status"])
    for check in report["checks"]:
        if check["status"] != "passed":
            logger.warning("Check failed: %s - %s", check["id"], check.get("message", ""))

    return 0 if report["status"] == "passed" else 1


def cmd_clean(_args: argparse.Namespace) -> int:
    output_dir = p.REPO_ROOT / "output"
    removed = 0
    for sub in ("step", "stl", "previews", "reports", "logs"):
        target_dir = output_dir / sub
        if not target_dir.exists():
            continue
        for entry in target_dir.iterdir():
            if entry.name == ".gitkeep":
                continue
            entry.unlink()
            removed += 1
    print(f"Removed {removed} generated file(s) under {output_dir}.")
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
        prog="python -m cad_project.cli",
        description="Spec-driven CAD pipeline for the parametric mounting bracket.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("build", help="Build the model and report basic geometry facts.")
    subparsers.add_parser("export", help="Build the model and export STEP + STL.")
    subparsers.add_parser("render", help="Build the model and render the isometric PNG preview.")
    subparsers.add_parser(
        "validate", help="Validate the model against the spec and write the JSON report."
    )
    subparsers.add_parser("all", help="Run the full pipeline end to end.")
    subparsers.add_parser("clean", help="Remove generated files under output/.")

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
