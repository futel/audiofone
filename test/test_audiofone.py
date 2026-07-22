from unittest.mock import MagicMock

import pytest

import audiofone as audiofone_module
import context
from audiofone import NumberValidity


class FakeTimer:
    """Stand-in for threading.Timer that doesn't spawn a real thread."""

    def __init__(self, interval, function):
        self.interval = interval
        self.function = function
        self.started = False
        self.cancelled = False

    def start(self):
        self.started = True

    def cancel(self):
        self.cancelled = True


@pytest.fixture(autouse=True)
def reset_state(monkeypatch):
    tones = MagicMock(name="tones")
    monkeypatch.setattr(audiofone_module, "tones", tones)
    monkeypatch.setattr(audiofone_module, "keypad", MagicMock(name="keypad"))
    # dialplan is built in main(), so construct a fresh one (initial: onhook)
    # per test. get_dialplan returns the model the Machine is attached to (with
    # the trigger and is_<state>() methods on it), not the Machine. It owns the
    # timers and the tone-playing on_enter callbacks, and shares the module's
    # tones mock, mirroring main().
    dialplan = context.get_dialplan(tones)
    monkeypatch.setattr(audiofone_module, "dialplan", dialplan)
    monkeypatch.setattr(audiofone_module, "dialed_number", "")
    # Timers now live on the Dialplan (in the context module); swap the real
    # threading.Timer there so tests never spawn a thread.
    monkeypatch.setattr(context.threading, "Timer", FakeTimer)


# soundfile_number

@pytest.mark.parametrize(
    "filename, expected",
    [
        ("5035555555.wav", "5035555555"),
        ("5035555555_monologue.wav", "5035555555"),
        ("123_a_b_c.wav", "123"),
    ],
)
def test_soundfile_number(filename, expected):
    assert audiofone_module.soundfile_number(filename) == expected


# get_soundfile

def test_get_soundfile_returns_matching_basename(monkeypatch):
    monkeypatch.setattr(
        audiofone_module.os, "listdir",
        lambda path: ["111.wav", "222_monologue.wav"])
    assert audiofone_module.get_soundfile("222") == "222_monologue"


def test_get_soundfile_returns_none_when_no_match(monkeypatch):
    monkeypatch.setattr(audiofone_module.os, "listdir", lambda path: ["111.wav"])
    assert audiofone_module.get_soundfile("999") is None


def test_get_soundfile_lists_the_audio_directory(monkeypatch):
    seen = {}

    def fake_listdir(path):
        seen["path"] = path
        return []

    monkeypatch.setattr(audiofone_module.os, "listdir", fake_listdir)
    audiofone_module.get_soundfile("123")
    assert seen["path"] == audiofone_module.audio_directory


# possible_number

def test_possible_number_true_when_dialed_shorter_than_longest(monkeypatch):
    monkeypatch.setattr(audiofone_module.os, "listdir", lambda path: ["12345.wav"])
    assert audiofone_module.possible_number("123") is True


def test_possible_number_false_when_dialed_as_long_as_longest(monkeypatch):
    monkeypatch.setattr(audiofone_module.os, "listdir", lambda path: ["123.wav"])
    assert audiofone_module.possible_number("123") is False


def test_possible_number_considers_longest_of_multiple_files(monkeypatch):
    monkeypatch.setattr(
        audiofone_module.os, "listdir", lambda path: ["1.wav", "12345.wav"])
    assert audiofone_module.possible_number("123") is True


# invalid_dialplan

@pytest.mark.parametrize("number", ["0", "0123", "12#34", "12*34", "#", "*"])
def test_invalid_dialplan_rejects(number):
    assert audiofone_module.invalid_dialplan(number) is True


@pytest.mark.parametrize("number", ["", "1", "123", "555"])
def test_invalid_dialplan_accepts(number):
    assert audiofone_module.invalid_dialplan(number) is False


# have_number

def test_have_number_returns_invalid_key_for_forbidden_number(monkeypatch):
    monkeypatch.setattr(audiofone_module.os, "listdir", lambda path: [])
    assert audiofone_module.have_number("0") is NumberValidity.INVALID_KEY


