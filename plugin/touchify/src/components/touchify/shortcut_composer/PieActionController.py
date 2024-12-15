
from typing import NoReturn

from PyQt5.QtGui import QIcon


from krita import *
from composer_utils.label import LabelText, LabelTextColorizer
from core_components.controller_base import Controller
from touchify.src.components.touchify.shortcut_composer.PieAction import PieAction
from touchify.src.resources import ResourceManager

class PieActionController(Controller[PieAction]):
    """
    Gives access to krita actions.

    - Operates on `Action`
    - Does not have a default value.
    """

    TYPE = PieAction

    @staticmethod
    def item_activate(value: str) -> str:

        actual_value = value.split("::", 1)[0]

        """Activate the action."""
        try:
            Krita.instance().action(actual_value).trigger()
        except AttributeError:
            print(actual_value)

    @staticmethod
    def item_name(value: str) -> str:


        actual_values = value.split("::", 1)

        if len(actual_values) >= 3:
            actual_value = actual_values[2]
            krita_action_text = False
        else:
            actual_value = actual_values[0]
            krita_action_text = True
        


        """Return the name of this action."""
        try:
            if krita_action_text:
                return Krita.instance().action(actual_value).text().replace("&", "")
            else:
                return actual_value
        except AttributeError:
            return "---"

    @staticmethod
    def item_pretty_name(value: str) -> str:

        actual_values = value.split("::", 1)

        if len(actual_values) >= 3:
            actual_value = actual_values[2]
            krita_action_text = False
        else:
            actual_value = actual_values[0]
            krita_action_text = True
        
        """Return the name of this action."""
        try:
            if krita_action_text:
                return Krita.instance().action(actual_value).text().replace("&", "")
            else:
                return actual_value
        except AttributeError:
            return "---"

    @staticmethod
    def item_icon(value: str) -> QIcon:    
        """Return the icon of this action."""
        try:
            actual_value = value.split("::", 1)[1]
            return ResourceManager.iconLoader(actual_value)
        except AttributeError:
            return QIcon()

    @staticmethod
    def get_value() -> NoReturn:
        """Get currently active tool."""
        raise NotImplementedError()

    @staticmethod
    def set_value(value: PieAction) -> None:
        """Set a passed tool."""
        PieActionController.item_activate(value)

    def get_label(self, value: PieAction) -> QIcon | LabelText:
        """Forward the tools' icon."""
        icon = PieActionController.item_icon(value)
        if not icon.isNull():
            return icon
        return LabelText(
            value=PieActionController.item_name(value)[:3],
            color=LabelTextColorizer.action())

    def get_pretty_name(self, value: PieAction) -> str:
        """Forward enums' pretty name."""
        return PieActionController.item_pretty_name(value)