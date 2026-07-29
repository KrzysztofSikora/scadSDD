"""Dimensional checks: measured geometry / feature metadata vs specs/rifle-mount/parameters.yaml."""

from __future__ import annotations

import pytest

from cad_project.measurements import measure
from cad_project.rifle_mount import parameters as p


def test_base_bounding_box_footprint(built_result):
    measurements = measure(built_result.base.part)
    assert measurements.bounding_box_mm.x_mm == pytest.approx(
        p.MOUNTING_PLATE_SIZE_MM, abs=p.tolerance_for("mounting_plate_size")
    )
    assert measurements.bounding_box_mm.y_mm == pytest.approx(
        p.MOUNTING_PLATE_SIZE_MM, abs=p.tolerance_for("mounting_plate_size")
    )


def test_base_bounding_box_height_includes_boss(built_result):
    measurements = measure(built_result.base.part)
    expected_height = p.MOUNTING_PLATE_THICKNESS_MM + p.NUT_BOSS_LENGTH_MM
    assert measurements.bounding_box_mm.z_mm == pytest.approx(expected_height, abs=0.2)


def test_magnet_count_and_diameter(built_result):
    features = built_result.base.features
    assert features.magnet_count == p.MAGNET_COUNT
    assert features.magnet_diameter_mm == pytest.approx(
        p.MAGNET_DIAMETER_MM, abs=p.tolerance_for("magnet_diameter")
    )


def test_magnet_positions_are_symmetric(built_result):
    positions = set(built_result.base.features.magnet_positions_mm)
    for x, y in positions:
        assert (-x, y) in positions
        assert (x, -y) in positions
        assert (-x, -y) in positions


def test_magnet_edge_offset(built_result):
    expected = p.MOUNTING_PLATE_SIZE_MM / 2 - p.MAGNET_EDGE_OFFSET_MM
    for x, y in built_result.base.features.magnet_positions_mm:
        assert abs(abs(x) - expected) <= p.tolerance_for("magnet_edge_offset")
        assert abs(abs(y) - expected) <= p.tolerance_for("magnet_edge_offset")


def test_arm_bounding_box_length(built_result):
    measurements = measure(built_result.arm.part)
    expected_length = p.ROD_THREADED_LENGTH_MM + p.COLLAR_LENGTH_MM + (
        p.U_WALL_THICKNESS_MM + p.U_ARM_HEIGHT_MM
    )
    assert measurements.bounding_box_mm.z_mm == pytest.approx(expected_length, abs=0.2)


def test_arm_u_internal_width_matches_spec(built_result):
    assert built_result.arm.features.u_internal_width_mm == pytest.approx(
        p.U_INTERNAL_WIDTH_MM, abs=p.tolerance_for("u_internal_width")
    )


def test_arm_collar_diameter_matches_spec(built_result):
    assert built_result.arm.features.collar_diameter_mm == pytest.approx(
        p.COLLAR_DIAMETER_MM, abs=p.tolerance_for("collar_diameter")
    )


def test_thread_features_match_spec_on_both_parts(built_result):
    for thread in (built_result.base.features.thread, built_result.arm.features.thread):
        assert thread.pitch_mm == pytest.approx(p.THREAD_PITCH_MM, abs=p.tolerance_for("thread_pitch"))
        assert thread.major_diameter_mm == pytest.approx(
            p.THREAD_MAJOR_DIAMETER_MM, abs=p.tolerance_for("thread_major_diameter")
        )
        assert thread.angle_deg == pytest.approx(p.THREAD_ANGLE_DEG, abs=0.01)
