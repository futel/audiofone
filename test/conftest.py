import os
import sys
from unittest.mock import MagicMock

import pytest

SRC_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "src", "opt", "futel", "src")
)
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# RPi.GPIO only installs on real Raspberry Pi hardware, so tests substitute a
# mock module in its place. This must happen before any module under test
# imports RPi.GPIO.
gpio_mock = MagicMock(name="RPi.GPIO")
rpi_mock = MagicMock(name="RPi")
rpi_mock.GPIO = gpio_mock
sys.modules["RPi"] = rpi_mock
sys.modules["RPi.GPIO"] = gpio_mock


@pytest.fixture(autouse=True)
def gpio():
    """Reset the mocked RPi.GPIO module's call history before each test."""
    import RPi.GPIO as GPIO

    GPIO.reset_mock(return_value=True, side_effect=True)
    return GPIO
