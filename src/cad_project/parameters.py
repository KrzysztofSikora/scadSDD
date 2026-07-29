"""Single source of truth for all numeric model parameters.

All numeric values used by the model come from ``specs/parameters.yaml``,
loaded once at import time. Nothing in this module (or anywhere else in the
codebase) hardcodes a dimension a second time — if a value needs to change,
it changes in ``specs/parameters.yaml`` only.

``specs/spec.md`` carries a human-readable copy of the same data for
reviewers; :func:`load_spec_md_parameters` extracts it (via a real YAML
parser applied to a clearly fenced code block, never a regex over prose) so
that ``tests/test_spec_compliance.py`` can detect drift between the two
files.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class SpecificationError(Exception):
    """Raised when the specification is missing, malformed, or incomplete.

    This is deliberately NOT a place to substitute a guessed value. Callers
    should let this propagate and stop geometry generation.
    """


def _find_repo_root(start: Path) -> Path:
    """Walk upward from ``start`` until a directory containing ``specs/`` is found."""
    for candidate in (start, *start.parents):
        if (candidate / "specs" / "parameters.yaml").exists():
            return candidate
    raise SpecificationError(
        "Could not locate 'specs/parameters.yaml' by walking up from "
        f"{start}. The repository layout is required for parameters.py to "
        "function."
    )


REPO_ROOT: Path = _find_repo_root(Path(__file__).resolve())
PARAMETERS_YAML_PATH: Path = REPO_ROOT / "specs" / "parameters.yaml"
SPEC_MD_PATH: Path = REPO_ROOT / "specs" / "spec.md"

_REQUIRED_PARAMETER_FIELDS = {"id", "name", "value", "unit", "tolerance", "description"}
_REQUIRED_PARAMETER_IDS = {
    "length",
    "width",
    "base_thickness",
    "hole_count",
    "hole_diameter",
    "hole_edge_offset",
    "fillet_radius",
    "material_density",
}


@dataclass(frozen=True)
class Parameter:
    """A single named, typed, toleranced value from the specification."""

    id: str
    name: str
    value: float
    unit: str
    tolerance: float
    description: str


def _validate_raw_document(doc: dict[str, Any], source: str) -> None:
    if not isinstance(doc, dict) or "project" not in doc or "parameters" not in doc:
        raise SpecificationError(
            f"{source}: expected top-level 'project' and 'parameters' keys."
        )
    if not isinstance(doc["parameters"], list) or not doc["parameters"]:
        raise SpecificationError(f"{source}: 'parameters' must be a non-empty list.")

    seen_ids: set[str] = set()
    for entry in doc["parameters"]:
        if not isinstance(entry, dict):
            raise SpecificationError(f"{source}: each parameter entry must be a mapping.")
        missing = _REQUIRED_PARAMETER_FIELDS - entry.keys()
        if missing:
            raise SpecificationError(
                f"{source}: parameter entry {entry!r} is missing required "
                f"field(s): {sorted(missing)}."
            )
        seen_ids.add(entry["id"])

    missing_ids = _REQUIRED_PARAMETER_IDS - seen_ids
    if missing_ids:
        raise SpecificationError(
            f"{source}: specification is missing required parameter id(s): "
            f"{sorted(missing_ids)}. Refusing to guess values for missing "
            "engineering parameters."
        )


def _load_yaml_document(text: str, source: str) -> dict[str, Any]:
    try:
        doc = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise SpecificationError(f"{source}: invalid YAML ({exc}).") from exc
    _validate_raw_document(doc, source)
    return doc


def load_parameters_yaml(path: Path = PARAMETERS_YAML_PATH) -> dict[str, Any]:
    """Load and validate ``specs/parameters.yaml``."""
    if not path.exists():
        raise SpecificationError(f"Machine parameter source not found: {path}")
    return _load_yaml_document(path.read_text(encoding="utf-8"), str(path))


def load_spec_md_parameters(path: Path = SPEC_MD_PATH) -> dict[str, Any]:
    """Extract the fenced ```yaml block from ``specs/spec.md`` and parse it.

    This intentionally does not parse the surrounding Markdown table with
    regular expressions. It only looks for a fenced code block tagged
    ``yaml`` (a stable, unambiguous delimiter) and hands the contents to a
    real YAML parser.
    """
    if not path.exists():
        raise SpecificationError(f"Human-readable specification not found: {path}")
    text = path.read_text(encoding="utf-8")
    fence = "```yaml"
    start = text.find(fence)
    if start == -1:
        raise SpecificationError(
            f"{path}: could not find a fenced ```yaml block containing the "
            "machine-readable parameter mirror."
        )
    start += len(fence)
    end = text.find("```", start)
    if end == -1:
        raise SpecificationError(f"{path}: fenced ```yaml block is not closed.")
    block = text[start:end]
    return _load_yaml_document(block, f"{path} (fenced yaml block)")


