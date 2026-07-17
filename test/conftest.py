import os
import sys

import pytest

SRC_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "src", "opt", "futel", "src")
)
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from gpiozero import Device
from gpiozero.pins.mock import MockFactory


@pytest.fixture(autouse=True)
def mock_factory():
    """
    gpiozero talks to real hardware by default, so tests substitute its
    mock pin factory. A fresh factory per test isolates pin state.
    """
    factory = MockFactory()
    Device.pin_factory = factory
    yield factory
    factory.reset()
    Device.pin_factory = None
