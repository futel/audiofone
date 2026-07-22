import pytest

import dialnumbers
from dialnumbers import (
    NumberValidity,
    get_soundfile,
    have_number,
    invalid_dialplan,
    possible_number,
    soundfile_number,
)

# A representative audio directory: the longest soundfile number is 10 digits.
LISTING = ["5035551234_monologue.wav", "911_emergency.wav"]


@pytest.fixture
def audio_dir(monkeypatch):
    """Pretend the audio directory contains LISTING, regardless of hardware."""
    monkeypatch.setattr(dialnumbers.os, "listdir", lambda path: list(LISTING))
    return LISTING


# soundfile_number: strip extension, then take the part before the first '_'.


@pytest.mark.parametrize(
    "filename,expected",
    [
        ("5035551234_monologue.wav", "5035551234"),
        ("911_emergency.wav", "911"),
        ("42.wav", "42"),
        ("1234", "1234"),
    ],
)
def test_soundfile_number_extracts_number(filename, expected):
    assert soundfile_number(filename) == expected


# get_soundfile: return the matching filename without its extension, else None.


def test_get_soundfile_returns_basename_for_match(audio_dir):
    assert get_soundfile("911") == "911_emergency"


def test_get_soundfile_returns_basename_for_longer_match(audio_dir):
    assert get_soundfile("5035551234") == "5035551234_monologue"


def test_get_soundfile_returns_none_when_no_match(audio_dir):
    assert get_soundfile("999") is None


# possible_number: True while shorter than the longest known soundfile number.


def test_possible_number_true_for_short_prefix(audio_dir):
    assert possible_number("50") is True


def test_possible_number_true_at_one_below_max_length(audio_dir):
    assert possible_number("503555123") is True


def test_possible_number_false_at_max_length(audio_dir):
    assert possible_number("5035551234") is False


def test_possible_number_false_when_longer_than_max(audio_dir):
    assert possible_number("50355512345") is False


# invalid_dialplan: leading zero or any '#'/'*' is forbidden.


@pytest.mark.parametrize("number", ["0", "0123", "12#3", "12*3", "#", "*"])
def test_invalid_dialplan_true_for_forbidden(number):
    assert invalid_dialplan(number) is True


@pytest.mark.parametrize("number", ["1", "911", "5035551234"])
def test_invalid_dialplan_false_for_allowed(number):
    assert invalid_dialplan(number) is False


# have_number: the public entry point tying the helpers together.


@pytest.mark.parametrize("number", ["0123", "12#", "5*"])
def test_have_number_invalid_key(audio_dir, number):
    assert have_number(number) is NumberValidity.INVALID_KEY


def test_have_number_returns_soundfile_on_match(audio_dir):
    assert have_number("911") == "911_emergency"


def test_have_number_possible_prefix(audio_dir):
    assert have_number("5") is NumberValidity.POSSIBLE_PREFIX


def test_have_number_not_prefix_when_too_long_and_unmatched(audio_dir):
    assert have_number("50355512345") is NumberValidity.NOT_PREFIX
