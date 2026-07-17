from unittest.mock import MagicMock

import pytest

import keypad as keypad_module
from keypad import PINS, Keypad

ROW_PINS = (PINS["row0"], PINS["row1"], PINS["row2"], PINS["row3"])
COL_PINS = (PINS["col0"], PINS["col1"], PINS["col2"])


def _pin_names(pins):
    return ["GPIO%d" % pin for pin in pins]


def _script_columns(kp, is_pressed_values):
    """Replace the keypad's column devices with fakes that yield the given
    is_pressed values across the scan (all three columns share the sequence,
    which is checked in row*3+col order, mirroring the real scan). After the
    sequence is exhausted, the last value repeats."""
    seq = iter(is_pressed_values)
    default = is_pressed_values[-1] if is_pressed_values else False

    def make_column():
        class FakeColumn:
            @property
            def is_pressed(self):
                return next(seq, default)

        return FakeColumn()

    kp._cols = [make_column(), make_column(), make_column()]


def _pressed_at(index):
    """is_pressed sequence with a single press at the Nth check, then release."""
    return [False] * index + [True, False]


def test_init_configures_rows_as_outputs():
    kp = Keypad(MagicMock())
    assert [d.pin.info.name for d in kp._rows] == _pin_names(ROW_PINS)
    for device in kp._rows:
        assert device.pin.function == "output"


def test_init_configures_columns_as_input_with_pullup():
    kp = Keypad(MagicMock())
    assert [d.pin.info.name for d in kp._cols] == _pin_names(COL_PINS)
    for device in kp._cols:
        assert device.pin.function == "input"
        assert device.pin.pull == "up"


def test_init_drives_all_rows_high():
    kp = Keypad(MagicMock())
    for device in kp._rows:
        assert device.value == 1


def test_cancel_sets_cancelled_flag():
    kp = Keypad(MagicMock())
    assert kp._cancelled is False
    kp.cancel()
    assert kp._cancelled is True


def test_all_rows_high_drives_every_row_pin_high():
    kp = Keypad(MagicMock())
    for device in kp._rows:
        device.off()
    kp._all_rows_high()
    for device in kp._rows:
        assert device.value == 1


def test_read_key_returns_empty_string_when_cancelled_before_any_press(
    monkeypatch,
):
    kp = Keypad(MagicMock())
    _script_columns(kp, [False])  # nothing ever pressed

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
    monkeypatch, row, col, expected_key
):
    monkeypatch.setattr(keypad_module.time, "sleep", lambda seconds: None)

    on_keydown = MagicMock()
    kp = Keypad(on_keydown)
    _script_columns(kp, _pressed_at(row * 3 + col))

    result = kp.read_key()

    assert result == expected_key
    on_keydown.assert_called_once_with(expected_key)


def test_read_key_polls_until_key_is_released(monkeypatch):
    monkeypatch.setattr(keypad_module.time, "sleep", lambda seconds: None)

    on_keydown = MagicMock()
    kp = Keypad(on_keydown)
    # row0, col0 -> '1': pressed at first check, held twice, then released.
    _script_columns(kp, [True, True, True, False])

    result = kp.read_key()

    assert result == "1"
    on_keydown.assert_called_once_with("1")


def test_read_key_returns_empty_string_if_cancelled_while_waiting_for_release(
    monkeypatch,
):
    kp = Keypad(MagicMock())
    _script_columns(kp, [True])  # pressed and never released

    def fake_sleep(seconds):
        kp.cancel()

    monkeypatch.setattr(keypad_module.time, "sleep", fake_sleep)

    assert kp.read_key() == ""
