from unittest.mock import MagicMock

import pytest

import keypad as keypad_module
from keypad import PINS, Keypad

ROW_PINS = (PINS["row0"], PINS["row1"], PINS["row2"], PINS["row3"])
COL_PINS = (PINS["col0"], PINS["col1"], PINS["col2"])


def _event_detected_at(trigger_index):
    """event_detected side_effect that returns True only on the Nth call."""
    calls = {"n": -1}

    def side_effect(pin):
        calls["n"] += 1
        return calls["n"] == trigger_index

    return side_effect


def test_init_configures_rows_as_outputs(gpio):
    Keypad(MagicMock())
    for row_pin in ROW_PINS:
        gpio.setup.assert_any_call(row_pin, gpio.OUT)


def test_init_configures_columns_as_input_with_pullup(gpio):
    Keypad(MagicMock())
    for col_pin in COL_PINS:
        gpio.setup.assert_any_call(col_pin, gpio.IN, pull_up_down=gpio.PUD_UP)


def test_init_drives_all_rows_high(gpio):
    Keypad(MagicMock())
    for row_pin in ROW_PINS:
        gpio.output.assert_any_call(row_pin, gpio.HIGH)


def test_cancel_sets_cancelled_flag():
    kp = Keypad(MagicMock())
    assert kp._cancelled is False
    kp.cancel()
    assert kp._cancelled is True


def test_all_rows_high_drives_every_row_pin_high(gpio):
    kp = Keypad(MagicMock())
    gpio.output.reset_mock()
    kp._all_rows_high()
    assert gpio.output.call_count == 4
    for row_pin in ROW_PINS:
        gpio.output.assert_any_call(row_pin, gpio.HIGH)


def test_remove_detect_removes_every_column(gpio):
    kp = Keypad(MagicMock())
    gpio.remove_event_detect.reset_mock()
    kp._remove_detect()
    assert gpio.remove_event_detect.call_count == 3
    for col_pin in COL_PINS:
        gpio.remove_event_detect.assert_any_call(col_pin)


def test_enable_safely_registers_edge_detect(gpio):
    kp = Keypad(MagicMock())
    kp._enable_safely(PINS["col0"], gpio.BOTH)
    gpio.add_event_detect.assert_called_once_with(
        PINS["col0"], gpio.BOTH, bouncetime=150
    )


def test_enable_safely_retries_once_after_failure(gpio):
    kp = Keypad(MagicMock())
    gpio.add_event_detect.side_effect = [RuntimeError("busy"), None]
    kp._enable_safely(PINS["col0"], gpio.BOTH)
    assert gpio.add_event_detect.call_count == 2
    gpio.add_event_detect.assert_called_with(
        PINS["col0"], gpio.BOTH, bouncetime=150
    )


def test_read_key_returns_empty_string_when_cancelled_before_any_press(
    monkeypatch, gpio
):
    gpio.event_detected.return_value = False
    kp = Keypad(MagicMock())

    def fake_sleep(seconds):
        kp.cancel()

    monkeypatch.setattr(keypad_module.time, "sleep", fake_sleep)

    assert kp.read_key() == ""


@pytest.mark.parametrize(
    "row, col, expected_key",
    [
        (0, 0, "1"), (0, 1, "2"), (0, 2, "3"),
        (1, 0, "4"), (1, 1, "5"), (1, 2, "6"),
        (2, 0, "7"), (2, 1, "8"), (2, 2, "9"),
        (3, 0, "*"), (3, 1, "0"), (3, 2, "#"),
    ],
)
def test_read_key_detects_keypress_at_each_position(
    monkeypatch, gpio, row, col, expected_key
):
    monkeypatch.setattr(keypad_module.time, "sleep", lambda seconds: None)
    gpio.event_detected.side_effect = _event_detected_at(row * 3 + col)
    gpio.input.return_value = 1  # released by the time it's polled

    on_keydown = MagicMock()
    kp = Keypad(on_keydown)

    result = kp.read_key()

    assert result == expected_key
    on_keydown.assert_called_once_with(expected_key)


def test_read_key_polls_until_key_is_released(monkeypatch, gpio):
    monkeypatch.setattr(keypad_module.time, "sleep", lambda seconds: None)
    gpio.event_detected.side_effect = _event_detected_at(0)  # row0, col0 -> '1'
    gpio.input.side_effect = [0, 0, 1]  # still held twice, then released

    kp = Keypad(MagicMock())
    result = kp.read_key()

    assert result == "1"
    assert gpio.input.call_count == 3


def test_read_key_returns_empty_string_if_cancelled_while_waiting_for_release(
    monkeypatch, gpio
):
    gpio.event_detected.side_effect = _event_detected_at(0)  # row0, col0 -> '1'
    gpio.input.return_value = 0  # never released

    kp = Keypad(MagicMock())

    def fake_sleep(seconds):
        kp.cancel()

    monkeypatch.setattr(keypad_module.time, "sleep", fake_sleep)

    assert kp.read_key() == ""
