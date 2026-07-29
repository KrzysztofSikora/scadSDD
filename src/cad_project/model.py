"""Parametric Build123d geometry for the mounting bracket.

Building the model never exports or writes any file — see
``src/cad_project/exports.py`` for that. Importing this module never runs
Build123d either; only calling :func:`build_model` does.
"""

from __future__ import annotations

from dataclasses import dataclass

from build123d import (
    Axis,
    Box,
    BuildPart,
    BuildSketch,
    Circle,
    Locations,
    Mode,
    Part,
    extrude,
    fillet,
)

from cad_project import parameters as p


@dataclass(frozen=True)
class ModelFeatures:
    """Explicit, jointly-authoritative metadata about the features built into the part.

    Detecting "how many mounting holes exist" purely from solid topology is
    unreliable in general (a cylindrical face could be a hole, a boss, or a
    fillet). Rather than pretend such detection is robust, ``build_model``
    reports the features it deliberately constructed, and
    ``validation.py``/tests treat this as the authoritative record —
    cross-checked by a best-effort topological pass that is kept clearly
    informational (see ``specs/constraints.md``).
    """

    base_length_mm: float
    base_width_mm: float
    base_thickness_mm: float
    fillet_radius_mm: float
    hole_count: int
    hole_diameter_mm: float
    hole_positions_mm: tuple[tuple[float, float], ...]


@dataclass(frozen=True)
class ModelResult:
    """The built solid plus the feature metadata used to construct it."""

    part: Part
    features: ModelFeatures


def _hole_positions() -> tuple[tuple[float, float], ...]:
    """Symmetric corner positions, one hole_edge_offset in from each edge."""
    x = p.LENGTH_MM / 2 - p.HOLE_EDGE_OFFSET_MM
    y = p.WIDTH_MM / 2 - p.HOLE_EDGE_OFFSET_MM
    return ((x, y), (x, -y), (-x, y), (-x, -y))


def build_model() -> ModelResult:
    """Deterministically build the mounting bracket from spec parameters.

    Order of operations (see ``specs/spec.md`` "Geometria"):
    1. base box (length x width x thickness), centered at the origin,
    2. fillet the four vertical outer edges,
    3. cut four through-holes at symmetric corner positions.

    Note: Build123d's ``Builder`` subclasses (``BuildPart``, ``BuildSketch``,
    ...) only register a child builder with its parent when both are
    entered in the *same* Python stack frame (see
    ``Builder.__enter__``/``_python_frame`` in Build123d). Splitting this
    into helper functions that take the builder as a parameter would
    silently break that parent/child link (the sketch's circles would never
    become pending faces on the part), so the whole sequence is kept inline
    in one function rather than factored apart.
    """
    p.check_engineering_preconditions()

    positions = _hole_positions()

    with BuildPart() as builder:
        Box(p.LENGTH_MM, p.WIDTH_MM, p.BASE_THICKNESS_MM)

        vertical_edges = builder.edges().filter_by(Axis.Z)
        fillet(vertical_edges, radius=p.FILLET_RADIUS_MM)

        top_face = builder.faces().sort_by(Axis.Z)[-1]
        with BuildSketch(top_face), Locations(*positions):
            Circle(p.HOLE_DIAMETER_MM / 2)
        extrude(amount=-p.BASE_THICKNESS_MM, mode=Mode.SUBTRACT)

    features = ModelFeatures(
        base_length_mm=p.LENGTH_MM,
        base_width_mm=p.WIDTH_MM,
        base_thickness_mm=p.BASE_THICKNESS_MM,
        fillet_radius_mm=p.FILLET_RADIUS_MM,
        hole_count=p.HOLE_COUNT,
        hole_diameter_mm=p.HOLE_DIAMETER_MM,
        hole_positions_mm=positions,
    )
    assert builder.part is not None, "BuildPart produced no solid"
    return ModelResult(part=builder.part, features=features)
