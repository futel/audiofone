import json
import os


def get_menus(menu_filename):
    """Return menus asset object."""
    filename = os.path.join(
        os.path.dirname(__file__), menu_filename)
    with open(filename) as f:
        return json.load(f)

def get_content_name(position, menu_plan):
    """Return menu content to play corresponding to position vector."""
    # eg () => "content" value of root elt
    # eg (2) => "content" value of 2nd elt of root elt
    # eg (1,3,2) => "content" value of 2nd elt of 3rd elt of 1st elt of root elt
    node = menu_plan
    for pos in position:
        try:
            node = node["destinations"][pos]
        except (KeyError, IndexError): # Invalid key for this node.
            return None
    return node["content"]