def _parameters_by_id(doc: dict[str, Any]) -> dict[str, Parameter]:
    result: dict[str, Parameter] = {}
    for entry in doc["parameters"]:
        result[entry["id"]] = Parameter(
            id=entry["id"],
            name=entry["name"],
            value=float(entry["value"]),
            unit=entry["unit"],
            tolerance=float(entry["tolerance"]),
            description=str(entry["description"]).strip(),
        )
    return result


_DOCUMENT: dict[str, Any] = load_parameters_yaml()
_PARAMETERS: dict[str, Parameter] = _parameters_by_id(_DOCUMENT)

# --- Project metadata -------------------------------------------------------
PROJECT_NAME: str = _DOCUMENT["project"]["name"]
MODEL_ID: str = _DOCUMENT["project"]["model_id"]
SPEC_VERSION: str = _DOCUMENT["project"]["spec_version"]
UNITS: str = _DOCUMENT["project"]["units"]

# --- Typed parameter accessors (the only place dimensions are named) -------
LENGTH_MM: float = _PARAMETERS["length"].value
WIDTH_MM: float = _PARAMETERS["width"].value
BASE_THICKNESS_MM: float = _PARAMETERS["base_thickness"].value
HOLE_COUNT: int = int(_PARAMETERS["hole_count"].value)
HOLE_DIAMETER_MM: float = _PARAMETERS["hole_diameter"].value
HOLE_EDGE_OFFSET_MM: float = _PARAMETERS["hole_edge_offset"].value
FILLET_RADIUS_MM: float = _PARAMETERS["fillet_radius"].value
MATERIAL_DENSITY_KG_MM3: float = _PARAMETERS["material_density"].value


def tolerance_for(parameter_id: str) -> float:
    """Return the specified tolerance for a parameter id, e.g. 'length'."""
    try:
        return _PARAMETERS[parameter_id].tolerance
    except KeyError as exc:
        raise SpecificationError(
            f"Unknown parameter id '{parameter_id}'. Known ids: "
            f"{sorted(_PARAMETERS)}."
        ) from exc


def all_parameters() -> dict[str, Parameter]:
    """Return all parameters keyed by technical id."""
    return dict(_PARAMETERS)


def check_engineering_preconditions() -> None:
    """Fail fast if the declared parameters are geometrically inconsistent.

    This is a specification-consistency check, not a geometry check: it
    verifies the numbers declared in ``specs/parameters.yaml`` do not
    contradict each other, *before* any Build123d call is made. Per project
    policy, inconsistencies must stop generation rather than be silently
    "fixed" by guessing.
    """
    hole_radius = HOLE_DIAMETER_MM / 2
    if hole_radius >= HOLE_EDGE_OFFSET_MM:
        raise SpecificationError(
            "Inconsistent specification: hole_edge_offset "
            f"({HOLE_EDGE_OFFSET_MM} mm) must be greater than the hole "
            f"radius ({hole_radius} mm), otherwise a mounting hole would "
            "extend past the edge of the base."
        )
    if HOLE_EDGE_OFFSET_MM - hole_radius <= FILLET_RADIUS_MM:
        raise SpecificationError(
            "Inconsistent specification: hole_edge_offset - hole_radius "
            f"({HOLE_EDGE_OFFSET_MM - hole_radius} mm) must be strictly "
            f"greater than fillet_radius ({FILLET_RADIUS_MM} mm), otherwise "
            "a mounting hole would intersect the rounded corner."
        )
    if 2 * HOLE_EDGE_OFFSET_MM >= LENGTH_MM or 2 * HOLE_EDGE_OFFSET_MM >= WIDTH_MM:
        raise SpecificationError(
            "Inconsistent specification: hole_edge_offset "
            f"({HOLE_EDGE_OFFSET_MM} mm) is too large for the base "
            f"dimensions ({LENGTH_MM} x {WIDTH_MM} mm) — the four holes "
            "would overlap or fall outside the base."
        )
    if HOLE_COUNT != 4:
        raise SpecificationError(
            f"This model implementation only supports hole_count == 4 "
            f"(one per corner); specification declares {HOLE_COUNT}. "
            "Update src/cad_project/model.py deliberately if the hole "
            "layout requirement has changed."
        )
