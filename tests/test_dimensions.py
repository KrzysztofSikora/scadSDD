"""Dimensional checks: the built solid's measured geometry must match specs/parameters.yaml."""

from __future__ import annotations

import pytest

from cad_project import parameters as p
from cad_project.measurements import measure
from cad_project.model import build_model


@pytest.fixture(scope="module")
def built():
    result = build_model()
    return result, measure(result.part)


def test_bounding_box_length(built):
    _result, measurements = built
    assert measurements.bounding_box_mm.x_mm == pytest.approx(
        p.LENGTH_MM, abs=p.tolerance_for("length")
    )


def test_bounding_box_width(built):
    _result, measurements = built
    assert measurements.bounding_box_mm.y_mm == pytest.approx(
        p.WIDTH_MM, abs=p.tolerance_for("width")
    )


def test_bounding_box_thickness(built):
    _result, measurements = built
    assert measurements.bounding_box_mm.z_mm == pytest.approx(
        p.BASE_THICKNESS_MM, abs=p.tolerance_for("base_thickness")
    )


def test_hole_count_matches_spec(built):
    result, _measurements = built
    assert result.features.hole_count == p.HOLE_COUNT


def test_hole_diameter_matches_spec(built):
    result, _measurements = built
    assert result.features.hole_diameter_mm == pytest.approx(
        p.HOLE_DIAMETER_MM, abs=p.tolerance_for("hole_diameter")
    )


def test_hole_positions_are_symmetric(built):
    """Holes must be placed symmetrically about both the X and Y axes."""
    result, _measurements = built
    positions = set(result.features.hole_positions_mm)
    for x, y in positions:
        assert (-x, y) in positions
        assert (x, -y) in positions
        assert (-x, -y) in positions


def test_hole_edge_offset_matches_spec(built):
    """Each hole center must sit exactly hole_edge_offset in from the base edges."""
    result, _measurements = built
    expected_x = p.LENGTH_MM / 2 - p.HOLE_EDGE_OFFSET_MM
    expected_y = p.WIDTH_MM / 2 - p.HOLE_EDGE_OFFSET_MM
    for x, y in result.features.hole_positions_mm:
        assert abs(abs(x) - expected_x) <= p.tolerance_for("hole_edge_offset")
        assert abs(abs(y) - expected_y) <= p.tolerance_for("hole_edge_offset")
