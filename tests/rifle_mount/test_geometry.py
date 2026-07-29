"""Structural geometry checks, thread compatibility, error handling, determinism.

Note: this file performs one additional full build (in the determinism
test) beyond the shared session fixture — see conftest.py for why that is
kept to a minimum (each build takes ~20-30s, dominated by real helical
thread sweeps).
"""

from __future__ import annotations

import pytest

from cad_project.measurements import measure
from cad_project.rifle_mount import parameters as p
from cad_project.rifle_mount.model import build_model
from cad_project.rifle_mount.parameters import SpecificationError


def test_base_is_one_valid_solid(built_result):
    assert len(built_result.base.part.solids()) == 1
    assert built_result.base.part.is_valid is True
    assert built_result.base.part.volume > 0


def test_arm_is_one_valid_solid(built_result):
    assert len(built_result.arm.part.solids()) == 1
    assert built_result.arm.part.is_valid is True
    assert built_result.arm.part.volume > 0


def test_thread_features_match_between_parts(built_result):
    assert built_result.base.features.thread == built_result.arm.features.thread


def test_thread_engagement_maintained_at_max_extension():
    fixed_offset = (
        p.MOUNTING_PLATE_THICKNESS_MM
        + p.NUT_BOSS_LENGTH_MM
        + p.COLLAR_LENGTH_MM
        + p.CRADLE_TRANSITION_HEIGHT_MM
        + p.U_WALL_THICKNESS_MM
        + p.BARREL_DIAMETER_REFERENCE_MM / 2
    )
    exposed_max = p.WALL_TO_BARREL_CENTER_MAX_MM - fixed_offset
    engagement_at_max = p.ROD_THREADED_LENGTH_MM - exposed_max
    assert engagement_at_max >= p.THREAD_ENGAGEMENT_LENGTH_MM


def test_arm_bounding_box_is_symmetric_about_the_thread_axis(built_result):
    """Independent check that the C cradle is coaxial with the rod/thread axis.

    Unlike the fixed-offset arithmetic checks above (which just re-derive
    the same formula as the production code), this measures the actual
    built solid: if the cradle were off-axis, the bounding box would be
    lopsided in X instead of symmetric around the rod's own central axis.
    After the U -> C reorientation (see specs/rifle-mount/decisions.md),
    this symmetry holds by construction, not by tuning a parameter.
    """
    bbox = built_result.arm.part.bounding_box()
    assert pytest.approx(-bbox.max.X, abs=0.5) == bbox.min.X


def test_adjustment_range_matches_spec():
    fixed_offset = (
        p.MOUNTING_PLATE_THICKNESS_MM
        + p.NUT_BOSS_LENGTH_MM
        + p.COLLAR_LENGTH_MM
        + p.CRADLE_TRANSITION_HEIGHT_MM
        + p.U_WALL_THICKNESS_MM
        + p.BARREL_DIAMETER_REFERENCE_MM / 2
    )
    exposed_min = p.WALL_TO_BARREL_CENTER_MIN_MM - fixed_offset
    exposed_max = p.WALL_TO_BARREL_CENTER_MAX_MM - fixed_offset
    assert exposed_min > 0
    assert exposed_max - exposed_min == pytest.approx(
        p.WALL_TO_BARREL_CENTER_MAX_MM - p.WALL_TO_BARREL_CENTER_MIN_MM, abs=1e-6
    )


def test_model_is_deterministic_across_two_builds(built_result):
    second = build_model()

    for part_name, first_part, second_part in (
        ("base", built_result.base, second.base),
        ("arm", built_result.arm, second.arm),
    ):
        m1 = measure(first_part.part)
        m2 = measure(second_part.part)
        assert m1.solid_count == m2.solid_count, part_name
        assert m1.bounding_box_mm == m2.bounding_box_mm, part_name
        assert m1.volume_mm3 == pytest.approx(m2.volume_mm3, abs=1e-6), part_name
        assert m1.surface_area_mm2 == pytest.approx(m2.surface_area_mm2, abs=1e-6), part_name
        assert first_part.features == second_part.features, part_name


def test_magnet_pocket_boss_collision_raises_clear_error(monkeypatch):
    monkeypatch.setattr(p, "MOUNTING_PLATE_SIZE_MM", 50.0)
    with pytest.raises(SpecificationError, match="collide"):
        p.check_engineering_preconditions()


def test_insufficient_rod_thread_length_raises_clear_error(monkeypatch):
    monkeypatch.setattr(p, "ROD_THREADED_LENGTH_MM", 50.0)
    with pytest.raises(SpecificationError, match="rod_threaded_length"):
        p.check_engineering_preconditions()


def test_collar_smaller_than_thread_raises_clear_error(monkeypatch):
    monkeypatch.setattr(p, "COLLAR_DIAMETER_MM", 20.0)
    with pytest.raises(SpecificationError, match="collar_diameter"):
        p.check_engineering_preconditions()


def test_u_width_not_bigger_than_barrel_raises_clear_error(monkeypatch):
    monkeypatch.setattr(p, "U_INTERNAL_WIDTH_MM", 15.0)
    with pytest.raises(SpecificationError, match="u_internal_width"):
        p.check_engineering_preconditions()
