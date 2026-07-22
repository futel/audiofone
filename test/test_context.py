from unittest.mock import MagicMock

import pytest

import context
import dialnumbers
from context import BUSY_TIMEOUT, Dialplan, get_dialplan
from dialnumbers import NumberValidity


class FakeTimer:
    """
    Stand-in for threading.Timer that records its wiring instead of spawning a
    thread. Tests can invoke .function directly to simulate the timer firing.
    """

    instances = []

    def __init__(self, interval, function):
        self.interval = interval
        self.function = function
        self.started = False
        self.cancelled = False
        FakeTimer.instances.append(self)

    def start(self):
        self.started = True

    def cancel(self):
        self.cancelled = True


@pytest.fixture(autouse=True)
def fake_timer(monkeypatch):
    """Replace threading.Timer so no real timer threads escape a test."""
    FakeTimer.instances = []
    monkeypatch.setattr(context.threading, "Timer", FakeTimer)
    return FakeTimer


@pytest.fixture(autouse=True)
def fixed_ring_time(monkeypatch):
    """Make the random ring duration deterministic."""
    monkeypatch.setattr(context.random, "randrange", lambda a, b: 7)


@pytest.fixture
def tones():
    return MagicMock(name="Tones")


@pytest.fixture
def dialplan(tones):
    return get_dialplan(tones)


def stub_have_number(monkeypatch, result):
    """Force dialnumbers.have_number to return a fixed value."""
    monkeypatch.setattr(dialnumbers, "have_number", lambda number: result)


# get_dialplan / construction.


def test_get_dialplan_returns_dialplan_in_onhook(dialplan):
    assert isinstance(dialplan, Dialplan)
    assert dialplan.is_onhook() is True


def test_get_dialplan_starts_with_empty_number_and_no_timers(dialplan):
    assert dialplan.dialed_number == ""
    assert dialplan.busy_timer is None
    assert dialplan.ring_timer is None


def test_get_dialplan_attaches_trigger_methods(dialplan):
    for trigger in ("hook_up", "hook_down", "key_release"):
        assert callable(getattr(dialplan, trigger))


# hook_up: onhook -> dialtone.


def test_hook_up_enters_dialtone(dialplan, tones):
    dialplan.hook_up()
    assert dialplan.is_dialtone() is True
    tones.dialtone.assert_called_once_with()


def test_hook_up_starts_busy_timer(dialplan):
    dialplan.hook_up()
    assert dialplan.busy_timer is not None
    assert dialplan.busy_timer.interval == BUSY_TIMEOUT
    assert dialplan.busy_timer.started is True


def test_on_enter_dialtone_resets_dialed_number(dialplan):
    dialplan.dialed_number = "50355"
    # Return to onhook then back to dialtone.
    dialplan.hook_down()
    dialplan.hook_up()
    assert dialplan.dialed_number == ""


# hook_down: any state -> onhook.


def test_hook_down_from_dialtone_enters_onhook(dialplan, tones):
    dialplan.hook_up()
    tones.reset_mock()
    dialplan.hook_down()
    assert dialplan.is_onhook() is True
    tones.off.assert_called_once_with()


def test_hook_down_cancels_and_clears_timers(dialplan):
    dialplan.hook_up()
    busy_timer = dialplan.busy_timer
    dialplan.hook_down()
    assert busy_timer.cancelled is True
    assert dialplan.busy_timer is None
    assert dialplan.ring_timer is None


# dialtone_timeout: dialtone -> busy.


def test_dialtone_timeout_enters_busy(dialplan, tones):
    dialplan.hook_up()
    tones.reset_mock()
    dialplan.dialtone_timeout()
    assert dialplan.is_busy() is True
    tones.off.assert_called_once_with()
    tones.busy.assert_called_once_with()


def test_busy_timer_firing_moves_to_busy(dialplan):
    dialplan.hook_up()
    dialplan.busy_timer.function()  # simulate the busy timer expiring
    assert dialplan.is_busy() is True


# key_release is a no-op outside dialtone/digits.


def test_key_release_from_onhook_is_nop(dialplan):
    dialplan.key_release(key="5")
    assert dialplan.is_onhook() is True


def test_key_release_from_busy_is_nop(dialplan):
    dialplan.hook_up()
    dialplan.dialtone_timeout()
    assert dialplan.is_busy() is True
    dialplan.key_release(key="5")
    assert dialplan.is_busy() is True


# key_release / after_key_release: dialtone/digits -> digits, digit collection
# and dialplan branching.


def test_key_release_from_dialtone_enters_digits(dialplan, monkeypatch):
    stub_have_number(monkeypatch, NumberValidity.POSSIBLE_PREFIX)
    dialplan.hook_up()
    dialplan.key_release(key="5")
    assert dialplan.is_digits() is True


