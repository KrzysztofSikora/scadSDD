"""Structural geometry checks, error handling, determinism, and a direct
verification that the wall pattern actually removes material (not just
that the build succeeds without an exception) — see
specs/planter/decisions.md ("Bug: Align.CENTER na częściowym Cone...")
for why a passing build is not sufficient evidence on its own.
"""

from __future__ import annotations

import pytest
from build123d import Align, Axis, BuildPart, Cone, offset

from cad_project.measurements import measure
from cad_project.planter import parameters as p
from cad_project.planter.model import build_model
from cad_project.planter.parameters import SpecificationError


def test_insert_is_one_valid_solid(built_result):
    assert len(built_result.insert.part.solids()) == 1
    assert built_result.insert.part.is_valid is True
    assert built_result.insert.part.volume > 0


def test_reservoir_is_one_valid_solid(built_result):
    assert len(built_result.reservoir.part.solids()) == 1
    assert built_result.reservoir.part.is_valid is True
    assert built_result.reservoir.part.volume > 0


def test_wall_pattern_actually_removes_material(built_result):
    """Regression test for the Align.CENTER bug (decisions.md): builds a
    bare shell (same envelope as the real insert, no floor/holes/skirt/
    tube) with and without ``_carve_wall_pattern`` applied, and asserts
    the pattern measurably reduces the volume. A passing build with
    ``is_valid=True`` is not sufficient evidence on its own — the buggy
    version also built cleanly while silently cutting nothing."""
    from cad_project.planter.model import _carve_wall_pattern

    assert built_result.insert.features.pattern_flute_count == p.PATTERN_FLUTE_COUNT > 0

    bottom_r = p.INSERT_BOTTOM_OUTER_DIAMETER_MM / 2
    top_r = p.INSERT_TOP_OUTER_DIAMETER_MM / 2

    with BuildPart() as plain:
        Cone(
            bottom_radius=bottom_r,
            top_radius=top_r,
            height=p.INSERT_BODY_HEIGHT_MM,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
        top_face = plain.faces().sort_by(Axis.Z)[-1]
        offset(amount=-p.INSERT_WALL_THICKNESS_MM, openings=top_face)

    with BuildPart() as fluted:
        Cone(
            bottom_radius=bottom_r,
            top_radius=top_r,
            height=p.INSERT_BODY_HEIGHT_MM,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
        top_face = fluted.faces().sort_by(Axis.Z)[-1]
        offset(amount=-p.INSERT_WALL_THICKNESS_MM, openings=top_face)
        _carve_wall_pattern(fluted, bottom_r, top_r)

    removed = plain.part.volume - fluted.part.volume
    assert removed > 100.0, (
        f"Wall pattern removed only {removed:.2f} mm^3 - flutes are not cutting "
        "(see decisions.md Align.CENTER bug)."
    )


def test_model_is_deterministic_across_two_builds(built_result):
    second = build_model()

    for part_name, first_part, second_part in (
        ("insert", built_result.insert, second.insert),
        ("reservoir", built_result.reservoir, second.reservoir),
    ):
        m1 = measure(first_part.part)
        m2 = measure(second_part.part)
        assert m1.solid_count == m2.solid_count, part_name
        assert m1.bounding_box_mm == m2.bounding_box_mm, part_name
        assert m1.volume_mm3 == pytest.approx(m2.volume_mm3, abs=1e-6), part_name
        assert m1.surface_area_mm2 == pytest.approx(m2.surface_area_mm2, abs=1e-6), part_name
        assert first_part.features == second_part.features, part_name


def test_floor_thinner_than_wall_raises_clear_error(monkeypatch):
    monkeypatch.setattr(p, "INSERT_FLOOR_THICKNESS_MM", 1.0)
    with pytest.raises(SpecificationError, match="insert_floor_thickness"):
        p.check_engineering_preconditions()


def test_flute_depth_too_deep_raises_clear_error(monkeypatch):
    monkeypatch.setattr(p, "PATTERN_FLUTE_DEPTH_MM", 2.2)
    with pytest.raises(SpecificationError, match="pattern_flute_depth"):
        p.check_engineering_preconditions()


def test_top_rim_fillet_too_large_raises_clear_error(monkeypatch):
    monkeypatch.setattr(p, "TOP_RIM_FILLET_RADIUS_MM", 3.0)
    with pytest.raises(SpecificationError, match="top_rim_fillet_radius"):
        p.check_engineering_preconditions()


def test_fill_spout_collision_raises_clear_error(monkeypatch):
    # Kept > 2mm above the reservoir-overhang threshold (110mm) so that
    # check fires first and this one is reached and fails instead.
    monkeypatch.setattr(p, "INSERT_BOTTOM_OUTER_DIAMETER_MM", 116.0)
    with pytest.raises(SpecificationError, match="fill spout"):
        p.check_engineering_preconditions()


def test_reservoir_mouth_overhang_too_small_raises_clear_error(monkeypatch):
    monkeypatch.setattr(p, "INSERT_BOTTOM_OUTER_DIAMETER_MM", 108.0)
    with pytest.raises(SpecificationError, match="insert's bottom edge"):
        p.check_engineering_preconditions()
