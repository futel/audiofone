from unittest.mock import MagicMock

from hookswitch import Hookswitch


def _make_hookswitch(pin=26):
    on_hook_up = MagicMock(name="on_hook_up")
    on_hook_down = MagicMock(name="on_hook_down")
    hookswitch = Hookswitch(
        on_hook_down=on_hook_down, on_hook_up=on_hook_up, pin=pin)
    return hookswitch, on_hook_up, on_hook_down


def _state_changed_callback(gpio):
    """Return the callback that run() registered with add_event_detect."""
    _, kwargs = gpio.add_event_detect.call_args
    return kwargs["callback"]


def test_default_pin_is_26():
    hookswitch = Hookswitch(on_hook_down=MagicMock(), on_hook_up=MagicMock())
    assert hookswitch._pin == 26


def test_run_configures_pin_as_input_with_pullup(gpio):
    hookswitch, _, _ = _make_hookswitch(pin=26)
    hookswitch.run()
    gpio.setup.assert_called_once_with(26, gpio.IN, pull_up_down=gpio.PUD_UP)


def test_run_uses_configured_pin(gpio):
    hookswitch, _, _ = _make_hookswitch(pin=7)
    hookswitch.run()
    gpio.setup.assert_called_once_with(7, gpio.IN, pull_up_down=gpio.PUD_UP)
    args, _ = gpio.add_event_detect.call_args
    assert args[0] == 7


def test_run_registers_edge_detection_for_both_directions(gpio):
    hookswitch, _, _ = _make_hookswitch(pin=26)
    hookswitch.run()
    gpio.add_event_detect.assert_called_once()
    args, kwargs = gpio.add_event_detect.call_args
    assert args[0] == 26
    assert args[1] == gpio.BOTH
    assert callable(kwargs["callback"])


def test_state_changed_calls_on_hook_up_when_input_is_low(gpio):
    hookswitch, on_hook_up, on_hook_down = _make_hookswitch(pin=26)
    hookswitch.run()
    gpio.input.return_value = 0

    _state_changed_callback(gpio)(26)

    on_hook_up.assert_called_once()
    on_hook_down.assert_not_called()


def test_state_changed_calls_on_hook_down_when_input_is_high(gpio):
    hookswitch, on_hook_up, on_hook_down = _make_hookswitch(pin=26)
    hookswitch.run()
    gpio.input.return_value = 1

    _state_changed_callback(gpio)(26)

    on_hook_down.assert_called_once()
    on_hook_up.assert_not_called()


def test_state_changed_reads_the_channel_it_is_invoked_with(gpio):
    hookswitch, _, _ = _make_hookswitch(pin=26)
    hookswitch.run()
    gpio.input.return_value = 1

    _state_changed_callback(gpio)(26)

    gpio.input.assert_called_once_with(26)
