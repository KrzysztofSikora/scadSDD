"""Parametric Build123d geometry for the premium self-watering planter.

Two independent parts, matching the physical, hand-assembled product:

* **Insert** ("wkład") — tapered pot that holds the soil, with a fluted
  outer wall (the one part of the geometry meant to change between future
  variants — see ``_carve_wall_pattern`` and
  ``specs/planter/decisions.md``, "Architektura wymiennego wzoru"), a
  perforated capillary tube hanging from its floor, and a positioning
  skirt that slips into the reservoir's mouth.
* **Reservoir** ("zbiornik") — water tray the insert rests on/in, with an
  external fill spout (pour water without removing the insert) and an
  overflow hole that caps the maximum water level.

Building never exports or writes any file — see ``specs/planter/spec.md``
("Geometria") for the operation order.  Like ``cad_project.model`` and
``cad_project.rifle_mount.model``, every nested ``BuildPart``/``BuildSketch``
context lives in this module's own functions, in the same Python stack
frame as its parent — Build123d's builders only link a child to its
parent when both are entered in the same frame.
"""

from __future__ import annotations

from dataclasses import dataclass

from build123d import (
    Align,
    Axis,
    Box,
    BuildPart,
    Cone,
    Cylinder,
    Location,
    Locations,
    Mode,
    Part,
    PolarLocations,
    SortBy,
    fillet,
    offset,
)

from cad_project.planter import parameters as p


@dataclass(frozen=True)
class InsertFeatures:
    top_outer_diameter_mm: float
    bottom_outer_diameter_mm: float
    body_height_mm: float
    wall_thickness_mm: float
    drainage_hole_count: int
    capillary_tube_outer_diameter_mm: float
    pattern_flute_count: int


@dataclass(frozen=True)
class ReservoirFeatures:
    mouth_inner_diameter_mm: float
    mouth_outer_diameter_mm: float
    cavity_depth_mm: float
    foot_count: int


@dataclass(frozen=True)
class InsertPartResult:
    part: Part
    features: InsertFeatures


@dataclass(frozen=True)
class ReservoirPartResult:
    part: Part
    features: ReservoirFeatures


@dataclass(frozen=True)
class PlanterResult:
    """Both physically-separate parts, built together from one spec check."""

    insert: InsertPartResult
    reservoir: ReservoirPartResult


def _carve_wall_pattern(builder: BuildPart, bottom_r: float, top_r: float) -> None:
    """Cut the v1 "premium fluted" relief into the insert's outer wall only.

    This is the swap point for future series variants: a different
    pattern replaces only this function (plus its own ``pattern_*``
    parameters) while every other dimension — plate/tube/reservoir sizes,
    the reservoir/spigot/spout geometry — stays identical, per
    specs/planter/decisions.md ("Architektura wymiennego wzoru").

    Flute cutters are themselves partial cones (``arc_size``) with the
    same taper rate as the main body, offset inward by
    ``pattern_flute_depth`` — this keeps the flute depth uniform along the
    height despite the tapered outer surface. Cuts stop
    ``pattern_flute_end_margin`` short of both the top and bottom edges so
    the top rim stays a clean circle (a jagged rim breaks the fillet — see
    decisions.md) and the bottom resting edge stays flat.
    """
    taper_rate = (top_r - bottom_r) / p.INSERT_BODY_HEIGHT_MM
    cutter_height = p.INSERT_BODY_HEIGHT_MM - 2 * p.PATTERN_FLUTE_END_MARGIN_MM
    cutter_bottom_r = (bottom_r - p.PATTERN_FLUTE_DEPTH_MM) + taper_rate * p.PATTERN_FLUTE_END_MARGIN_MM
    cutter_top_r = cutter_bottom_r + taper_rate * cutter_height

    # Align.MIN (not CENTER) on X/Y: a partial-arc Cone's bounding box is
    # NOT centered on the revolve axis (it's centered on the wedge's own
    # bbox instead), so Align.CENTER silently mis-places the cutter off
    # the axis and the subtraction becomes a no-op — verified directly by
    # comparing cut volume before/after this fix, see decisions.md
    # ("Architektura wymiennego wzoru"). Align.MIN starts the wedge
    # exactly at the axis (its true apex), which is what PolarLocations
    # then rotates into place.
    with PolarLocations(0, p.PATTERN_FLUTE_COUNT), Locations(Location((0, 0, p.PATTERN_FLUTE_END_MARGIN_MM))):
        Cone(
            bottom_radius=cutter_bottom_r,
            top_radius=cutter_top_r,
            height=cutter_height,
            arc_size=p.PATTERN_FLUTE_WIDTH_DEG,
            align=(Align.MIN, Align.MIN, Align.MIN),
            mode=Mode.SUBTRACT,
        )


