from unittest.mock import MagicMock

import pytest

import audiofone as audiofone_module
from audiofone import Hookstate, NumberValidity


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
    monkeypatch.setattr(audiofone_module, "hookstate", Hookstate.ON)
    monkeypatch.setattr(audiofone_module, "dialed_number", "")
    monkeypatch.setattr(audiofone_module, "busy_timer", None)
    monkeypatch.setattr(audiofone_module, "ring_timer", None)
    monkeypatch.setattr(audiofone_module, "tones", MagicMock(name="tones"))
    monkeypatch.setattr(audiofone_module, "keypad", MagicMock(name="keypad"))
    monkeypatch.setattr(audiofone_module.threading, "Timer", FakeTimer)


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


# go_busy / go_fast_busy

def test_go_busy_sets_state_and_plays_busy_tone():
    audiofone_module.go_busy()
    assert audiofone_module.hookstate == Hookstate.BUSY_WAIT
    audiofone_module.tones.off.assert_called_once()
    audiofone_module.tones.busy.assert_called_once()


def test_go_fast_busy_sets_state_and_plays_tone():
    audiofone_module.go_fast_busy()
    assert audiofone_module.hookstate == Hookstate.BUSY_WAIT
    audiofone_module.tones.off.assert_called_once()
    audiofone_module.tones.busy.assert_called_once()


# play_busy

def test_play_busy_does_nothing_when_on_hook():
    audiofone_module.hookstate = Hookstate.ON
    audiofone_module.play_busy()
    assert audiofone_module.hookstate == Hookstate.ON
    audiofone_module.tones.busy.assert_not_called()


def test_play_busy_goes_busy_when_off_hook():
    audiofone_module.hookstate = Hookstate.OFF
    audiofone_module.busy_timer = FakeTimer(1, lambda: None)
    audiofone_module.play_busy()
    assert audiofone_module.hookstate == Hookstate.BUSY_WAIT
    assert audiofone_module.busy_timer is None
    audiofone_module.tones.busy.assert_called_once()


# timers

def test_start_busy_timer_creates_and_starts_timer():
    audiofone_module.start_busy_timer()
    timer = audiofone_module.busy_timer
    assert isinstance(timer, FakeTimer)
    assert timer.interval == audiofone_module.BUSY_TIMEOUT
    assert timer.function is audiofone_module.play_busy
    assert timer.started is True


def test_start_busy_timer_cancels_existing_timers_first():
    old_busy = FakeTimer(1, lambda: None)
    old_ring = FakeTimer(1, lambda: None)
    audiofone_module.busy_timer = old_busy
    audiofone_module.ring_timer = old_ring
    audiofone_module.start_busy_timer()
    assert old_busy.cancelled is True
    assert old_ring.cancelled is True


def test_cancel_busy_timer_cancels_and_clears():
    timer = FakeTimer(1, lambda: None)
    audiofone_module.busy_timer = timer
    audiofone_module.cancel_busy_timer()
    assert timer.cancelled is True
    assert audiofone_module.busy_timer is None


def test_cancel_busy_timer_noop_when_none():
    audiofone_module.busy_timer = None
    audiofone_module.cancel_busy_timer()
    assert audiofone_module.busy_timer is None


def test_cancel_ring_timer_cancels_and_clears():
    timer = FakeTimer(1, lambda: None)
    audiofone_module.ring_timer = timer
    audiofone_module.cancel_ring_timer()
    assert timer.cancelled is True
    assert audiofone_module.ring_timer is None


def test_cancel_timers_cancels_both():
    busy = FakeTimer(1, lambda: None)
    ring = FakeTimer(1, lambda: None)
    audiofone_module.busy_timer = busy
    audiofone_module.ring_timer = ring
    audiofone_module.cancel_timers()
    assert busy.cancelled is True
    assert ring.cancelled is True


# on_keydown

def test_on_keydown_does_nothing_when_on_hook():
    audiofone_module.hookstate = Hookstate.ON
    audiofone_module.on_keydown("5")
    audiofone_module.tones.key.assert_not_called()


def test_on_keydown_plays_key_tone_when_off_hook():
    audiofone_module.hookstate = Hookstate.OFF
    audiofone_module.on_keydown("5")
    audiofone_module.tones.off.assert_called_once()
    audiofone_module.tones.key.assert_called_once_with("5")


def test_on_keydown_restarts_busy_timer_when_off_hook():
    audiofone_module.hookstate = Hookstate.OFF
    audiofone_module.on_keydown("5")
    assert isinstance(audiofone_module.busy_timer, FakeTimer)
    assert audiofone_module.busy_timer.started is True


def test_on_keydown_does_not_replay_off_tone_outside_off_hook_state():
    audiofone_module.hookstate = Hookstate.BUSY_WAIT
    audiofone_module.on_keydown("5")
    audiofone_module.tones.off.assert_not_called()
    audiofone_module.tones.key.assert_called_once_with("5")


# on_handset_pickup

def test_on_handset_pickup_resets_state():
    audiofone_module.dialed_number = "999"
    audiofone_module.on_handset_pickup()
    assert audiofone_module.hookstate == Hookstate.OFF
    assert audiofone_module.dialed_number == ""
    audiofone_module.tones.dialtone.assert_called_once()
    assert isinstance(audiofone_module.busy_timer, FakeTimer)
    assert audiofone_module.busy_timer.started is True


# on_hangup

def test_on_hangup_resets_state_cancels_keypad_and_timers():
    audiofone_module.hookstate = Hookstate.OFF
    busy = FakeTimer(1, lambda: None)
    ring = FakeTimer(1, lambda: None)
    audiofone_module.busy_timer = busy
    audiofone_module.ring_timer = ring

    audiofone_module.on_hangup()

    assert audiofone_module.hookstate == Hookstate.ON
    audiofone_module.tones.off.assert_called_once()
    audiofone_module.keypad.cancel.assert_called_once()
    assert busy.cancelled is True
    assert ring.cancelled is True


# start_number_event / play_audio_after_ring

def test_start_number_event_enters_ringing_state(monkeypatch):
    monkeypatch.setattr(audiofone_module.random, "randrange", lambda a, b: 7)
    audiofone_module.start_number_event("555_test")
    assert audiofone_module.hookstate == Hookstate.RINGING
    audiofone_module.tones.ring.assert_called_once()
    timer = audiofone_module.ring_timer
    assert isinstance(timer, FakeTimer)
    assert timer.interval == 7
    assert timer.started is True


def test_start_number_event_cancels_existing_timers():
    old_busy = FakeTimer(1, lambda: None)
    audiofone_module.busy_timer = old_busy
    audiofone_module.start_number_event("555_test")
    assert old_busy.cancelled is True


def test_play_audio_after_ring_plays_and_sets_state():
    audiofone_module.ring_timer = FakeTimer(1, lambda: None)
    audiofone_module.play_audio_after_ring("555_test")
    audiofone_module.tones.off.assert_called_once()
    audiofone_module.tones.play_audio.assert_called_once_with("555_test")
    assert audiofone_module.hookstate == Hookstate.PLAYING_AUDIO
    assert audiofone_module.ring_timer is None
