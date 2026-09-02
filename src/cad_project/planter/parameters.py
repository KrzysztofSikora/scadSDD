"""Single source of truth for all numeric parameters of the planter.

Mirrors the pattern in ``cad_project.rifle_mount.parameters`` (see that
module's docstring for the rationale): all numeric values come from
``specs/planter/parameters.yaml``, loaded once at import time.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from cad_project.parameters import SpecificationError


def _find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "specs" / "planter" / "parameters.yaml").exists():
            return candidate
    raise SpecificationError(
        "Could not locate 'specs/planter/parameters.yaml' by walking up "
        f"from {start}."
    )


REPO_ROOT: Path = _find_repo_root(Path(__file__).resolve())
PARAMETERS_YAML_PATH: Path = REPO_ROOT / "specs" / "planter" / "parameters.yaml"
SPEC_MD_PATH: Path = REPO_ROOT / "specs" / "planter" / "spec.md"

_REQUIRED_PARAMETER_FIELDS = {"id", "name", "value", "unit", "tolerance", "description"}
_REQUIRED_PARAMETER_IDS = {
    "insert_top_outer_diameter",
    "insert_bottom_outer_diameter",
    "insert_body_height",
    "insert_wall_thickness",
    "insert_floor_thickness",
    "top_rim_fillet_radius",
    "drainage_hole_diameter",
    "drainage_hole_count",
    "drainage_hole_circle_diameter",
    "spigot_height",
    "fit_clearance",
    "capillary_tube_outer_diameter",
    "capillary_tube_inner_diameter",
    "capillary_tube_soil_protrusion",
    "capillary_tube_slot_width",
    "capillary_tube_slot_count",
    "capillary_tube_reservoir_clearance",
    "reservoir_mouth_inner_diameter",
    "reservoir_wall_thickness",
    "reservoir_cavity_depth",
    "reservoir_foot_height",
    "reservoir_foot_diameter",
    "reservoir_foot_count",
    "fill_spout_outer_diameter",
    "fill_spout_inner_diameter",
    "fill_spout_top_protrusion",
    "fill_spout_bottom_clearance",
    "overflow_hole_diameter",
    "overflow_hole_height_from_floor",
    "material_density",
    "pattern_flute_count",
    "pattern_flute_depth",
    "pattern_flute_width_deg",
    "pattern_flute_end_margin",
}


@dataclass(frozen=True)
class Parameter:
    id: str
    name: str
    value: float
    unit: str
    tolerance: float
    description: str


def _validate_raw_document(doc: dict[str, Any], source: str) -> None:
    if not isinstance(doc, dict) or "project" not in doc or "parameters" not in doc:
        raise SpecificationError(f"{source}: expected top-level 'project' and 'parameters' keys.")
    if not isinstance(doc["parameters"], list) or not doc["parameters"]:
        raise SpecificationError(f"{source}: 'parameters' must be a non-empty list.")

    seen_ids: set[str] = set()
    for entry in doc["parameters"]:
        if not isinstance(entry, dict):
            raise SpecificationError(f"{source}: each parameter entry must be a mapping.")
        missing = _REQUIRED_PARAMETER_FIELDS - entry.keys()
        if missing:
            raise SpecificationError(
                f"{source}: parameter entry {entry!r} is missing required field(s): "
                f"{sorted(missing)}."
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
    if not path.exists():
        raise SpecificationError(f"Machine parameter source not found: {path}")
    return _load_yaml_document(path.read_text(encoding="utf-8"), str(path))


def load_spec_md_parameters(path: Path = SPEC_MD_PATH) -> dict[str, Any]:
    if not path.exists():
        raise SpecificationError(f"Human-readable specification not found: {path}")
    text = path.read_text(encoding="utf-8")
    fence = "```yaml"
    start = text.find(fence)
    if start == -1:
        raise SpecificationError(
            f"{path}: could not find a fenced ```yaml block with the machine parameter mirror."
        )
    start += len(fence)
    end = text.find("```", start)
    if end == -1:
        raise SpecificationError(f"{path}: fenced ```yaml block is not closed.")
    return _load_yaml_document(text[start:end], f"{path} (fenced yaml block)")


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

PROJECT_NAME: str = _DOCUMENT["project"]["name"]
MODEL_ID: str = _DOCUMENT["project"]["model_id"]
SPEC_VERSION: str = _DOCUMENT["project"]["spec_version"]
UNITS: str = _DOCUMENT["project"]["units"]

INSERT_TOP_OUTER_DIAMETER_MM: float = _PARAMETERS["insert_top_outer_diameter"].value
INSERT_BOTTOM_OUTER_DIAMETER_MM: float = _PARAMETERS["insert_bottom_outer_diameter"].value
INSERT_BODY_HEIGHT_MM: float = _PARAMETERS["insert_body_height"].value
INSERT_WALL_THICKNESS_MM: float = _PARAMETERS["insert_wall_thickness"].value
INSERT_FLOOR_THICKNESS_MM: float = _PARAMETERS["insert_floor_thickness"].value
TOP_RIM_FILLET_RADIUS_MM: float = _PARAMETERS["top_rim_fillet_radius"].value
DRAINAGE_HOLE_DIAMETER_MM: float = _PARAMETERS["drainage_hole_diameter"].value
DRAINAGE_HOLE_COUNT: int = int(_PARAMETERS["drainage_hole_count"].value)
DRAINAGE_HOLE_CIRCLE_DIAMETER_MM: float = _PARAMETERS["drainage_hole_circle_diameter"].value
SPIGOT_HEIGHT_MM: float = _PARAMETERS["spigot_height"].value
FIT_CLEARANCE_MM: float = _PARAMETERS["fit_clearance"].value

CAPILLARY_TUBE_OUTER_DIAMETER_MM: float = _PARAMETERS["capillary_tube_outer_diameter"].value
CAPILLARY_TUBE_INNER_DIAMETER_MM: float = _PARAMETERS["capillary_tube_inner_diameter"].value
CAPILLARY_TUBE_SOIL_PROTRUSION_MM: float = _PARAMETERS["capillary_tube_soil_protrusion"].value
CAPILLARY_TUBE_SLOT_WIDTH_MM: float = _PARAMETERS["capillary_tube_slot_width"].value
CAPILLARY_TUBE_SLOT_COUNT: int = int(_PARAMETERS["capillary_tube_slot_count"].value)
CAPILLARY_TUBE_RESERVOIR_CLEARANCE_MM: float = _PARAMETERS["capillary_tube_reservoir_clearance"].value

RESERVOIR_MOUTH_INNER_DIAMETER_MM: float = _PARAMETERS["reservoir_mouth_inner_diameter"].value
RESERVOIR_WALL_THICKNESS_MM: float = _PARAMETERS["reservoir_wall_thickness"].value
RESERVOIR_CAVITY_DEPTH_MM: float = _PARAMETERS["reservoir_cavity_depth"].value
RESERVOIR_FOOT_HEIGHT_MM: float = _PARAMETERS["reservoir_foot_height"].value
RESERVOIR_FOOT_DIAMETER_MM: float = _PARAMETERS["reservoir_foot_diameter"].value
RESERVOIR_FOOT_COUNT: int = int(_PARAMETERS["reservoir_foot_count"].value)

FILL_SPOUT_OUTER_DIAMETER_MM: float = _PARAMETERS["fill_spout_outer_diameter"].value
FILL_SPOUT_INNER_DIAMETER_MM: float = _PARAMETERS["fill_spout_inner_diameter"].value
FILL_SPOUT_TOP_PROTRUSION_MM: float = _PARAMETERS["fill_spout_top_protrusion"].value
FILL_SPOUT_BOTTOM_CLEARANCE_MM: float = _PARAMETERS["fill_spout_bottom_clearance"].value

OVERFLOW_HOLE_DIAMETER_MM: float = _PARAMETERS["overflow_hole_diameter"].value
OVERFLOW_HOLE_HEIGHT_FROM_FLOOR_MM: float = _PARAMETERS["overflow_hole_height_from_floor"].value

MATERIAL_DENSITY_KG_MM3: float = _PARAMETERS["material_density"].value

PATTERN_FLUTE_COUNT: int = int(_PARAMETERS["pattern_flute_count"].value)
PATTERN_FLUTE_DEPTH_MM: float = _PARAMETERS["pattern_flute_depth"].value
PATTERN_FLUTE_WIDTH_DEG: float = _PARAMETERS["pattern_flute_width_deg"].value
PATTERN_FLUTE_END_MARGIN_MM: float = _PARAMETERS["pattern_flute_end_margin"].value

# Derived: spigot OD is set by the reservoir mouth it must slip-fit into.
SPIGOT_OUTER_DIAMETER_MM: float = RESERVOIR_MOUTH_INNER_DIAMETER_MM - 2 * FIT_CLEARANCE_MM
# Derived: reservoir outer diameter, from its inner diameter + wall.
RESERVOIR_MOUTH_OUTER_DIAMETER_MM: float = (
    RESERVOIR_MOUTH_INNER_DIAMETER_MM + 2 * RESERVOIR_WALL_THICKNESS_MM
)


def tolerance_for(parameter_id: str) -> float:
    try:
        return _PARAMETERS[parameter_id].tolerance
    except KeyError as exc:
        raise SpecificationError(
            f"Unknown parameter id '{parameter_id}'. Known ids: {sorted(_PARAMETERS)}."
        ) from exc


def all_parameters() -> dict[str, Parameter]:
    return dict(_PARAMETERS)


def insert_outer_radius_at(z_mm: float) -> float:
    """Insert's outer radius at height ``z_mm`` above the resting plane (Z=0).

    Linear interpolation between the bottom (Z=0) and top (Z=insert_body_height)
    outer radii — matches the ``Cone`` taper built in model.py.
    """
    bottom_r = INSERT_BOTTOM_OUTER_DIAMETER_MM / 2
    top_r = INSERT_TOP_OUTER_DIAMETER_MM / 2
    taper_rate = (top_r - bottom_r) / INSERT_BODY_HEIGHT_MM
    return bottom_r + taper_rate * z_mm


def check_engineering_preconditions() -> None:
    """Fail fast if the declared parameters are geometrically inconsistent.

    See specs/planter/decisions.md for the derivation these checks encode
    (spigot/reservoir fit, spout/insert clearance, capillary tube extents).
    """
    if INSERT_FLOOR_THICKNESS_MM < INSERT_WALL_THICKNESS_MM:
        raise SpecificationError(
            "Inconsistent specification: insert_floor_thickness "
            f"({INSERT_FLOOR_THICKNESS_MM} mm) must be >= insert_wall_thickness "
            f"({INSERT_WALL_THICKNESS_MM} mm) — the floor is built by thickening the "
            "shell's uniform-thickness base, never thinning it."
        )

    if PATTERN_FLUTE_DEPTH_MM >= INSERT_WALL_THICKNESS_MM - 0.5:
        raise SpecificationError(
            "Inconsistent specification: pattern_flute_depth "
            f"({PATTERN_FLUTE_DEPTH_MM} mm) leaves less than 0.5mm of wall at the flute "
            f"bottom (insert_wall_thickness = {INSERT_WALL_THICKNESS_MM} mm) — the outer "
            "wall pattern must never breach into the soil cavity."
        )

    if TOP_RIM_FILLET_RADIUS_MM >= INSERT_WALL_THICKNESS_MM:
        raise SpecificationError(
            "Inconsistent specification: top_rim_fillet_radius "
            f"({TOP_RIM_FILLET_RADIUS_MM} mm) must be smaller than insert_wall_thickness "
            f"({INSERT_WALL_THICKNESS_MM} mm) — only the outer top edge is filleted (see "
            "model.py), and OCCT cannot fillet it past the wall's own thickness."
        )

    if 2 * PATTERN_FLUTE_END_MARGIN_MM >= INSERT_BODY_HEIGHT_MM:
        raise SpecificationError(
            "Inconsistent specification: pattern_flute_end_margin "
            f"({PATTERN_FLUTE_END_MARGIN_MM} mm) x 2 >= insert_body_height "
            f"({INSERT_BODY_HEIGHT_MM} mm) — no room left for the flutes themselves."
        )

    if PATTERN_FLUTE_WIDTH_DEG * PATTERN_FLUTE_COUNT >= 360.0:
        raise SpecificationError(
            "Inconsistent specification: pattern_flute_width_deg "
            f"({PATTERN_FLUTE_WIDTH_DEG} deg) x pattern_flute_count ({PATTERN_FLUTE_COUNT}) "
            f">= 360 deg — adjacent flutes would overlap/merge."
        )

    if SPIGOT_OUTER_DIAMETER_MM <= 0:
        raise SpecificationError(
            "Inconsistent specification: reservoir_mouth_inner_diameter "
            f"({RESERVOIR_MOUTH_INNER_DIAMETER_MM} mm) is too small for fit_clearance "
            f"({FIT_CLEARANCE_MM} mm) on each side — derived spigot_outer_diameter is "
            f"<= 0 ({SPIGOT_OUTER_DIAMETER_MM} mm)."
        )

    spigot_margin = (INSERT_BOTTOM_OUTER_DIAMETER_MM - SPIGOT_OUTER_DIAMETER_MM) / 2
    if spigot_margin <= 2.0:
        raise SpecificationError(
            "Inconsistent specification: the resting ring between the insert's spigot "
            f"(derived OD {SPIGOT_OUTER_DIAMETER_MM:.2f} mm) and its bottom outer edge "
            f"(insert_bottom_outer_diameter = {INSERT_BOTTOM_OUTER_DIAMETER_MM} mm) is only "
            f"{spigot_margin:.2f} mm wide (need > 2mm) — increase insert_bottom_outer_diameter "
            "or reduce reservoir_mouth_inner_diameter."
        )

    overhang_margin = (INSERT_BOTTOM_OUTER_DIAMETER_MM - RESERVOIR_MOUTH_OUTER_DIAMETER_MM) / 2
    if overhang_margin <= 2.0:
        raise SpecificationError(
            "Inconsistent specification: the insert's bottom edge "
            f"(insert_bottom_outer_diameter = {INSERT_BOTTOM_OUTER_DIAMETER_MM} mm) overhangs "
            f"the reservoir's rim (derived OD {RESERVOIR_MOUTH_OUTER_DIAMETER_MM:.2f} mm) by "
            f"only {overhang_margin:.2f} mm (need > 2mm) — the seam would not be hidden."
        )

    if CAPILLARY_TUBE_INNER_DIAMETER_MM >= CAPILLARY_TUBE_OUTER_DIAMETER_MM:
        raise SpecificationError(
            "Inconsistent specification: capillary_tube_inner_diameter "
            f"({CAPILLARY_TUBE_INNER_DIAMETER_MM} mm) must be smaller than "
            f"capillary_tube_outer_diameter ({CAPILLARY_TUBE_OUTER_DIAMETER_MM} mm)."
        )

    slot_span = CAPILLARY_TUBE_SLOT_COUNT * CAPILLARY_TUBE_SLOT_WIDTH_MM
    max_span = 0.6 * math.pi * CAPILLARY_TUBE_OUTER_DIAMETER_MM
    if slot_span >= max_span:
        raise SpecificationError(
            "Inconsistent specification: capillary_tube_slot_count x "
            f"capillary_tube_slot_width ({slot_span:.1f} mm) would remove too much of the "
            f"tube's circumference (>= {max_span:.1f} mm, 60% of {CAPILLARY_TUBE_OUTER_DIAMETER_MM} mm "
            "OD circumference) — the ribs between slots would be too thin/absent."
        )

    if CAPILLARY_TUBE_RESERVOIR_CLEARANCE_MM >= RESERVOIR_CAVITY_DEPTH_MM - SPIGOT_HEIGHT_MM:
        raise SpecificationError(
            "Inconsistent specification: capillary_tube_reservoir_clearance "
            f"({CAPILLARY_TUBE_RESERVOIR_CLEARANCE_MM} mm) must be smaller than "
            f"reservoir_cavity_depth - spigot_height "
            f"({RESERVOIR_CAVITY_DEPTH_MM - SPIGOT_HEIGHT_MM} mm), otherwise the capillary "
            "tube would not reach past the spigot's own submerged length."
        )

    if FILL_SPOUT_BOTTOM_CLEARANCE_MM >= RESERVOIR_CAVITY_DEPTH_MM:
        raise SpecificationError(
            "Inconsistent specification: fill_spout_bottom_clearance "
            f"({FILL_SPOUT_BOTTOM_CLEARANCE_MM} mm) must be smaller than "
            f"reservoir_cavity_depth ({RESERVOIR_CAVITY_DEPTH_MM} mm)."
        )

    overflow_low = OVERFLOW_HOLE_HEIGHT_FROM_FLOOR_MM - OVERFLOW_HOLE_DIAMETER_MM / 2
    overflow_high = OVERFLOW_HOLE_HEIGHT_FROM_FLOOR_MM + OVERFLOW_HOLE_DIAMETER_MM / 2
    if overflow_low <= 0:
        raise SpecificationError(
            "Inconsistent specification: overflow_hole_height_from_floor "
            f"({OVERFLOW_HOLE_HEIGHT_FROM_FLOOR_MM} mm) minus half its diameter is <= 0 — "
            "the overflow hole would breach the reservoir's floor."
        )
    if overflow_high >= RESERVOIR_CAVITY_DEPTH_MM - SPIGOT_HEIGHT_MM:
        raise SpecificationError(
            "Inconsistent specification: the overflow hole (top edge at "
            f"{overflow_high:.1f} mm from the reservoir floor) would collide with the "
            f"spigot's insertion zone (top {SPIGOT_HEIGHT_MM} mm of the "
            f"{RESERVOIR_CAVITY_DEPTH_MM} mm cavity) — lower overflow_hole_height_from_floor "
            "or increase reservoir_cavity_depth."
        )

    # Fill spout / insert wall clearance. The spout is mounted flush against
    # the reservoir's outer wall (axis at reservoir_mouth_outer_diameter/2)
    # and must clear the insert's outer surface at every height it spans
    # (Z=0 up to fill_spout_top_protrusion). Since the insert's outer
    # radius only grows with Z (see insert_outer_radius_at), Z=0 is the
    # worst case as long as the taper is non-negative.
    if INSERT_TOP_OUTER_DIAMETER_MM < INSERT_BOTTOM_OUTER_DIAMETER_MM:
        raise SpecificationError(
            "Inconsistent specification: insert_top_outer_diameter "
            f"({INSERT_TOP_OUTER_DIAMETER_MM} mm) must be >= insert_bottom_outer_diameter "
            f"({INSERT_BOTTOM_OUTER_DIAMETER_MM} mm) — the fill-spout clearance check below "
            "assumes the insert never narrows going up."
        )
    spout_max_reach = RESERVOIR_MOUTH_OUTER_DIAMETER_MM / 2 + FILL_SPOUT_OUTER_DIAMETER_MM / 2
    spout_clearance = INSERT_BOTTOM_OUTER_DIAMETER_MM / 2 - spout_max_reach
    if spout_clearance <= 2.0:
        raise SpecificationError(
            "Inconsistent specification: the fill spout (mounted at radius "
            f"{RESERVOIR_MOUTH_OUTER_DIAMETER_MM / 2:.1f} mm, reaching out to "
            f"{spout_max_reach:.1f} mm) clears the insert's bottom edge (radius "
            f"{INSERT_BOTTOM_OUTER_DIAMETER_MM / 2:.1f} mm) by only "
            f"{spout_clearance:.2f} mm (need > 2mm) — increase insert_bottom_outer_diameter "
            "or reduce fill_spout_outer_diameter/reservoir_mouth_inner_diameter."
        )
