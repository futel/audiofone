import pytest

import menu
from menu import get_content


SAMPLE_MENUS = {
    "content": "root.wav",
    "destinations": [
        {"content": "a.wav",
         "destinations": [
             {"content": "a_a.wav"},
             {"content": "a_b.wav"}]},
        {"content": "b.wav",
         "destinations": [
             {"content": "b_a.wav"},
             {"content": "b_b.wav",
              "destinations": [
                  {"content": "b_b_a.wav"}]}]},
        {"content": "c.wav"}]}


@pytest.fixture(autouse=True)
def sample_menus(monkeypatch):
    """get_content reads the module-global `menus`; patch it so tests run
    against a known tree instead of the bundled asset."""
    monkeypatch.setattr(menu, "menus", SAMPLE_MENUS)


def test_empty_position_returns_initial_content():
    assert get_content([]) == "root.wav"


def test_none_position_returns_initial_content():
    assert get_content(None) == "root.wav"


def test_single_level_first_destination():
    assert get_content([0]) == "a.wav"


def test_single_level_other_destinations():
    assert get_content([1]) == "b.wav"
    assert get_content([2]) == "c.wav"


def test_nested_two_levels():
    assert get_content([0, 0]) == "a_a.wav"
    assert get_content([0, 1]) == "a_b.wav"
    assert get_content([1, 0]) == "b_a.wav"


def test_nested_three_levels():
    assert get_content([1, 1, 0]) == "b_b_a.wav"


def test_leaf_node_without_destinations():
    """A destination with no "destinations" key is a valid leaf."""
    assert get_content([2]) == "c.wav"


def test_does_not_mutate_position():
    """Callers should be able to reuse the position vector after the call."""
    position = [1, 1, 0]
    get_content(position)
    assert position == [1, 1, 0]


def test_out_of_range_index_raises():
    with pytest.raises(IndexError):
        get_content([9])


def test_descending_into_leaf_raises():
    """Navigating past a leaf (no "destinations") is a caller error."""
    with pytest.raises(KeyError):
        get_content([2, 0])
