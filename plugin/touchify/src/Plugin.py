from PyQt5 import *
from PyQt5.QtWidgets import *
from krita import *

from jemlib.api_touchify.env import *
from jemlib.api_krita import KritaAPI
from jemlib.api_krita.wrappers.window import WindowAPI
from jemlib.managers.GlobalEvents import GlobalEvents

from jemlib.alib_vaporjem import Logger
from touchify.src.PluginWindow import TouchifyWindow

class TouchifyPlugin(Extension):
    

    instances: dict[str, TouchifyWindow] = {}
    setup_instance: bool = False
    new_instance: TouchifyWindow = None

    def __init__(self, parent):
        super().__init__(parent)
        GlobalEvents(self)
        self.DEV_HOOK_FIND_PLUGIN = "TOUCHIFY"

    def setup(self):
        KritaAPI.notifier().add_window_created_callback(self.onWindowCreated)
        KritaAPI.notifier().add_configuration_changed_callback(self.onConfigurationChanged)
        GlobalEvents().setup()
    
    def onWindowDestroyed(self, windowId: str):
        item: TouchifyWindow = self.instances[windowId]
        item.Unload()
        item.deleteLater()
        del self.instances[windowId]

    def onWindowCreated(self):
        if not self.setup_instance: return
        window: WindowAPI | None = None
        window_id = self.new_instance.INSTANCE_ID

        for __window in KritaAPI.get_windows():
            if __window.qwindow.property("KRITA_TOUCHIFY_IS_LOADED") != True:
                __window.qwindow.setProperty("KRITA_TOUCHIFY_IS_LOADED", True)
                window = __window
        
        if window == None: return

        window.windowClosed.connect(lambda: self.onWindowDestroyed(window_id))
        self.instances[window_id] = self.new_instance
        Logger.debug("Touchify", "Plugin","window_load")
        self.instances[window_id].Load(window)
        Logger.debug("Touchify", "Plugin","window_load_done")

        self.setup_instance = False

    def onConfigurationChanged(self):
        GlobalEvents().SIGNAL_KRITA_CONFIG_UPDATED.emit()

    def createActions(self, window: Window):
        Logger.debug("Touchify", "Plugin","create_actions")
        self.setup_instance = True
        self.new_instance = TouchifyWindow(self)
        self.new_instance.LoadActions(WindowAPI(window))
        Logger.debug("Touchify", "Plugin","create_actions_done")



