
from typing import NoReturn

from PyQt5.QtGui import QIcon


from krita import *
#from jemlib.api_composer.action import PieAction
from jemlib.api_krita import KritaAPI
from shortcut_composer.core_components.controller_base import Controller
from shortcut_composer.composer_utils.label.label_text import LabelText
from shortcut_composer.api_krita.enums.helpers import EnumGroup
from jemlib.alib_vaporjem.extensions.json_extensions import JsonExtensions
from jemlib.managers.IconRepository import IconRepository
from touchify.src.components.pie_wheel.api_composer.touchify_constants import SEPERATOR


from touchify.src.config.triggers.Trigger import Trigger
from jemlib.managers.GlobalEvents import GlobalEvents
    
class PieAction(EnumGroup):
    def __new__(cls, value):
        setattr(value, "PLACEHOLDER", "PLACEHOLDER")
        super().__new__(cls, value)

class PieActionController(Controller[PieAction]):
    """
    Gives access to krita actions.

    - Operates on `Action`
    - Does not have a default value.
    """

    TYPE = PieAction

    @staticmethod
    def item_activate(value: str) -> str:

        actual_value = value.split(SEPERATOR, -1)[0]
        

        """Activate the action."""
        try:
            triggerResult = JsonExtensions.loadClass(actual_value, Trigger)
            GlobalEvents().SIGNAL_PIE_TRIGGER_SENT.emit(triggerResult)
        except AttributeError:
            print(actual_value)

    @staticmethod
    def item_name(value: str) -> str:

        
        actual_values = value.split(SEPERATOR, -1)

        if len(actual_values) >= 3:
            actual_value = actual_values[2]
            krita_action_text = False
        else:
            actual_value = actual_values[0]
            krita_action_text = True
        


        """Return the name of this action."""
        try:
            if krita_action_text:
                return KritaAPI.get_action(actual_value).text().replace("&", "")
            else:
                return actual_value
        except AttributeError:
            return "---"

    @staticmethod
    def item_pretty_name(value: str) -> str:

        actual_values = value.split(SEPERATOR, 1)

        if len(actual_values) >= 3:
            actual_value = actual_values[2]
            krita_action_text = False
        else:
            actual_value = actual_values[0]
            krita_action_text = True
        
        """Return the name of this action."""
        try:
            if krita_action_text:
                return KritaAPI.get_action(actual_value).text().replace("&", "")
            else:
                return actual_value
        except AttributeError:
            return "---"

    @staticmethod
    def item_icon(value: str) -> QIcon:    
        """Return the icon of this action."""
        try:
            print(value)
            actual_value = value.split(SEPERATOR, -1)[1]
            return IconRepository.iconLoader(actual_value)
        except AttributeError:
            return QIcon()
        except IndexError:
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
        return QIcon()
        #return LabelText(
            #value=PieActionController.item_name(value)[:3],
            #color=LabelTextColorizer.action())

    def get_pretty_name(self, value: PieAction) -> str:
        """Forward enums' pretty name."""
        return PieActionController.item_pretty_name(value)