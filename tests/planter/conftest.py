"""Shared fixtures for planter tests.

Building this model is fast (plain booleans, no helical thread sweeps
unlike rifle_mount), but a single session-scoped build is still shared
across test files that only need to inspect (not mutate) the result,
matching the pattern used by tests/rifle_mount/conftest.py.
"""

from __future__ import annotations

import pytest

from cad_project.planter.model import build_model


@pytest.fixture(scope="session")
def built_result():
    return build_model()
