"""Shared fixtures for rifle_mount tests.

Building this model is slow (~20-30s combined for both parts, dominated by
the real helical thread sweeps — see specs/rifle-mount/decisions.md), so a
single session-scoped build is shared across every test file that only
needs to inspect (not mutate) the result. Only the dedicated determinism
test in test_geometry.py performs a second, independent build.
"""

from __future__ import annotations

import pytest

from cad_project.rifle_mount.model import build_model


@pytest.fixture(scope="session")
def built_result():
    return build_model()
