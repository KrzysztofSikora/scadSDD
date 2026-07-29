"""Pure geometric measurement functions over a built :class:`Part`.

Nothing in this module mutates the model, exports files, or reads
specification data — it only measures the solid it is given.
"""

from __future__ import annotations

from dataclasses import dataclass

from build123d import GeomType, Part

from cad_project import parameters as p


@dataclass(frozen=True)
class BoundingBox:
    x_mm: float
    y_mm: float
    z_mm: float


@dataclass(frozen=True)
class Measurements:
    solid_count: int
    is_valid: bool
    volume_mm3: float
    surface_area_mm2: float
    bounding_box_mm: BoundingBox
    mass_kg: float | None


def measure(part: Part, *, density_kg_mm3: float | None = None) -> Measurements:
    """Compute the standard measurement set for a solid.

    Args:
        part: the built solid.
        density_kg_mm3: material density used only for the optional mass
            estimate. Defaults to ``parameters.MATERIAL_DENSITY_KG_MM3``.
    """
    solids = part.solids()
    bbox = part.bounding_box()
    volume = part.volume
    density = p.MATERIAL_DENSITY_KG_MM3 if density_kg_mm3 is None else density_kg_mm3
    mass = volume * density if density is not None else None

    return Measurements(
        solid_count=len(solids),
        is_valid=bool(part.is_valid),
        volume_mm3=volume,
        surface_area_mm2=part.area,
        bounding_box_mm=BoundingBox(
            x_mm=bbox.size.X,
            y_mm=bbox.size.Y,
            z_mm=bbox.size.Z,
        ),
        mass_kg=mass,
    )


def count_cylindrical_faces_near_radius(
    part: Part, radius_mm: float, *, radius_tolerance_mm: float = 0.01
) -> int:
    """Best-effort topological count of cylindrical faces near a given radius.

    This is intentionally *not* used as the authoritative hole count (see
    ``specs/constraints.md``): a cylindrical face at this radius could in
    principle come from a fillet or another feature that happens to share
    the same radius, not necessarily a mounting hole. Each cylindrical hole
    contributes exactly one cylindrical face in Build123d/OCCT's
    representation of a simple through-bore, so for the reference bracket
    geometry this count is expected to equal ``hole_count`` — but it is
    reported in the validation report as a supplementary, informational
    cross-check, never as a replacement for the explicit ``ModelFeatures``
    metadata returned by ``build_model()``.
    """
    count = 0
    for face in part.faces():
        if face.geom_type != GeomType.CYLINDER:
            continue
        face_radius = getattr(face, "radius", None)
        if face_radius is None:
            continue
        if abs(face_radius - radius_mm) <= radius_tolerance_mm:
            count += 1
    return count
