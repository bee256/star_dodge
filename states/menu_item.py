from enum import Enum

class MenuItemType(Enum):
    SELECT = 1
    TOGGLE = 2
    ENTRY = 3

class MenuItem:
    def __init__(self, name: str, display_text: str, mitype: MenuItemType, position: (int, int), is_visible: bool):
        self.name = name
        self.display_text = display_text
        self.mitype = mitype
        self.pos_x = position[0]
        self.pos_x = position[1]
        self.is_visible = is_visible
