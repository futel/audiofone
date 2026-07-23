from unittest.mock import MagicMock

import pytest

import tones as tones_module
from tones import NETRECEIVE_PORT, Tones


@pytest.fixture
def mock_client(monkeypatch):
    client = MagicMock(name="SimpleUDPClient")
    monkeypatch.setattr(
        tones_module.udp_client, "SimpleUDPClient", MagicMock(return_value=client)
    )
    return client


@pytest.fixture
def tones(mock_client):
    instance = Tones()
    # The constructor sends an initial /off; drop it so per-method tests can
    # assert on a clean send_message.
    mock_client.reset_mock()
    return instance


def test_constructor_uses_default_host_and_port(mock_client):
    Tones()
    tones_module.udp_client.SimpleUDPClient.assert_called_once_with(
        "127.0.0.1", NETRECEIVE_PORT
    )


def test_constructor_uses_given_host_and_port(mock_client):
    Tones(host="10.0.0.5", port=1234)
    tones_module.udp_client.SimpleUDPClient.assert_called_once_with("10.0.0.5", 1234)


def test_constructor_sends_off(mock_client):
    Tones()
    mock_client.send_message.assert_called_once_with("/off", "")


def test_dialtone_sends_dialtone_message(tones, mock_client):
    tones.dialtone()
    mock_client.send_message.assert_called_once_with("/dialtone", "")


def test_off_sends_off_message(tones, mock_client):
    tones.off()
    mock_client.send_message.assert_called_once_with("/off", "")


def test_busy_sends_busy_message(tones, mock_client):
    tones.busy()
    mock_client.send_message.assert_called_once_with("/busy", "")


def test_fast_busy_sends_fastbusy_message(tones, mock_client):
    tones.fast_busy()
    mock_client.send_message.assert_called_once_with("/fastbusy", "")


def test_ring_sends_ring_message(tones, mock_client):
    tones.ring()
    mock_client.send_message.assert_called_once_with("/ring", "")


def test_keys_off_sends_keys_off_message(tones, mock_client):
    tones.keys_off()
    mock_client.send_message.assert_called_once_with("/keys", "off")


def test_play_audio_sends_basename(tones, mock_client):
    tones.play_audio("5035555555_monologue")
    mock_client.send_message.assert_called_once_with(
        "/play", "5035555555_monologue"
    )


@pytest.mark.parametrize("digit", list("0123456789"))
def test_key_sends_digit_keys_as_int(tones, mock_client, digit):
    tones.key(digit)
    mock_client.send_message.assert_called_once_with("/key", int(digit))


@pytest.mark.parametrize("key", ["*", "#"])
def test_key_sends_non_digit_keys_unchanged(tones, mock_client, key):
    tones.key(key)
    mock_client.send_message.assert_called_once_with("/key", key)