def test_have_number_returns_soundfile_when_matched(monkeypatch):
    monkeypatch.setattr(
        audiofone_module.os, "listdir", lambda path: ["555_test.wav"])
    assert audiofone_module.have_number("555") == "555_test"


def test_have_number_returns_possible_prefix(monkeypatch):
    monkeypatch.setattr(
        audiofone_module.os, "listdir", lambda path: ["5551234.wav"])
    assert audiofone_module.have_number("555") is NumberValidity.POSSIBLE_PREFIX


def test_have_number_returns_not_prefix(monkeypatch):
    monkeypatch.setattr(audiofone_module.os, "listdir", lambda path: ["555.wav"])
    assert audiofone_module.have_number("5551") is NumberValidity.NOT_PREFIX


# on_keydown

def test_on_keydown_does_nothing_when_on_hook():
    # dialplan starts onhook; keypresses are ignored until off hook.
    audiofone_module.on_keydown("5")
    audiofone_module.tones.key.assert_not_called()
    assert audiofone_module.dialplan.state == "onhook"


def test_on_keydown_plays_key_tone_when_off_hook():
    audiofone_module.dialplan.to_dialtone()
    audiofone_module.tones.reset_mock()  # discard on_enter_dialtone's calls
    audiofone_module.on_keydown("5")
    audiofone_module.tones.off.assert_called_once()
    audiofone_module.tones.key.assert_called_once_with("5")


def test_on_keydown_restarts_busy_timer_when_off_hook():
    audiofone_module.dialplan.to_dialtone()
    audiofone_module.on_keydown("5")
    timer = audiofone_module.dialplan.busy_timer
    assert isinstance(timer, FakeTimer)
    assert timer.started is True


# on_handset_pickup

def test_on_handset_pickup_resets_state_and_starts_dialtone():
    audiofone_module.dialed_number = "999"
    audiofone_module.on_handset_pickup()
    assert audiofone_module.dialplan.state == "dialtone"
    assert audiofone_module.dialed_number == ""
    audiofone_module.tones.dialtone.assert_called_once()
    timer = audiofone_module.dialplan.busy_timer
    assert isinstance(timer, FakeTimer)
    assert timer.started is True


# on_hangup

def test_on_hangup_resets_state_cancels_keypad_and_timers():
    audiofone_module.dialplan.to_dialtone()
    busy = FakeTimer(1, lambda: None)
    ring = FakeTimer(1, lambda: None)
    audiofone_module.dialplan.busy_timer = busy
    audiofone_module.dialplan.ring_timer = ring

    audiofone_module.on_hangup()

    assert audiofone_module.dialplan.state == "onhook"
    audiofone_module.tones.off.assert_called_once()
    audiofone_module.keypad.cancel.assert_called_once()
    assert busy.cancelled is True
    assert ring.cancelled is True


def test_on_hangup_from_any_state_returns_onhook():
    # hook_down is a global transition, valid from every state.
    audiofone_module.dialplan.to_busy()
    audiofone_module.on_hangup()
    assert audiofone_module.dialplan.state == "onhook"


# start_number_event

def test_start_number_event_rings_and_starts_timer(monkeypatch):
    monkeypatch.setattr(context.random, "randrange", lambda a, b: 7)
    audiofone_module.dialplan.to_digits()
    audiofone_module.start_number_event("555_test")
    assert audiofone_module.dialplan.state == "ringing"
    audiofone_module.tones.ring.assert_called_once()
    timer = audiofone_module.dialplan.ring_timer
    assert isinstance(timer, FakeTimer)
    assert timer.interval == 7
    assert timer.started is True


def test_start_number_event_cancels_existing_timers():
    old_busy = FakeTimer(1, lambda: None)
    audiofone_module.dialplan.to_digits()
    audiofone_module.dialplan.busy_timer = old_busy
    audiofone_module.start_number_event("555_test")
    assert old_busy.cancelled is True