def test_key_release_accumulates_possible_prefix(dialplan, tones, monkeypatch):
    stub_have_number(monkeypatch, NumberValidity.POSSIBLE_PREFIX)
    dialplan.hook_up()
    dialplan.key_release(key="5")
    assert dialplan.dialed_number == "5"
    assert dialplan.is_digits() is True
    tones.off.assert_called()


def test_key_release_accumulates_across_multiple_keys(dialplan, monkeypatch):
    stub_have_number(monkeypatch, NumberValidity.POSSIBLE_PREFIX)
    dialplan.hook_up()
    dialplan.key_release(key="5")
    dialplan.key_release(key="0")
    dialplan.key_release(key="3")
    assert dialplan.dialed_number == "503"


def test_key_release_invalid_key_goes_to_busy(dialplan, monkeypatch):
    stub_have_number(monkeypatch, NumberValidity.INVALID_KEY)
    dialplan.hook_up()
    dialplan.key_release(key="0")
    assert dialplan.is_busy() is True


def test_key_release_not_prefix_goes_to_busy(dialplan, monkeypatch):
    stub_have_number(monkeypatch, NumberValidity.NOT_PREFIX)
    dialplan.hook_up()
    dialplan.key_release(key="9")
    assert dialplan.is_busy() is True


def test_key_release_match_enters_ringing(dialplan, tones, monkeypatch):
    stub_have_number(monkeypatch, "911_emergency")
    dialplan.hook_up()
    dialplan.key_release(key="9")
    assert dialplan.is_ringing() is True
    tones.ring.assert_called_once_with()


def test_key_release_match_cancels_busy_timer(dialplan, monkeypatch):
    stub_have_number(monkeypatch, "911_emergency")
    dialplan.hook_up()
    busy_timer = dialplan.busy_timer
    dialplan.key_release(key="9")
    assert busy_timer.cancelled is True
    assert dialplan.busy_timer is None


# ringing -> audio, driven by the ring timer.


def test_on_enter_ringing_starts_ring_timer(dialplan, monkeypatch):
    stub_have_number(monkeypatch, "911_emergency")
    dialplan.hook_up()
    dialplan.key_release(key="9")
    assert dialplan.ring_timer is not None
    assert dialplan.ring_timer.interval == 7
    assert dialplan.ring_timer.started is True


def test_ring_timer_firing_plays_audio(dialplan, tones, monkeypatch):
    stub_have_number(monkeypatch, "911_emergency")
    dialplan.hook_up()
    dialplan.key_release(key="9")
    tones.reset_mock()
    dialplan.ring_timer.function()  # simulate the ring timer expiring
    assert dialplan.is_audio() is True
    tones.play_audio.assert_called_once_with("911_emergency")


def test_play_audio_after_ring_clears_ring_timer(dialplan, tones):
    # Drive to ringing directly and fire the ring completion.
    dialplan.hook_up()
    dialplan.to_ringing()
    dialplan.play_audio_after_ring("some_sound")
    assert dialplan.is_audio() is True
    assert dialplan.ring_timer is None
    tones.play_audio.assert_called_once_with("some_sound")


# Timer helpers in isolation.


def test_start_busy_timer_cancels_previous(dialplan):
    dialplan.start_busy_timer()
    first = dialplan.busy_timer
    dialplan.start_busy_timer()
    assert first.cancelled is True
    assert dialplan.busy_timer is not first


def test_cancel_busy_timer_is_safe_when_unset(dialplan):
    dialplan.busy_timer = None
    dialplan.cancel_busy_timer()  # must not raise
    assert dialplan.busy_timer is None


def test_cancel_ring_timer_is_safe_when_unset(dialplan):
    dialplan.ring_timer = None
    dialplan.cancel_ring_timer()  # must not raise
    assert dialplan.ring_timer is None


def test_cancel_timers_cancels_both(dialplan):
    dialplan.start_busy_timer()
    dialplan.start_ring_timer("sound")
    busy_timer = dialplan.busy_timer
    ring_timer = dialplan.ring_timer
    dialplan.cancel_timers()
    assert busy_timer.cancelled is True
    assert ring_timer.cancelled is True
    assert dialplan.busy_timer is None
    assert dialplan.ring_timer is None


# A full successful dial from onhook to audio.


def test_full_dial_flow_reaches_audio(dialplan, tones, monkeypatch):
    responses = {
        "9": NumberValidity.POSSIBLE_PREFIX,
        "91": NumberValidity.POSSIBLE_PREFIX,
        "911": "911_emergency",
    }
    monkeypatch.setattr(dialnumbers, "have_number", lambda number: responses[number])

    dialplan.hook_up()
    for digit in "911":
        dialplan.key_release(key=digit)

    assert dialplan.is_ringing() is True
    assert dialplan.dialed_number == "911"

    dialplan.ring_timer.function()
    assert dialplan.is_audio() is True
    tones.play_audio.assert_called_once_with("911_emergency")
