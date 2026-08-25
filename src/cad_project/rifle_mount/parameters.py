"""Single source of truth for all numeric parameters of the rifle mount.

Mirrors the pattern in ``cad_project.parameters`` (the mounting bracket):
all numeric values come from ``specs/rifle-mount/parameters.yaml``, loaded
once at import time. See that module's docstring for the rationale; kept
as a separate, self-contained loader here (rather than a shared import)
so the existing bracket model stays untouched.
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
        if (candidate / "specs" / "rifle-mount" / "parameters.yaml").exists():
            return candidate
    raise SpecificationError(
        "Could not locate 'specs/rifle-mount/parameters.yaml' by walking up "
        f"from {start}."
    )


REPO_ROOT: Path = _find_repo_root(Path(__file__).resolve())
PARAMETERS_YAML_PATH: Path = REPO_ROOT / "specs" / "rifle-mount" / "parameters.yaml"
SPEC_MD_PATH: Path = REPO_ROOT / "specs" / "rifle-mount" / "spec.md"

_REQUIRED_PARAMETER_FIELDS = {"id", "name", "value", "unit", "tolerance", "description"}
_REQUIRED_PARAMETER_IDS = {
    "wall_to_barrel_center_min",
    "wall_to_barrel_center_max",
    "barrel_diameter_reference",
    "magnet_pocket_length",
    "magnet_pocket_width",
    "magnet_thickness",
    "magnet_count",
    "magnet_pocket_wall_thickness",
    "mounting_plate_size",
    "mounting_plate_thickness",
    "magnet_center_offset_y",
    "plate_corner_fillet_radius",
    "thread_pitch",
    "thread_major_diameter",
    "thread_angle_deg",
    "thread_engagement_length",
    "nut_wall_thickness",
    "nut_boss_length",
    "rod_threaded_length",
    "collar_length",
    "collar_diameter",
    "cradle_transition_height",
    "cradle_corner_fillet_radius",
    "u_internal_width",
    "u_arm_length",
    "u_arm_height",
    "u_wall_thickness",
    "liner_groove_width",
    "liner_groove_depth",
    "material_density",
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

WALL_TO_BARREL_CENTER_MIN_MM: float = _PARAMETERS["wall_to_barrel_center_min"].value
WALL_TO_BARREL_CENTER_MAX_MM: float = _PARAMETERS["wall_to_barrel_center_max"].value
BARREL_DIAMETER_REFERENCE_MM: float = _PARAMETERS["barrel_diameter_reference"].value
MAGNET_POCKET_LENGTH_MM: float = _PARAMETERS["magnet_pocket_length"].value
MAGNET_POCKET_WIDTH_MM: float = _PARAMETERS["magnet_pocket_width"].value
MAGNET_THICKNESS_MM: float = _PARAMETERS["magnet_thickness"].value
MAGNET_COUNT: int = int(_PARAMETERS["magnet_count"].value)
MAGNET_POCKET_WALL_THICKNESS_MM: float = _PARAMETERS["magnet_pocket_wall_thickness"].value
MOUNTING_PLATE_SIZE_MM: float = _PARAMETERS["mounting_plate_size"].value
MOUNTING_PLATE_THICKNESS_MM: float = _PARAMETERS["mounting_plate_thickness"].value
MAGNET_CENTER_OFFSET_Y_MM: float = _PARAMETERS["magnet_center_offset_y"].value
PLATE_CORNER_FILLET_RADIUS_MM: float = _PARAMETERS["plate_corner_fillet_radius"].value
THREAD_PITCH_MM: float = _PARAMETERS["thread_pitch"].value
THREAD_MAJOR_DIAMETER_MM: float = _PARAMETERS["thread_major_diameter"].value
THREAD_ANGLE_DEG: float = _PARAMETERS["thread_angle_deg"].value
THREAD_ENGAGEMENT_LENGTH_MM: float = _PARAMETERS["thread_engagement_length"].value
NUT_WALL_THICKNESS_MM: float = _PARAMETERS["nut_wall_thickness"].value
NUT_BOSS_LENGTH_MM: float = _PARAMETERS["nut_boss_length"].value
ROD_THREADED_LENGTH_MM: float = _PARAMETERS["rod_threaded_length"].value
COLLAR_LENGTH_MM: float = _PARAMETERS["collar_length"].value
COLLAR_DIAMETER_MM: float = _PARAMETERS["collar_diameter"].value
CRADLE_TRANSITION_HEIGHT_MM: float = _PARAMETERS["cradle_transition_height"].value
CRADLE_CORNER_FILLET_RADIUS_MM: float = _PARAMETERS["cradle_corner_fillet_radius"].value
U_INTERNAL_WIDTH_MM: float = _PARAMETERS["u_internal_width"].value
U_ARM_LENGTH_MM: float = _PARAMETERS["u_arm_length"].value
U_ARM_HEIGHT_MM: float = _PARAMETERS["u_arm_height"].value
U_WALL_THICKNESS_MM: float = _PARAMETERS["u_wall_thickness"].value
LINER_GROOVE_WIDTH_MM: float = _PARAMETERS["liner_groove_width"].value
LINER_GROOVE_DEPTH_MM: float = _PARAMETERS["liner_groove_depth"].value
MATERIAL_DENSITY_KG_MM3: float = _PARAMETERS["material_density"].value

# Derived: nut/boss outer diameter (thread major diameter + wall on both sides).
NUT_BOSS_OUTER_DIAMETER_MM: float = THREAD_MAJOR_DIAMETER_MM + 2 * NUT_WALL_THICKNESS_MM


def tolerance_for(parameter_id: str) -> float:
    try:
        return _PARAMETERS[parameter_id].tolerance
    except KeyError as exc:
        raise SpecificationError(
            f"Unknown parameter id '{parameter_id}'. Known ids: {sorted(_PARAMETERS)}."
        ) from exc


def all_parameters() -> dict[str, Parameter]:
    return dict(_PARAMETERS)


def check_engineering_preconditions() -> None:
    """Fail fast if the declared parameters are geometrically inconsistent.

    See specs/rifle-mount/decisions.md for the derivation these checks
    encode (fixed-offset calculation, thread-engagement math).
    """
    if abs(MOUNTING_PLATE_THICKNESS_MM - (MAGNET_THICKNESS_MM + MAGNET_POCKET_WALL_THICKNESS_MM)) > 1e-9:
        raise SpecificationError(
            "Inconsistent specification: mounting_plate_thickness "
            f"({MOUNTING_PLATE_THICKNESS_MM} mm) must equal magnet_thickness + "
            f"magnet_pocket_wall_thickness ({MAGNET_THICKNESS_MM + MAGNET_POCKET_WALL_THICKNESS_MM} mm)."
        )

    # v3: two rectangular pockets, centered in X (x=0), symmetric in Y at
    # +-magnet_center_offset_y — see specs/rifle-mount/decisions.md
    # ("v3 - paski magnetyczne zamiast dysków").
    half_length = MAGNET_POCKET_LENGTH_MM / 2
    half_width = MAGNET_POCKET_WIDTH_MM / 2
    if half_width >= MAGNET_CENTER_OFFSET_Y_MM:
        raise SpecificationError(
            "Inconsistent specification: magnet_center_offset_y "
            f"({MAGNET_CENTER_OFFSET_Y_MM} mm) must be greater than half the pocket width "
            f"({half_width} mm), otherwise the two symmetric pockets would overlap."
        )
    if half_length >= MOUNTING_PLATE_SIZE_MM / 2:
        raise SpecificationError(
            "Inconsistent specification: magnet_pocket_length "
            f"({MAGNET_POCKET_LENGTH_MM} mm) does not fit within mounting_plate_size "
            f"({MOUNTING_PLATE_SIZE_MM} mm)."
        )
    if MAGNET_CENTER_OFFSET_Y_MM + half_width >= MOUNTING_PLATE_SIZE_MM / 2:
        raise SpecificationError(
            "Inconsistent specification: a magnet pocket (center_offset_y "
            f"{MAGNET_CENTER_OFFSET_Y_MM} mm + half width {half_width} mm) would extend "
            f"past the plate edge (mounting_plate_size/2 = {MOUNTING_PLATE_SIZE_MM / 2} mm)."
        )

    nearest_pocket_edge = MAGNET_CENTER_OFFSET_Y_MM - half_width
    if nearest_pocket_edge <= NUT_BOSS_OUTER_DIAMETER_MM / 2:
        raise SpecificationError(
            "Inconsistent specification: magnet pockets would collide with the "
            f"threaded nut boss (nearest pocket edge {nearest_pocket_edge:.2f} mm from "
            f"axis <= boss radius {NUT_BOSS_OUTER_DIAMETER_MM / 2} mm). Increase "
            "mounting_plate_size/magnet_center_offset_y or reduce nut_wall_thickness."
        )

    if COLLAR_DIAMETER_MM <= THREAD_MAJOR_DIAMETER_MM:
        raise SpecificationError(
            f"Inconsistent specification: collar_diameter ({COLLAR_DIAMETER_MM} mm) must be "
            f"greater than thread_major_diameter ({THREAD_MAJOR_DIAMETER_MM} mm), otherwise it "
            "cannot act as a stop against the nut boss face."
        )
    if COLLAR_DIAMETER_MM >= NUT_BOSS_OUTER_DIAMETER_MM:
        raise SpecificationError(
            f"Inconsistent specification: collar_diameter ({COLLAR_DIAMETER_MM} mm) must be "
            f"smaller than the nut boss outer diameter ({NUT_BOSS_OUTER_DIAMETER_MM} mm), "
            "otherwise it cannot seat against the boss face."
        )

    if U_INTERNAL_WIDTH_MM <= BARREL_DIAMETER_REFERENCE_MM:
        raise SpecificationError(
            f"Inconsistent specification: u_internal_width ({U_INTERNAL_WIDTH_MM} mm) must be "
            f"greater than barrel_diameter_reference ({BARREL_DIAMETER_REFERENCE_MM} mm) to allow "
            "the barrel to slide in freely."
        )

    # The C cradle's symmetric clearance (u_internal_width) now runs along
    # the axis perpendicular to both the rod and the barrel, centered on
    # X=0 by construction (see model.py) — coaxiality with the thread axis
    # no longer depends on any parameter value, unlike the old U shape
    # (which needed u_arm_height tuned to a specific number for this — see
    # specs/rifle-mount/decisions.md, "U cradle coaxial alignment fix").
    # See "U -> C cradle reorientation" in decisions.md for why this check
    # was removed rather than reformulated.

    if LINER_GROOVE_DEPTH_MM >= U_WALL_THICKNESS_MM:
        raise SpecificationError(
            f"Inconsistent specification: liner_groove_depth ({LINER_GROOVE_DEPTH_MM} mm) must be "
            f"smaller than u_wall_thickness ({U_WALL_THICKNESS_MM} mm)."
        )

    # v2: the C-cradle block's outer footprint (see model.py) is a
    # rectangle u_block_x_extent x u_arm_length with its 4 vertical edges
    # rounded by cradle_corner_fillet_radius. A box fillet radius must stay
    # strictly below half of either adjacent face dimension, or the fillet
    # is geometrically impossible - see specs/rifle-mount/decisions.md
    # ("v2 - łagodne przejście C/gwint").
    u_block_x_extent = 2 * U_WALL_THICKNESS_MM + U_INTERNAL_WIDTH_MM
    half_x = u_block_x_extent / 2
    half_y = U_ARM_LENGTH_MM / 2
    if min(half_x, half_y) <= CRADLE_CORNER_FILLET_RADIUS_MM:
        raise SpecificationError(
            "Inconsistent specification: cradle_corner_fillet_radius "
            f"({CRADLE_CORNER_FILLET_RADIUS_MM} mm) must be smaller than half of the "
            f"C-cradle block's shorter footprint dimension ({min(half_x, half_y)} mm), "
            "otherwise the corner fillet is geometrically impossible."
        )

    # v2: the smooth loft transition between the collar and the (rounded)
    # C-cradle block must stay within the standard FDM self-supporting
    # overhang angle (45 deg from vertical), so the arm prints without
    # support material - see specs/rifle-mount/decisions.md ("v2 - łagodne
    # przejście C/gwint"). The worst case is the block's rounded corner,
    # at distance hypot(half_x - r, half_y - r) + r from the axis; this
    # analytic formula is a conservative (slightly larger) upper bound on
    # the actual lofted geometry, confirmed by direct measurement of the
    # built solid (measured ~21.0mm vs ~21.24mm analytic here).
    max_cradle_radial_extent = (
        math.hypot(
            half_x - CRADLE_CORNER_FILLET_RADIUS_MM,
            half_y - CRADLE_CORNER_FILLET_RADIUS_MM,
        )
        + CRADLE_CORNER_FILLET_RADIUS_MM
    )
    transition_overhang = max_cradle_radial_extent - COLLAR_DIAMETER_MM / 2
    if transition_overhang > 0:
        transition_angle_deg = math.degrees(
            math.atan(transition_overhang / CRADLE_TRANSITION_HEIGHT_MM)
        )
        if transition_angle_deg > 45.0:
            raise SpecificationError(
                "Inconsistent specification: the collar -> C-cradle transition overhang "
                f"angle ({transition_angle_deg:.1f} deg) exceeds the 45 deg self-supporting "
                "threshold for FDM printing without support material. Increase "
                "cradle_transition_height, increase collar_diameter, or decrease the "
                "C-cradle block's footprint/fillet radius."
            )

    # The C cradle's barrel rests against its back wall (adjacent to the
    # collar), so the barrel's center sits at u_wall_thickness (back wall)
    # + barrel_diameter_reference/2 past the start of the cradle block. See
    # specs/rifle-mount/decisions.md ("U -> C cradle reorientation") — this
    # must match src/cad_project/rifle_mount/model.py's u_gap_z_start
    # exactly. v2 adds cradle_transition_height as a new fixed (non-adjustable)
    # component - see decisions.md ("v2 - łagodne przejście C/gwint").
    fixed_offset = (
        MOUNTING_PLATE_THICKNESS_MM
        + NUT_BOSS_LENGTH_MM
        + COLLAR_LENGTH_MM
        + CRADLE_TRANSITION_HEIGHT_MM
        + U_WALL_THICKNESS_MM
        + BARREL_DIAMETER_REFERENCE_MM / 2
    )
    exposed_min = WALL_TO_BARREL_CENTER_MIN_MM - fixed_offset
    exposed_max = WALL_TO_BARREL_CENTER_MAX_MM - fixed_offset

    if exposed_min <= 0:
        raise SpecificationError(
            "Inconsistent specification: wall_to_barrel_center_min "
            f"({WALL_TO_BARREL_CENTER_MIN_MM} mm) is too small for the fixed assembly offset "
            f"({fixed_offset} mm) — the rod would need negative exposed length."
        )
    if exposed_max + THREAD_ENGAGEMENT_LENGTH_MM > ROD_THREADED_LENGTH_MM:
        raise SpecificationError(
            "Inconsistent specification: rod_threaded_length "
            f"({ROD_THREADED_LENGTH_MM} mm) is too short to maintain "
            f"thread_engagement_length ({THREAD_ENGAGEMENT_LENGTH_MM} mm) at maximum extension "
            f"(requires >= {exposed_max + THREAD_ENGAGEMENT_LENGTH_MM} mm)."
        )
