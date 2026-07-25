from unittest.mock import MagicMock

import pytest

import zoo_context
from zoo_context import Dialplan, get_dialplan


@pytest.fixture
def tone_player(monkeypatch):
    """get_dialplan builds its own tones.Tones(); patch the class so the
    dialplan uses this mock and tests can assert on it."""
    instance = MagicMock(name="Tones")
    monkeypatch.setattr(zoo_context.tones, "Tones", lambda: instance)
    return instance


@pytest.fixture
def keypad():
    return MagicMock(name="Keypad")


@pytest.fixture
def dialplan(tone_player, keypad):
    return get_dialplan(keypad)


def event(**kwargs):
    """Build a stand-in for a transitions event (send_event=True), whose
    callback payload is read via event.kwargs.get(...)."""
    return MagicMock(name="event", kwargs=kwargs)


def test_get_dialplan_returns_dialplan_in_onhook(dialplan):
    assert isinstance(dialplan, Dialplan)
    assert dialplan.is_onhook() is True


def test_dialplan_starts_with_empty_digit_sequence(dialplan):
    assert dialplan.digit_sequence == []


def test_audio_off_stops_tone_and_terminates_process(dialplan, tone_player):
    process = MagicMock(name="audio_process")
    dialplan.audio_process = process
    dialplan.audio_off()
    tone_player.off.assert_called_once_with()
    process.terminate.assert_called_once_with()


def test_audio_off_without_process_only_stops_tone(dialplan, tone_player):
    dialplan.audio_process = None
    dialplan.audio_off()
    tone_player.off.assert_called_once_with()


def test_on_enter_digits_plays_key_tone(dialplan, tone_player):
    dialplan.on_enter_digits(event(key="5"))
    tone_player.key.assert_called_once_with("5")


def test_on_enter_busy_plays_busy(dialplan, tone_player):
    dialplan.on_enter_busy(event())
    tone_player.busy.assert_called_once_with()


def test_on_enter_onhook_resets_digit_sequence_and_cancels_keypad(
        dialplan, keypad):
    dialplan.digit_sequence = [1, 2, 3]
    dialplan.on_enter_onhook(event())
    assert dialplan.digit_sequence == []
    keypad.cancel.assert_called_once_with()


def test_play_audio_launches_aplay(dialplan, monkeypatch):
    popen = MagicMock(name="Popen")
    monkeypatch.setattr(zoo_context.subprocess, "Popen", popen)
    dialplan.play_audio("greeting.wav")
    popen.assert_called_once_with(
        ["aplay", zoo_context.audio_directory + "greeting.wav"])


@pytest.fixture
def no_aplay(monkeypatch):
    """Entering the audio state launches aplay via subprocess.Popen; stub it
    so tests exercise the transitions without spawning a player."""
    monkeypatch.setattr(zoo_context.subprocess, "Popen", MagicMock(name="Popen"))


def test_hook_up_enters_audio_with_no_digits(dialplan, no_aplay):
    """hook_up goes onhook -> audio; the missing key leaves the sequence empty."""
    dialplan.hook_up()
    assert dialplan.is_audio() is True
    assert dialplan.digit_sequence == []


def test_key_release_appends_digit(dialplan, no_aplay):
    """Pressing then releasing a digit key from audio records the digit."""
    dialplan.hook_up()
    dialplan.key_press(key="3")
    dialplan.key_release(key="3")
    assert dialplan.is_audio() is True
    assert dialplan.digit_sequence == [3]


def test_non_digit_key_is_not_recorded(dialplan, no_aplay):
    """Non-digit keys (e.g. '*') are ignored and not appended to the sequence."""
    dialplan.hook_up()
    dialplan.key_press(key="*")
    dialplan.key_release(key="*")
    assert dialplan.digit_sequence == []


def test_hook_down_returns_to_onhook_and_resets(dialplan, no_aplay):
    """hook_down from any state returns to onhook and clears dialed digits."""
    dialplan.hook_up()
    dialplan.key_press(key="3")
    dialplan.key_release(key="3")
    dialplan.hook_down()
    assert dialplan.is_onhook() is True
    assert dialplan.digit_sequence == []
