"""Tests that run the integration inside a real Home Assistant core.

Needs ``pip install pytest-homeassistant-custom-component`` (Linux or WSL).
Kept apart from ``tests/``, whose conftest replaces ``homeassistant`` with
stubs — run the two directories in separate pytest calls.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Home Assistant imports ``custom_components`` from its (test) config folder
# when it starts. Import this repo's folder first, so that it is the one.
import custom_components  # noqa: E402, F401


@pytest.fixture(autouse=True)
def _custom_integrations(enable_custom_integrations):
    """Let Home Assistant load integrations from custom_components/."""
    yield
