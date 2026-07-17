import time
from unittest.mock import MagicMock

from gpiozero import Button

from hookswitch import Hookswitch


def _named_mock(name):
    # gpiozero introspects a callback's signature (and its __name__) when it is
    # assigned to when_pressed/when_released, so the mock needs a __name__.
    callback = MagicMock(name=name)
    callback.__name__ = name
    return callback


def _make_hookswitch(pin=7):
    on_hook_up = _named_mock("on_hook_up")
    on_hook_down = _named_mock("on_hook_down")
    hookswitch = Hookswitch(
        on_hook_down=on_hook_down, on_hook_up=on_hook_up, pin=pin)
    return hookswitch, on_hook_up, on_hook_down


def _wait_for(predicate, timeout=1.0):
    """Wait for gpiozero's event thread to deliver a callback."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(0.005)


def test_default_pin_is_7():
    hookswitch = Hookswitch(on_hook_down=MagicMock(), on_hook_up=MagicMock())
    assert hookswitch._pin == 7


def test_run_configures_button_on_pin_with_pullup():
    hookswitch, _, _ = _make_hookswitch(pin=7)
    hookswitch.run()
    assert isinstance(hookswitch._button, Button)
    assert hookswitch._button.pin.info.name == "GPIO7"
    assert hookswitch._button.pin.pull == "up"


def test_run_uses_configured_pin():
    hookswitch, _, _ = _make_hookswitch(pin=26)
    hookswitch.run()
    assert hookswitch._button.pin.info.name == "GPIO26"


def test_calls_on_hook_up_when_pin_goes_low():
    hookswitch, on_hook_up, on_hook_down = _make_hookswitch(pin=7)
    hookswitch.run()

    hookswitch._button.pin.drive_low()

    _wait_for(lambda: on_hook_up.called)
    on_hook_up.assert_called_once()
    on_hook_down.assert_not_called()


def test_calls_on_hook_down_when_pin_goes_high():
    hookswitch, on_hook_up, on_hook_down = _make_hookswitch(pin=7)
    hookswitch.run()
    hookswitch._button.pin.drive_low()
    _wait_for(lambda: on_hook_up.called)

    hookswitch._button.pin.drive_high()

    _wait_for(lambda: on_hook_down.called)
    on_hook_down.assert_called_once()
