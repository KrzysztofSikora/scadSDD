"""Parametric Build123d geometry for the magnetic rifle barrel mount.

Two independent parts, matching the physical, hand-assembled product:

* **Base** — square plate with 4 magnet pockets + a threaded nut boss.
* **Arm** — externally threaded rod + stop collar + U-shaped barrel cradle.

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
    extrude,
    fillet,
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
    magnet_diameter_mm: float
    magnet_positions_mm: tuple[tuple[float, float], ...]
    nut_boss_outer_diameter_mm: float
    nut_boss_length_mm: float
    thread: ThreadFeatures


@dataclass(frozen=True)
class ArmFeatures:
    rod_threaded_length_mm: float
    collar_diameter_mm: float
    collar_length_mm: float
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


def _magnet_positions() -> tuple[tuple[float, float], ...]:
    x = p.MOUNTING_PLATE_SIZE_MM / 2 - p.MAGNET_EDGE_OFFSET_MM
    return ((x, x), (x, -x), (-x, x), (-x, -x))


def build_base_part() -> BasePartResult:
    """Square magnet plate + internally-threaded nut boss.

    Order: plate -> fillet corners -> magnet pockets -> nut boss (plain
    cylinder) -> plain bore -> subtract thread ridges last (the boss's
    outer end face is only a simple, unambiguous flat disc as long as the
    thread cut happens after every other face-selection-based operation).
    """
    p.check_engineering_preconditions()
    positions = _magnet_positions()

    with BuildPart() as builder:
        Box(p.MOUNTING_PLATE_SIZE_MM, p.MOUNTING_PLATE_SIZE_MM, p.MOUNTING_PLATE_THICKNESS_MM)
        vertical_edges = builder.edges().filter_by(Axis.Z)
        fillet(vertical_edges, radius=p.PLATE_CORNER_FILLET_RADIUS_MM)

        inner_face = builder.faces().sort_by(Axis.Z)[-1]
        with BuildSketch(inner_face), Locations(*positions):
            Circle(p.MAGNET_DIAMETER_MM / 2)
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
        with Locations(Location((0, 0, boss_top_z - p.THREAD_ENGAGEMENT_LENGTH_MM))):
            TrapezoidalThread(
                diameter=p.THREAD_MAJOR_DIAMETER_MM,
                pitch=p.THREAD_PITCH_MM,
                thread_angle=p.THREAD_ANGLE_DEG,
                length=p.THREAD_ENGAGEMENT_LENGTH_MM,
                external=False,
                end_finishes=("fade", "fade"),
                mode=Mode.SUBTRACT,
            )

    assert builder.part is not None, "BuildPart produced no solid"

    features = BaseFeatures(
        plate_size_mm=p.MOUNTING_PLATE_SIZE_MM,
        plate_thickness_mm=p.MOUNTING_PLATE_THICKNESS_MM,
        magnet_count=p.MAGNET_COUNT,
        magnet_diameter_mm=p.MAGNET_DIAMETER_MM,
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
    """Threaded rod + stop collar + U-shaped barrel cradle.

    Every feature is placed with an explicit ``Location`` (never
    face-selection), so the complex threaded-rod solid never needs its
    faces queried — see the module docstring and
    specs/rifle-mount/decisions.md ("U orientation").
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

    u_outer_depth = 2 * p.U_WALL_THICKNESS_MM + p.U_INTERNAL_WIDTH_MM
    collar_end_z = p.ROD_THREADED_LENGTH_MM + p.COLLAR_LENGTH_MM
    u_gap_z_center = collar_end_z + p.U_WALL_THICKNESS_MM + p.U_INTERNAL_WIDTH_MM / 2

    # The U-cradle is centered on the rod's own axis (X=0) rather than
    # resting tangent to it, so the barrel ends up coaxial with the
    # thread/rod axis - see specs/rifle-mount/decisions.md ("U cradle
    # coaxial alignment fix").
    u_total_height = p.U_WALL_THICKNESS_MM + p.U_ARM_HEIGHT_MM
    u_floor_x = -u_total_height / 2 + p.U_WALL_THICKNESS_MM

    with BuildPart() as builder:
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

        with Locations(Location((0, 0, collar_end_z))):
            Box(
                u_total_height,
                p.U_ARM_LENGTH_MM,
                u_outer_depth,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )

        with Locations(Location((u_floor_x, 0, u_gap_z_center))):
            Box(
                p.U_ARM_HEIGHT_MM + 20,
                p.U_ARM_LENGTH_MM + 4,
                p.U_INTERNAL_WIDTH_MM,
                align=(Align.MIN, Align.CENTER, Align.CENTER),
                mode=Mode.SUBTRACT,
            )

        with Locations(Location((u_floor_x - 1, 0, u_gap_z_center))):
            Box(
                p.LINER_GROOVE_DEPTH_MM + 1,
                p.U_ARM_LENGTH_MM + 4,
                p.LINER_GROOVE_WIDTH_MM,
                align=(Align.MIN, Align.CENTER, Align.CENTER),
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
