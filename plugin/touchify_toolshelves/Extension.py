from typing import TYPE_CHECKING
from krita import *

from touchify_toolshelves.src.managers.WidgetPadManager import WidgetPadManager


if TYPE_CHECKING:
    from touchify.src.PluginWindow import TouchifyWindow
    from touchify.src.PluginManagers import TouchifyManagers

class TouchifyToolshelfExtension(Extension):
    def __init__(self, parent):
        super().__init__(parent)

    def setup(self):
        pass
    
    @staticmethod
    def isDockWidgetMode():
        #result = KritaAPI.read_setting(TouchifyEnv.SettingsPath.WIDGETPAD, f"useDockWidgetsForWidgetPads", "false").lower() == "true"
        #return result
        return False

    def createActions(self, window):
        pass

    def TOUCHIFY_ADDON_SETUP(self, managers: "TouchifyManagers", window: "TouchifyWindow"):
        managers.External_Load("widgetpad", WidgetPadManager, window)
