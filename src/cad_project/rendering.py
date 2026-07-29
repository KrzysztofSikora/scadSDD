"""Headless isometric PNG preview rendering.

The execution environment has ``cadquery-ocp-novtk`` (OCP built without VTK
bindings), so Build123d/OCP's own interactive 3D viewers are not available.
Instead this module tessellates each face of the solid individually
(``Face.tessellate``) and rasterizes a simple Lambert-shaded isometric view
with matplotlib's ``Agg`` backend, which is fully headless and needs no
GUI, X server, or VTK.

Faces are drawn in a single figure but as separate ``Poly3DCollection``
instances ordered from lowest to highest average Z, with
``ax.computed_zorder = False`` forcing that draw order. This avoids a
rendering artifact observed when tessellating the whole solid into one
collection: `Poly3DCollection`'s default per-polygon "average" depth sort
mis-ordered large, irregular triangles produced by OCCT's triangulation of
the top face (a rectangle with four holes cut out), causing far geometry to
incorrectly paint over near geometry. See specs/decisions.md.

Rendering failures must never block STEP/STL export — callers should treat
:func:`render_preview_png` failures as an independent, separately reported
error (see ``src/cad_project/cli.py``).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from build123d import GeomType, Part

from cad_project import parameters as p
from cad_project.parameters import REPO_ROOT

PREVIEW_PATH: Path = REPO_ROOT / "output" / "previews" / "model.png"

_ISOMETRIC_ELEVATION_DEG = 35.264
_ISOMETRIC_AZIMUTH_DEG = 45.0
_LIGHT_DIRECTION = np.array([0.5, 0.5, 0.85])
_LIGHT_DIRECTION = _LIGHT_DIRECTION / np.linalg.norm(_LIGHT_DIRECTION)
_BASE_COLOR = np.array([0.55, 0.65, 0.85])
_HOLE_SHADE_FACTOR = 0.55
_MIN_SHADE = 0.25
_FIGURE_SIZE_INCHES = 6.0
_FIGURE_DPI = 160
_TESSELLATION_TOLERANCE_MM = 0.1


@dataclass(frozen=True)
class RenderOutcome:
    status: str  # "passed" | "failed"
    path: str
    error: str | None = None


def _face_mesh(face, tolerance: float) -> np.ndarray | None:
    vertices, triangles = face.tessellate(tolerance)
    if not triangles:
        return None
    points = np.array([(v.X, v.Y, v.Z) for v in vertices])
    tri_indices = np.array(triangles)
    return points[tri_indices]


def _shade_triangles(mesh: np.ndarray, *, darken: bool) -> np.ndarray:
    v0, v1, v2 = mesh[:, 0], mesh[:, 1], mesh[:, 2]
    normals = np.cross(v1 - v0, v2 - v0)
    lengths = np.linalg.norm(normals, axis=1, keepdims=True)
    lengths[lengths == 0] = 1.0
    normals = normals / lengths
    shade = np.clip(np.abs(normals @ _LIGHT_DIRECTION), _MIN_SHADE, 1.0)
    colors = _BASE_COLOR[None, :] * shade[:, None]
    if darken:
        colors = colors * _HOLE_SHADE_FACTOR
    return np.clip(colors, 0.0, 1.0)


def _is_hole_wall(face) -> bool:
    if face.geom_type != GeomType.CYLINDER:
        return False
    radius = getattr(face, "radius", None)
    if radius is None:
        return False
    return abs(radius - p.HOLE_DIAMETER_MM / 2) <= 0.01


def render_preview_png(part: Part, path: Path = PREVIEW_PATH) -> RenderOutcome:
    """Render an isometric, light-background PNG preview of ``part``.

    Never raises: any failure is captured and returned as a failed
    :class:`RenderOutcome` so callers can report it without aborting the
    rest of the export pipeline.
    """
    try:
        return _render(part, path)
    except Exception as exc:  # noqa: BLE001 - deliberately captured for the report
        return RenderOutcome(status="failed", path=str(path), error=str(exc))


def _render(part: Part, path: Path) -> RenderOutcome:
    import matplotlib

    matplotlib.use("Agg", force=True)
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    faces = list(part.faces())
    if not faces:
        return RenderOutcome(status="failed", path=str(path), error="Part has no faces to render.")

    face_layers: list[tuple[float, np.ndarray, bool]] = []
    for face in faces:
        mesh = _face_mesh(face, _TESSELLATION_TOLERANCE_MM)
        if mesh is None:
            continue
        avg_z = float(mesh[:, :, 2].mean())
        face_layers.append((avg_z, mesh, _is_hole_wall(face)))

    if not face_layers:
        return RenderOutcome(
            status="failed", path=str(path), error="Tessellation produced no triangles."
        )

    face_layers.sort(key=lambda item: item[0])

    bbox = part.bounding_box()

    fig = plt.figure(
        figsize=(_FIGURE_SIZE_INCHES, _FIGURE_SIZE_INCHES),
        dpi=_FIGURE_DPI,
        facecolor="white",
    )
    ax = fig.add_subplot(111, projection="3d")
    ax.computed_zorder = False
    ax.set_facecolor("white")

    for order, (_avg_z, mesh, is_hole) in enumerate(face_layers):
        colors = _shade_triangles(mesh, darken=is_hole)
        collection = Poly3DCollection(
            mesh,
            facecolor=colors,
            edgecolor=(0.15, 0.15, 0.15, 0.5),
            linewidths=0.15,
        )
        collection.set_zorder(order)
        ax.add_collection3d(collection)

    ax.set_xlim(bbox.min.X, bbox.max.X)
    ax.set_ylim(bbox.min.Y, bbox.max.Y)
    ax.set_zlim(bbox.min.Z, bbox.max.Z)
    ax.set_box_aspect((bbox.size.X, bbox.size.Y, max(bbox.size.Z, bbox.size.X * 0.15)))
    ax.view_init(elev=_ISOMETRIC_ELEVATION_DEG, azim=_ISOMETRIC_AZIMUTH_DEG)
    ax.set_axis_off()

    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout(pad=0)
    fig.savefig(path, facecolor="white")
    plt.close(fig)

    if not path.exists() or path.stat().st_size == 0:
        return RenderOutcome(
            status="failed", path=str(path), error="Figure save produced no file / empty file."
        )
    return RenderOutcome(status="passed", path=str(path))


def existing_preview_outcome(path: Path = PREVIEW_PATH) -> RenderOutcome:
    """Check whether a previously rendered preview exists, without rendering.

    Used by ``cad_project.cli validate`` as opposed to ``render``/``all``.
    """
    if path.exists() and path.stat().st_size > 0:
        return RenderOutcome(status="passed", path=str(path))
    return RenderOutcome(
        status="failed",
        path=str(path),
        error=f"Preview file not found at {path}. Run `render` or `all` first.",
    )
