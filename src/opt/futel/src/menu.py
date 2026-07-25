import json
import os

menu_filename = 'menu.json'

def get_menus():
    """Return menus asset object."""
    filename = os.path.join(
        os.path.dirname(__file__), menu_filename)
    with open(filename) as f:
        return json.load(f)

menus = get_menus()

def get_content(position):
    """Return menu content to play for position vector."""
    node = menus
    for pos in position or []:
        node = node["destinations"][pos]
    return node["content"]
