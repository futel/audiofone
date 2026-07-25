import json
import os

import pytest

import menu
from menu import get_content_name, get_menus


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


def test_empty_position_returns_initial_content():
    assert get_content_name([], SAMPLE_MENUS) == "root.wav"


def test_single_level_first_destination():
    assert get_content_name([0], SAMPLE_MENUS) == "a.wav"


def test_single_level_other_destinations():
    assert get_content_name([1], SAMPLE_MENUS) == "b.wav"
    assert get_content_name([2], SAMPLE_MENUS) == "c.wav"


def test_nested_two_levels():
    assert get_content_name([0, 0], SAMPLE_MENUS) == "a_a.wav"
    assert get_content_name([0, 1], SAMPLE_MENUS) == "a_b.wav"
    assert get_content_name([1, 0], SAMPLE_MENUS) == "b_a.wav"


def test_nested_three_levels():
    assert get_content_name([1, 1, 0], SAMPLE_MENUS) == "b_b_a.wav"


def test_leaf_node_without_destinations():
    """A destination with no "destinations" key is a valid leaf."""
    assert get_content_name([2], SAMPLE_MENUS) == "c.wav"


def test_does_not_mutate_position():
    """Callers should be able to reuse the position vector after the call."""
    position = [1, 1, 0]
    get_content_name(position, SAMPLE_MENUS)
    assert position == [1, 1, 0]


def test_does_not_mutate_menu_plan():
    """The passed-in menu tree is only read, never modified."""
    plan = json.loads(json.dumps(SAMPLE_MENUS))
    get_content_name([1, 1, 0], plan)
    assert plan == SAMPLE_MENUS


def test_out_of_range_index_raises():
    with pytest.raises(IndexError):
        get_content_name([9], SAMPLE_MENUS)


def test_descending_into_leaf_raises():
    """Navigating past a leaf (no "destinations") is a caller error."""
    with pytest.raises(KeyError):
        get_content_name([2, 0], SAMPLE_MENUS)


def test_none_position_raises():
    """position is iterated directly now, so None is not a valid vector."""
    with pytest.raises(TypeError):
        get_content_name(None, SAMPLE_MENUS)


# get_menus reads a bundled asset from disk, relative to the menu module.

def test_get_menus_returns_bundled_asset():
    """get_menus loads and parses the named file next to the module."""
    asset_path = os.path.join(os.path.dirname(menu.__file__), "menu.json")
    with open(asset_path) as f:
        expected = json.load(f)
    assert get_menus("menu.json") == expected


def test_get_menus_result_is_navigable_by_get_content_name():
    """The loaded asset works as the tree get_content_name walks."""
    plan = get_menus("menu.json")
    assert get_content_name([], plan) == plan["content"]


def test_get_menus_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        get_menus("does_not_exist.json")
