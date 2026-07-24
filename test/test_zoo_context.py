from unittest.mock import MagicMock

import pytest

import zoo_context
from zoo_context import Dialplan, get_dialplan


@pytest.fixture
def tones(monkeypatch):
    """get_dialplan builds its own Tones(); patch the class so the dialplan
    uses this mock and tests can assert on it."""
    instance = MagicMock(name="Tones")
    monkeypatch.setattr(zoo_context, "Tones", lambda: instance)
    return instance


@pytest.fixture
def keypad():
    return MagicMock(name="Keypad")


@pytest.fixture
def dialplan(tones, keypad):
    return get_dialplan(keypad)


def test_get_dialplan_returns_dialplan_in_onhook(dialplan):
    assert isinstance(dialplan, Dialplan)
    assert dialplan.is_onhook() is True
