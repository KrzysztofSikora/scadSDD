"""Command-line entry point for the self-watering planter pipeline.

Same command vocabulary as ``cad_project.cli`` (the bracket) and
``cad_project.rifle_mount.cli``: build, export, render, validate, all,
clean — but operating on **two** physical parts (insert + reservoir) and
their own output tree, ``output/planter/``. Run as
``python -m cad_project.planter.cli <command>``.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys

from cad_project.exports import existing_export_outcome, export_step_file, export_stl_file
from cad_project.measurements import measure
from cad_project.planter import parameters as p
from cad_project.planter.model import build_model
from cad_project.planter.validation import REPORT_PATH, build_report, error_report
from cad_project.rendering import existing_preview_outcome, render_preview_png

OUTPUT_ROOT = p.REPO_ROOT / "output" / "planter"
INSERT_STEP_PATH = OUTPUT_ROOT / "step" / "insert.step"
RESERVOIR_STEP_PATH = OUTPUT_ROOT / "step" / "reservoir.step"
INSERT_STL_PATH = OUTPUT_ROOT / "stl" / "insert.stl"
RESERVOIR_STL_PATH = OUTPUT_ROOT / "stl" / "reservoir.stl"
INSERT_PREVIEW_PATH = OUTPUT_ROOT / "previews" / "insert.png"
RESERVOIR_PREVIEW_PATH = OUTPUT_ROOT / "previews" / "reservoir.png"
LOG_PATH = OUTPUT_ROOT / "logs" / "build.log"

logger = logging.getLogger("cad_project.planter")


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
    logger.info("Building '%s' (spec version %s)...", p.MODEL_ID, p.SPEC_VERSION)
    result = build_model()
    insert_m = measure(result.insert.part)
    reservoir_m = measure(result.reservoir.part)
    logger.info(
        "Insert OK: solid_count=%d bbox=(%.1f, %.1f, %.1f) volume=%.1f mm^3",
        insert_m.solid_count, insert_m.bounding_box_mm.x_mm, insert_m.bounding_box_mm.y_mm,
        insert_m.bounding_box_mm.z_mm, insert_m.volume_mm3,
    )
    logger.info(
        "Reservoir OK: solid_count=%d bbox=(%.1f, %.1f, %.1f) volume=%.1f mm^3",
        reservoir_m.solid_count, reservoir_m.bounding_box_mm.x_mm, reservoir_m.bounding_box_mm.y_mm,
        reservoir_m.bounding_box_mm.z_mm, reservoir_m.volume_mm3,
    )
    return 0


def cmd_export(_args: argparse.Namespace) -> int:
    logger.info("Building model for export...")
    result = build_model()
    insert_step = export_step_file(result.insert.part, INSERT_STEP_PATH)
    reservoir_step = export_step_file(result.reservoir.part, RESERVOIR_STEP_PATH)
    insert_stl = export_stl_file(result.insert.part, INSERT_STL_PATH)
    reservoir_stl = export_stl_file(result.reservoir.part, RESERVOIR_STL_PATH)
    for label, outcome in (
        ("insert STEP", insert_step), ("reservoir STEP", reservoir_step),
        ("insert STL", insert_stl), ("reservoir STL", reservoir_stl),
    ):
        logger.info("%s export: %s -> %s", label, outcome.status, outcome.path)
    ok = all(o.status == "passed" for o in (insert_step, reservoir_step, insert_stl, reservoir_stl))
    return 0 if ok else 1


def cmd_render(_args: argparse.Namespace) -> int:
    logger.info("Building model for preview rendering...")
    result = build_model()
    insert_outcome = render_preview_png(result.insert.part, INSERT_PREVIEW_PATH)
    reservoir_outcome = render_preview_png(result.reservoir.part, RESERVOIR_PREVIEW_PATH)
    for label, outcome in (("insert", insert_outcome), ("reservoir", reservoir_outcome)):
        if outcome.status == "passed":
            logger.info("Preview (%s) rendered: %s", label, outcome.path)
        else:
            logger.error("Preview (%s) rendering failed: %s", label, outcome.error)
    ok = insert_outcome.status == "passed" and reservoir_outcome.status == "passed"
    return 0 if ok else 1


def cmd_validate(_args: argparse.Namespace) -> int:
    logger.info("Building and measuring model for validation...")
    result = build_model()
    insert_m = measure(result.insert.part)
    reservoir_m = measure(result.reservoir.part)

    insert_exports = (
        existing_export_outcome(INSERT_STEP_PATH, "insert STEP"),
        existing_export_outcome(INSERT_STL_PATH, "insert STL"),
        existing_preview_outcome(INSERT_PREVIEW_PATH),
    )
    reservoir_exports = (
        existing_export_outcome(RESERVOIR_STEP_PATH, "reservoir STEP"),
        existing_export_outcome(RESERVOIR_STL_PATH, "reservoir STL"),
        existing_preview_outcome(RESERVOIR_PREVIEW_PATH),
    )

    report = build_report(result, insert_m, reservoir_m, insert_exports, reservoir_exports)
    _write_report(report)
    logger.info("Validation status: %s", report["status"])
    for check in report["checks"]:
        if check["status"] != "passed":
            logger.warning("Check failed: %s - %s", check["id"], check.get("message", ""))
    return 0 if report["status"] == "passed" else 1


def cmd_all(_args: argparse.Namespace) -> int:
    logger.info("Running full pipeline (build -> measure -> validate -> export -> render -> report)...")
    result = build_model()
    insert_m = measure(result.insert.part)
    reservoir_m = measure(result.reservoir.part)

    insert_step = export_step_file(result.insert.part, INSERT_STEP_PATH)
    reservoir_step = export_step_file(result.reservoir.part, RESERVOIR_STEP_PATH)
    insert_stl = export_stl_file(result.insert.part, INSERT_STL_PATH)
    reservoir_stl = export_stl_file(result.reservoir.part, RESERVOIR_STL_PATH)
    for label, outcome in (
        ("insert STEP", insert_step), ("reservoir STEP", reservoir_step),
        ("insert STL", insert_stl), ("reservoir STL", reservoir_stl),
    ):
        logger.info("%s export: %s -> %s", label, outcome.status, outcome.path)

    insert_preview = render_preview_png(result.insert.part, INSERT_PREVIEW_PATH)
    reservoir_preview = render_preview_png(result.reservoir.part, RESERVOIR_PREVIEW_PATH)
    for label, preview_outcome in (("insert", insert_preview), ("reservoir", reservoir_preview)):
        if preview_outcome.status == "passed":
            logger.info("Preview (%s) rendered: %s", label, preview_outcome.path)
        else:
            logger.warning(
                "Preview (%s) failed (does not block STEP/STL): %s", label, preview_outcome.error
            )

    report = build_report(
        result, insert_m, reservoir_m,
        (insert_step, insert_stl, insert_preview),
        (reservoir_step, reservoir_stl, reservoir_preview),
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
        prog="python -m cad_project.planter.cli",
        description="Spec-driven CAD pipeline for the premium self-watering planter.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("build", help="Build both parts and report basic geometry facts.")
    subparsers.add_parser("export", help="Build and export STEP + STL for both parts.")
    subparsers.add_parser("render", help="Build and render isometric PNG previews for both parts.")
    subparsers.add_parser("validate", help="Validate against the spec and write the JSON report.")
    subparsers.add_parser("all", help="Run the full pipeline end to end.")
    subparsers.add_parser("clean", help="Remove generated files under output/planter/.")
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
