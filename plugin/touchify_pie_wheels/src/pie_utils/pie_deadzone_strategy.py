from enum import Enum


class PieDeadzoneStrategy(Enum):
    """
    Enumeration of actions that can be done on deadzone key release in Pie.

    Values are strings meant for being displayed in the UI.
    """
    DO_NOTHING = "Do nothing"
    """No action is needed."""
    PICK_TOP = "Pick top"
    """Label on the top is activated."""
    PICK_PREVIOUS = "Pick previous"
    """Previously selected label is activated."""