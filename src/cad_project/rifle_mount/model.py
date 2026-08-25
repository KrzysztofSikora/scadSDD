"""Parametric Build123d geometry for the magnetic rifle barrel mount.

Two independent parts, matching the physical, hand-assembled product:

* **Base** — square plate with 2 magnet pockets + a threaded nut boss.
* **Arm** — externally threaded rod + stop collar + C-shaped barrel cradle.

Building never exports or writes any file. See ``specs/rifle-mount/spec.md``
("Geometria") for the operation order and ``specs/rifle-mount/decisions.md``
for why the two parts are built as flat, single-scope functions rather than
factored into smaller helpers that take a shared builder: Build123d's
``Builder`` subclasses (``BuildPart``, ``BuildSketch``, ...) only link a
child builder to its parent when both are entered in the same Python stack
frame (see ``cad_project.model`` for the same constraint on the bracket
model) — so each part's full operation sequence is kept in one function.

The thread itself is real, printable geometry (``bd_warehouse``'s
trapezoidal/ACME thread generator), not a placeholder — see
``specs/rifle-mount/decisions.md``. This makes building noticeably slower
than the mounting bracket (rough order of 20-30s combined for both parts on
typical hardware).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from bd_warehouse.thread import TrapezoidalThread
from build123d import (
    Align,
    Axis,
    Box,
    BuildPart,
    BuildSketch,
    Circle,
    Cylinder,
    Location,
    Locations,
    Mode,
    Part,
    Plane,
    Rectangle,
    RectangleRounded,
    extrude,
    fillet,
    loft,
)

from cad_project.rifle_mount import parameters as p


@dataclass(frozen=True)
class ThreadFeatures:
    """Explicit thread metadata — see specs/rifle-mount/constraints.md on
    why thread compatibility is asserted from these declared values rather
    than by re-deriving thread geometry topologically from the solid."""

    pitch_mm: float
    major_diameter_mm: float
    angle_deg: float
    engagement_length_mm: float


@dataclass(frozen=True)
class BaseFeatures:
    plate_size_mm: float
    plate_thickness_mm: float
    magnet_count: int
    magnet_pocket_length_mm: float
    magnet_pocket_width_mm: float
    magnet_positions_mm: tuple[tuple[float, float], ...]
    nut_boss_outer_diameter_mm: float
    nut_boss_length_mm: float
    thread: ThreadFeatures


@dataclass(frozen=True)
class ArmFeatures:
    rod_threaded_length_mm: float
    collar_diameter_mm: float
    collar_length_mm: float
    cradle_transition_height_mm: float
    cradle_corner_fillet_radius_mm: float
    u_internal_width_mm: float
    u_arm_length_mm: float
    u_wall_thickness_mm: float
    thread: ThreadFeatures


@dataclass(frozen=True)
class BasePartResult:
    part: Part
    features: BaseFeatures


@dataclass(frozen=True)
class ArmPartResult:
    part: Part
    features: ArmFeatures


@dataclass(frozen=True)
class RifleMountResult:
    """Both physically-separate parts, built together from one spec check."""

    base: BasePartResult
    arm: ArmPartResult


# Empirically, subtracting a single internal TrapezoidalThread solid this
# long (major_diameter=25mm, pitch=4mm, angle=29deg, nut_wall_thickness=4mm)
# from the boss becomes an invalid OCCT boolean past roughly 24mm of cut
# length (produces zero solids, not an exception) - a known robustness
# limit of bd_warehouse/OCCT for long helical internal cuts, unrelated to
# this model's specific parameters (reproduced with a bare cylinder too).
# Splitting the cut into several shorter TrapezoidalThread subtractions,
# each within this safe length, avoids it - see
# specs/rifle-mount/decisions.md ("Wydłużenie zazębienia gwintu").
_MAX_SINGLE_INTERNAL_THREAD_CUT_MM = 20.0


def _magnet_positions() -> tuple[tuple[float, float], ...]:
    y = p.MAGNET_CENTER_OFFSET_Y_MM
    return ((0.0, y), (0.0, -y))


def build_base_part() -> BasePartResult:
    """Square magnet plate + internally-threaded nut boss.

    Order: plate -> fillet corners -> magnet pockets -> nut boss (plain
    cylinder) -> plain bore -> subtract thread ridges last (the boss's
    outer end face is only a simple, unambiguous flat disc as long as the
    thread cut happens after every other face-selection-based operation).

    Magnet pockets are bored from the outer (wall-facing) face, not the
    inner face - see specs/rifle-mount/decisions.md ("v2.2 - kieszenie
    magnesów od strony ścianki"). This leaves magnet_pocket_wall_thickness
    of material on the *inner* side instead of the wall side.

    Pockets are rectangular (adhesive magnetic strips, not disc magnets)
    since v3 - see specs/rifle-mount/decisions.md ("v3 - paski
    magnetyczne zamiast dysków").
    """
    p.check_engineering_preconditions()
    positions = _magnet_positions()

    with BuildPart() as builder:
        Box(p.MOUNTING_PLATE_SIZE_MM, p.MOUNTING_PLATE_SIZE_MM, p.MOUNTING_PLATE_THICKNESS_MM)
        vertical_edges = builder.edges().filter_by(Axis.Z)
        fillet(vertical_edges, radius=p.PLATE_CORNER_FILLET_RADIUS_MM)

        outer_face = builder.faces().sort_by(Axis.Z)[0]
        with BuildSketch(outer_face), Locations(*positions):
            Rectangle(p.MAGNET_POCKET_LENGTH_MM, p.MAGNET_POCKET_WIDTH_MM)
        extrude(amount=-p.MAGNET_THICKNESS_MM, mode=Mode.SUBTRACT)

        boss_base_face = builder.faces().sort_by(Axis.Z)[-1]
        with BuildSketch(boss_base_face):
            Circle(p.NUT_BOSS_OUTER_DIAMETER_MM / 2)
        extrude(amount=p.NUT_BOSS_LENGTH_MM, mode=Mode.ADD)

        boss_top_face = builder.faces().sort_by(Axis.Z)[-1]
        with BuildSketch(boss_top_face):
            Circle(p.THREAD_MAJOR_DIAMETER_MM / 2)
        extrude(amount=-p.THREAD_ENGAGEMENT_LENGTH_MM, mode=Mode.SUBTRACT)

        boss_top_z = p.MOUNTING_PLATE_THICKNESS_MM / 2 + p.NUT_BOSS_LENGTH_MM
        thread_start_z = boss_top_z - p.THREAD_ENGAGEMENT_LENGTH_MM
        segment_count = max(
            1, math.ceil(p.THREAD_ENGAGEMENT_LENGTH_MM / _MAX_SINGLE_INTERNAL_THREAD_CUT_MM)
        )
        segment_length = p.THREAD_ENGAGEMENT_LENGTH_MM / segment_count
        for i in range(segment_count):
            with Locations(Location((0, 0, thread_start_z + i * segment_length))):
                TrapezoidalThread(
                    diameter=p.THREAD_MAJOR_DIAMETER_MM,
                    pitch=p.THREAD_PITCH_MM,
                    thread_angle=p.THREAD_ANGLE_DEG,
                    length=segment_length,
                    external=False,
                    end_finishes=("fade", "fade"),
                    mode=Mode.SUBTRACT,
                )

    assert builder.part is not None, "BuildPart produced no solid"

    features = BaseFeatures(
        plate_size_mm=p.MOUNTING_PLATE_SIZE_MM,
        plate_thickness_mm=p.MOUNTING_PLATE_THICKNESS_MM,
        magnet_count=p.MAGNET_COUNT,
        magnet_pocket_length_mm=p.MAGNET_POCKET_LENGTH_MM,
        magnet_pocket_width_mm=p.MAGNET_POCKET_WIDTH_MM,
        magnet_positions_mm=positions,
        nut_boss_outer_diameter_mm=p.NUT_BOSS_OUTER_DIAMETER_MM,
        nut_boss_length_mm=p.NUT_BOSS_LENGTH_MM,
        thread=ThreadFeatures(
            pitch_mm=p.THREAD_PITCH_MM,
            major_diameter_mm=p.THREAD_MAJOR_DIAMETER_MM,
            angle_deg=p.THREAD_ANGLE_DEG,
            engagement_length_mm=p.THREAD_ENGAGEMENT_LENGTH_MM,
        ),
    )
    return BasePartResult(part=builder.part, features=features)


def build_arm_part() -> ArmPartResult:
    """Threaded rod + stop collar + smooth transition + C-shaped barrel cradle.

    Every feature is placed with an explicit ``Location`` (never
    face-selection), so the complex threaded-rod solid never needs its
    faces queried — see the module docstring and
    specs/rifle-mount/decisions.md ("U orientation", "U -> C cradle
    reorientation").

    v2 adds a smooth (lofted) transition between the collar and the
    C-cradle block, and rounds the block's outer vertical edges, so the
    arm prints without support material — see decisions.md ("v2 —
    łagodne przejście C/gwint"). The cradle block is built and filleted
    *first*, while it is the only solid in the builder, so
    ``builder.edges().filter_by(Axis.Z)`` unambiguously selects only its
    own 4 corner edges (mirrors the plate-corner fillet pattern in
    ``build_base_part``).
    """
    p.check_engineering_preconditions()

    # Root radius of the external thread's core rod, computed by a throwaway
    # probe (outside any BuildPart context, so it registers nowhere) rather
    # than re-derived by hand, to stay exactly consistent with bd_warehouse's
    # own thread geometry.
    probe = TrapezoidalThread(
        diameter=p.THREAD_MAJOR_DIAMETER_MM,
        pitch=p.THREAD_PITCH_MM,
        thread_angle=p.THREAD_ANGLE_DEG,
        length=1,
        external=True,
    )
    core_radius = probe.root_radius

    # The C-cradle opens toward the arm's tip (away from the collar), not
    # upward — see specs/rifle-mount/decisions.md ("U -> C cradle
    # reorientation"). Its symmetric clearance (u_internal_width) now runs
    # along X, perpendicular to both the rod axis (Z) and the barrel axis
    # (Y); this makes the barrel coaxial with the rod by construction
    # (X=0 always, regardless of parameter values), unlike the old U shape
    # which needed u_arm_height tuned to a specific value for that.
    collar_end_z = p.ROD_THREADED_LENGTH_MM + p.COLLAR_LENGTH_MM
    cradle_start_z = collar_end_z + p.CRADLE_TRANSITION_HEIGHT_MM
    u_block_x_extent = 2 * p.U_WALL_THICKNESS_MM + p.U_INTERNAL_WIDTH_MM
    u_block_z_depth = p.U_WALL_THICKNESS_MM + p.U_ARM_HEIGHT_MM
    u_gap_z_start = cradle_start_z + p.U_WALL_THICKNESS_MM

    with BuildPart() as builder:
        with Locations(Location((0, 0, cradle_start_z))):
            Box(
                u_block_x_extent,
                p.U_ARM_LENGTH_MM,
                u_block_z_depth,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
        vertical_edges = builder.edges().filter_by(Axis.Z)
        fillet(vertical_edges, radius=p.CRADLE_CORNER_FILLET_RADIUS_MM)

        Cylinder(
            radius=core_radius,
            height=p.ROD_THREADED_LENGTH_MM,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )

        with Locations(Location((0, 0, p.ROD_THREADED_LENGTH_MM))):
            Cylinder(
                radius=p.COLLAR_DIAMETER_MM / 2,
                height=p.COLLAR_LENGTH_MM,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )

        # Smooth loft transition: a circle matching the collar's top face
        # blends into a rounded rectangle matching the cradle block's own
        # (already-filleted) bottom cross-section — same fillet radius on
        # both ends, so the two solids meet without a seam or step. See
        # decisions.md for the self-supporting angle this achieves (~42.4°,
        # measured directly on the built solid).
        with BuildSketch(Plane.XY.offset(collar_end_z)) as transition_bottom:
            Circle(p.COLLAR_DIAMETER_MM / 2)
        with BuildSketch(Plane.XY.offset(cradle_start_z)) as transition_top:
            RectangleRounded(u_block_x_extent, p.U_ARM_LENGTH_MM, p.CRADLE_CORNER_FILLET_RADIUS_MM)
        loft([transition_bottom.sketch.faces()[0], transition_top.sketch.faces()[0]])

        with Locations(Location((0, 0, u_gap_z_start))):
            Box(
                p.U_INTERNAL_WIDTH_MM,
                p.U_ARM_LENGTH_MM + 4,
                p.U_ARM_HEIGHT_MM + 20,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                mode=Mode.SUBTRACT,
            )

        with Locations(Location((0, 0, u_gap_z_start + 1))):
            Box(
                p.LINER_GROOVE_WIDTH_MM,
                p.U_ARM_LENGTH_MM + 4,
                p.LINER_GROOVE_DEPTH_MM + 1,
                align=(Align.CENTER, Align.CENTER, Align.MAX),
                mode=Mode.SUBTRACT,
            )

        with Locations(Location((0, 0, 0))):
            TrapezoidalThread(
                diameter=p.THREAD_MAJOR_DIAMETER_MM,
                pitch=p.THREAD_PITCH_MM,
                thread_angle=p.THREAD_ANGLE_DEG,
                length=p.ROD_THREADED_LENGTH_MM,
                external=True,
                end_finishes=("fade", "fade"),
                mode=Mode.ADD,
            )

    assert builder.part is not None, "BuildPart produced no solid"

    features = ArmFeatures(
        rod_threaded_length_mm=p.ROD_THREADED_LENGTH_MM,
        collar_diameter_mm=p.COLLAR_DIAMETER_MM,
        collar_length_mm=p.COLLAR_LENGTH_MM,
        cradle_transition_height_mm=p.CRADLE_TRANSITION_HEIGHT_MM,
        cradle_corner_fillet_radius_mm=p.CRADLE_CORNER_FILLET_RADIUS_MM,
        u_internal_width_mm=p.U_INTERNAL_WIDTH_MM,
        u_arm_length_mm=p.U_ARM_LENGTH_MM,
        u_wall_thickness_mm=p.U_WALL_THICKNESS_MM,
        thread=ThreadFeatures(
            pitch_mm=p.THREAD_PITCH_MM,
            major_diameter_mm=p.THREAD_MAJOR_DIAMETER_MM,
            angle_deg=p.THREAD_ANGLE_DEG,
            engagement_length_mm=p.THREAD_ENGAGEMENT_LENGTH_MM,
        ),
    )
    return ArmPartResult(part=builder.part, features=features)


def build_model() -> RifleMountResult:
    """Build both parts of the rifle mount."""
    return RifleMountResult(base=build_base_part(), arm=build_arm_part())