def build_insert_part() -> InsertPartResult:
    """Tapered, fluted pot shell + thickened floor + capillary tube + skirt.

    Z=0 is the insert's bottom resting edge (where it lands on the
    reservoir's rim) — the same reference plane used by
    ``build_reservoir_part``, so the two parts' Z coordinates describe one
    consistent assembly even though each is built/measured independently
    (see specs/planter/constraints.md on why the two parts are never
    unioned into a single solid).
    """
    p.check_engineering_preconditions()

    bottom_r = p.INSERT_BOTTOM_OUTER_DIAMETER_MM / 2
    top_r = p.INSERT_TOP_OUTER_DIAMETER_MM / 2
    wall = p.INSERT_WALL_THICKNESS_MM

    with BuildPart() as builder:
        Cone(
            bottom_radius=bottom_r,
            top_radius=top_r,
            height=p.INSERT_BODY_HEIGHT_MM,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
        top_face = builder.faces().sort_by(Axis.Z)[-1]
        offset(amount=-wall, openings=top_face)

        _carve_wall_pattern(builder, bottom_r, top_r)

        # Thicken the floor from the shell's uniform wall thickness up to
        # insert_floor_thickness by fusing an extra disc on the inside.
        extra_floor = p.INSERT_FLOOR_THICKNESS_MM - wall
        if extra_floor > 0:
            with Locations(Location((0, 0, wall))):
                Cylinder(
                    radius=bottom_r - wall - 0.2,
                    height=extra_floor,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )

        # Drainage/aeration holes through the floor.
        with PolarLocations(p.DRAINAGE_HOLE_CIRCLE_DIAMETER_MM / 2, p.DRAINAGE_HOLE_COUNT):
            Cylinder(
                radius=p.DRAINAGE_HOLE_DIAMETER_MM / 2,
                height=p.INSERT_FLOOR_THICKNESS_MM + 2,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                mode=Mode.SUBTRACT,
            )

        # Positioning skirt: thin-walled tube hanging below Z=0, slip-fits
        # into the reservoir's mouth.
        with Locations(Location((0, 0, 0))):
            Cylinder(
                radius=p.SPIGOT_OUTER_DIAMETER_MM / 2,
                height=p.SPIGOT_HEIGHT_MM,
                align=(Align.CENTER, Align.CENTER, Align.MAX),
            )
            Cylinder(
                radius=p.SPIGOT_OUTER_DIAMETER_MM / 2 - wall,
                height=p.SPIGOT_HEIGHT_MM + 2,
                align=(Align.CENTER, Align.CENTER, Align.MAX),
                mode=Mode.SUBTRACT,
            )

        # Fillet only the outer top edge — the inner edge sits on the same
        # ~wall-thickness-wide face, and OCCT cannot fillet both edges of a
        # face narrower than their combined radii (verified directly by
        # building — see specs/planter/decisions.md).
        top_face_2 = builder.faces().sort_by(Axis.Z)[-1]
        outer_top_edge = top_face_2.edges().sort_by(SortBy.RADIUS)[-1]
        fillet(outer_top_edge, radius=p.TOP_RIM_FILLET_RADIUS_MM)

        # Capillary tube: perforated hollow column, user-filled with soil,
        # spanning from inside the reservoir (near its floor) up into the
        # soil chamber. Built last so its slots never interact with the
        # floor-thickening/drainage-hole operations above (different
        # radius range entirely).
        tube_z_bottom = -(p.SPIGOT_HEIGHT_MM + p.RESERVOIR_CAVITY_DEPTH_MM - p.CAPILLARY_TUBE_RESERVOIR_CLEARANCE_MM)
        tube_z_top = p.CAPILLARY_TUBE_SOIL_PROTRUSION_MM
        tube_length = tube_z_top - tube_z_bottom
        with Locations(Location((0, 0, tube_z_bottom))):
            Cylinder(
                radius=p.CAPILLARY_TUBE_OUTER_DIAMETER_MM / 2,
                height=tube_length,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            Cylinder(
                radius=p.CAPILLARY_TUBE_INNER_DIAMETER_MM / 2,
                height=tube_length + 2,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                mode=Mode.SUBTRACT,
            )
            with PolarLocations(0, p.CAPILLARY_TUBE_SLOT_COUNT):
                Box(
                    p.CAPILLARY_TUBE_OUTER_DIAMETER_MM / 2 + 3,
                    p.CAPILLARY_TUBE_SLOT_WIDTH_MM,
                    tube_length + 2,
                    align=(Align.MIN, Align.CENTER, Align.CENTER),
                    mode=Mode.SUBTRACT,
                )

    assert builder.part is not None, "BuildPart produced no solid"

    features = InsertFeatures(
        top_outer_diameter_mm=p.INSERT_TOP_OUTER_DIAMETER_MM,
        bottom_outer_diameter_mm=p.INSERT_BOTTOM_OUTER_DIAMETER_MM,
        body_height_mm=p.INSERT_BODY_HEIGHT_MM,
        wall_thickness_mm=p.INSERT_WALL_THICKNESS_MM,
        drainage_hole_count=p.DRAINAGE_HOLE_COUNT,
        capillary_tube_outer_diameter_mm=p.CAPILLARY_TUBE_OUTER_DIAMETER_MM,
        pattern_flute_count=p.PATTERN_FLUTE_COUNT,
    )
    return InsertPartResult(part=builder.part, features=features)


def build_reservoir_part() -> ReservoirPartResult:
    """Straight-walled water tray + feet + external fill spout + overflow hole.

    Z=0 is the reservoir's top rim (same reference plane as the insert's
    resting edge, Z=0 in ``build_insert_part``); the cavity extends
    downward to Z=-reservoir_cavity_depth.
    """
    p.check_engineering_preconditions()

    outer_r = p.RESERVOIR_MOUTH_OUTER_DIAMETER_MM / 2
    wall = p.RESERVOIR_WALL_THICKNESS_MM
    depth = p.RESERVOIR_CAVITY_DEPTH_MM

    with BuildPart() as builder:
        with Locations(Location((0, 0, -depth))):
            Cylinder(radius=outer_r, height=depth, align=(Align.CENTER, Align.CENTER, Align.MIN))
        top_face = builder.faces().sort_by(Axis.Z)[-1]
        offset(amount=-wall, openings=top_face)

        # Feet under the true floor.
        with PolarLocations(outer_r * 0.6, p.RESERVOIR_FOOT_COUNT), Locations(Location((0, 0, -depth))):
            Cylinder(
                radius=p.RESERVOIR_FOOT_DIAMETER_MM / 2,
                height=p.RESERVOIR_FOOT_HEIGHT_MM,
                align=(Align.CENTER, Align.CENTER, Align.MAX),
            )

        # External fill spout, mounted flush against the outer wall so its
        # bore overlaps the cavity by construction (no separate connecting
        # hole needed) — see specs/planter/decisions.md.
        spout_z_bottom = -(depth - p.FILL_SPOUT_BOTTOM_CLEARANCE_MM)
        spout_z_top = p.FILL_SPOUT_TOP_PROTRUSION_MM
        spout_length = spout_z_top - spout_z_bottom
        with Locations(Location((outer_r, 0, spout_z_bottom))):
            Cylinder(
                radius=p.FILL_SPOUT_OUTER_DIAMETER_MM / 2,
                height=spout_length,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            Cylinder(
                radius=p.FILL_SPOUT_INNER_DIAMETER_MM / 2,
                height=spout_length + 2,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                mode=Mode.SUBTRACT,
            )

        # Overflow hole: horizontal through-hole opposite the spout, sets
        # the maximum water level.
        overflow_z = -depth + p.OVERFLOW_HOLE_HEIGHT_FROM_FLOOR_MM
        with Locations(Location((0, -outer_r - 2, overflow_z), (90, 0, 0))):
            Cylinder(
                radius=p.OVERFLOW_HOLE_DIAMETER_MM / 2,
                height=wall + 4,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                mode=Mode.SUBTRACT,
            )

    assert builder.part is not None, "BuildPart produced no solid"

    features = ReservoirFeatures(
        mouth_inner_diameter_mm=p.RESERVOIR_MOUTH_INNER_DIAMETER_MM,
        mouth_outer_diameter_mm=p.RESERVOIR_MOUTH_OUTER_DIAMETER_MM,
        cavity_depth_mm=p.RESERVOIR_CAVITY_DEPTH_MM,
        foot_count=p.RESERVOIR_FOOT_COUNT,
    )
    return ReservoirPartResult(part=builder.part, features=features)


def build_model() -> PlanterResult:
    return PlanterResult(insert=build_insert_part(), reservoir=build_reservoir_part())
