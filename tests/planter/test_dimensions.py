"""Dimensional checks: measured geometry / feature metadata vs specs/planter/parameters.yaml."""

from __future__ import annotations

import pytest

from cad_project.measurements import measure
from cad_project.planter import parameters as p


def test_insert_bounding_box_footprint(built_result):
    measurements = measure(built_result.insert.part)
    assert measurements.bounding_box_mm.x_mm == pytest.approx(
        p.INSERT_TOP_OUTER_DIAMETER_MM, abs=p.tolerance_for("insert_top_outer_diameter") + 0.2
    )
    assert measurements.bounding_box_mm.y_mm == pytest.approx(
        p.INSERT_TOP_OUTER_DIAMETER_MM, abs=p.tolerance_for("insert_top_outer_diameter") + 0.2
    )


def test_insert_feature_metadata_matches_spec(built_result):
    features = built_result.insert.features
    assert features.top_outer_diameter_mm == pytest.approx(
        p.INSERT_TOP_OUTER_DIAMETER_MM, abs=p.tolerance_for("insert_top_outer_diameter")
    )
    assert features.bottom_outer_diameter_mm == pytest.approx(
        p.INSERT_BOTTOM_OUTER_DIAMETER_MM, abs=p.tolerance_for("insert_bottom_outer_diameter")
    )
    assert features.body_height_mm == pytest.approx(
        p.INSERT_BODY_HEIGHT_MM, abs=p.tolerance_for("insert_body_height")
    )
    assert features.drainage_hole_count == p.DRAINAGE_HOLE_COUNT
    assert features.pattern_flute_count == p.PATTERN_FLUTE_COUNT
    assert features.capillary_tube_outer_diameter_mm == pytest.approx(
        p.CAPILLARY_TUBE_OUTER_DIAMETER_MM, abs=p.tolerance_for("capillary_tube_outer_diameter")
    )


def test_reservoir_feature_metadata_matches_spec(built_result):
    features = built_result.reservoir.features
    assert features.mouth_inner_diameter_mm == pytest.approx(
        p.RESERVOIR_MOUTH_INNER_DIAMETER_MM, abs=p.tolerance_for("reservoir_mouth_inner_diameter")
    )
    assert features.cavity_depth_mm == pytest.approx(
        p.RESERVOIR_CAVITY_DEPTH_MM, abs=p.tolerance_for("reservoir_cavity_depth")
    )
    assert features.foot_count == p.RESERVOIR_FOOT_COUNT


def test_reservoir_bounding_box_depth(built_result):
    measurements = measure(built_result.reservoir.part)
    # Z spans from -(cavity_depth + foot_height) up to +fill_spout_top_protrusion.
    expected_height = p.RESERVOIR_CAVITY_DEPTH_MM + p.RESERVOIR_FOOT_HEIGHT_MM + p.FILL_SPOUT_TOP_PROTRUSION_MM
    assert measurements.bounding_box_mm.z_mm == pytest.approx(expected_height, abs=0.5)


def test_spigot_fits_reservoir_mouth_with_margin():
    """The spigot (derived) must slip inside the reservoir mouth with a
    positive, bounded radial clearance — see decisions.md for the
    fit_clearance derivation."""
    spigot_od = p.SPIGOT_OUTER_DIAMETER_MM
    assert 0 < spigot_od < p.RESERVOIR_MOUTH_INNER_DIAMETER_MM
    radial_gap = (p.RESERVOIR_MOUTH_INNER_DIAMETER_MM - spigot_od) / 2
    assert radial_gap == pytest.approx(p.FIT_CLEARANCE_MM, abs=1e-6)
