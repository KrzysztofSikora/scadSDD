"""Structural/topological geometry checks, error handling, and determinism."""

from __future__ import annotations

import pytest

from cad_project import parameters as p
from cad_project.measurements import count_cylindrical_faces_near_radius, measure
from cad_project.model import build_model
from cad_project.parameters import SpecificationError


def test_model_builds_without_error():
    result = build_model()
    assert result.part is not None


def test_produces_exactly_one_solid():
    result = build_model()
    assert len(result.part.solids()) == 1


def test_geometry_is_valid():
    result = build_model()
    assert result.part.is_valid is True


def test_volume_is_positive():
    result = build_model()
    assert result.part.volume > 0


def test_volume_is_less_than_solid_box():
    """Sanity check that material was actually removed by the holes/fillets."""
    result = build_model()
    solid_box_volume = p.LENGTH_MM * p.WIDTH_MM * p.BASE_THICKNESS_MM
    assert 0 < result.part.volume < solid_box_volume


def test_fillet_faces_present_at_specified_radius():
    result = build_model()
    fillet_faces = count_cylindrical_faces_near_radius(result.part, p.FILLET_RADIUS_MM)
    assert fillet_faces == 4


def test_topological_hole_face_count_matches_features():
    """Best-effort topological cross-check (informational per spec) should agree here."""
    result = build_model()
    observed = count_cylindrical_faces_near_radius(result.part, p.HOLE_DIAMETER_MM / 2)
    assert observed == result.features.hole_count


def test_model_is_deterministic_across_two_builds():
    first = build_model()
    second = build_model()

    m1 = measure(first.part)
    m2 = measure(second.part)

    assert m1.solid_count == m2.solid_count
    assert m1.bounding_box_mm == m2.bounding_box_mm
    assert m1.volume_mm3 == pytest.approx(m2.volume_mm3, abs=1e-6)
    assert m1.surface_area_mm2 == pytest.approx(m2.surface_area_mm2, abs=1e-6)
    assert first.features == second.features


def test_invalid_hole_edge_offset_raises_clear_specification_error(monkeypatch):
    """A hole_edge_offset that would push holes past the edge must stop generation, not guess."""
    monkeypatch.setattr(p, "HOLE_EDGE_OFFSET_MM", 1.0)
    with pytest.raises(SpecificationError, match="hole_edge_offset"):
        build_model()


def test_hole_edge_offset_overlapping_fillet_raises_clear_error(monkeypatch):
    """A hole too close to the corner would intersect the rounded fillet."""
    monkeypatch.setattr(p, "HOLE_EDGE_OFFSET_MM", 4.0)
    monkeypatch.setattr(p, "FILLET_RADIUS_MM", 3.0)
    with pytest.raises(SpecificationError, match="fillet_radius"):
        build_model()


def test_unsupported_hole_count_raises_clear_error(monkeypatch):
    monkeypatch.setattr(p, "HOLE_COUNT", 6)
    with pytest.raises(SpecificationError, match="hole_count"):
        build_model()
