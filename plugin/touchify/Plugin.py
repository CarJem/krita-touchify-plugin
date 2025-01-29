from PyQt5 import *
from PyQt5.QtWidgets import *
from krita import *

from touchify.__env__ import *
from touchify.src.managers.shared.events import GlobalEvents

from touchify.PluginWindow import TouchifyWindow

class TouchifyPlugin(Extension):

    instances: dict[str, TouchifyWindow] = {}
    setup_instance: bool = False
    new_instance: TouchifyWindow = None

    def __init__(self, parent):
        super().__init__(parent)
        self.event_handler = GlobalEvents(self)
        self.DEV_HOOK_FIND_PLUGIN = "TOUCHIFY"


    def setup(self):
        Krita.instance().notifier().windowCreated.connect(self.onWindowCreated)
        Krita.instance().notifier().configurationChanged.connect(self.onConfigurationChanged)


        self.intervalTimer = QTimer(self)
        self.intervalTimer.timeout.connect(GlobalEvents.EMIT_SIGNAL_TIMER_TICKED)
        self.intervalTimer.start(250)
    
    def onWindowDestroyed(self, windowId: str):
        item: TouchifyWindow = self.instances[windowId]
        item.Window_Unload()
        item.deleteLater()
        del self.instances[windowId]

    def onWindowCreated(self):
        if not self.setup_instance: return

        window: Window | None = None
        window_id = self.new_instance.Window_UUID()

        for __window in Krita.instance().windows():
            if __window.qwindow().property("KRITA_TOUCHIFY_IS_LOADED") != True:
                __window.qwindow().setProperty("KRITA_TOUCHIFY_IS_LOADED", True)
                window = __window
        
        if window == None: return

        window.windowClosed.connect(lambda: self.onWindowDestroyed(window_id))
        self.instances[window_id] = self.new_instance
        self.instances[window_id].Window_Load(window)

        self.setup_instance = False

    def onConfigurationChanged(self):
        GlobalEvents.EMIT_SIGNAL_KRITA_CONFIG_UPDATED()

    def createActions(self, window: Window):
        self.setup_instance = True
        self.new_instance = TouchifyWindow(self)
        self.new_instance.Actions_Init(window)



