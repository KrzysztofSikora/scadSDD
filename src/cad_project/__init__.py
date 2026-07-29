"""Spec-driven CAD sample project: parametric Build123d models.

Two independent models live here:

* the mounting bracket (this package's top-level ``parameters``/``model``/
  ``validation``/``cli`` modules) — see ``specs/spec.md`` and
  ``specs/parameters.yaml``;
* the magnetic rifle barrel mount (``cad_project.rifle_mount``) — see
  ``specs/rifle-mount/spec.md`` and ``specs/rifle-mount/parameters.yaml``.

``measurements``, ``exports``, and ``rendering`` are generic (they take any
Build123d ``Part``) and are shared by both models.
"""

__version__ = "0.2.0"
