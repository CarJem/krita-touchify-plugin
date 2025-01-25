from PyQt5 import *
from PyQt5.QtWidgets import *
from krita import *

from touchify.src.variables import *
from touchify.src.global_events import GlobalEvents




from touchify.src.components.touchify.dockers.toolshelf.ToolshelfDockWidget import ToolshelfDockWidget
from touchify.src.components.touchify.dockers.toolbox.ToolboxDocker import ToolboxDocker

from touchify.src.window import TouchifyWindow

class TouchifyExtension(Extension):

    instances: dict[str, TouchifyWindow] = {}
    setup_instance: bool = False
    new_instance: TouchifyWindow = None

    def __init__(self, parent):
        super().__init__(parent)
        self.event_handler = GlobalEvents(self)
        self.DEV_HOOK_FIND_PLUGIN = "TOUCHIFY"

        self.settings_clipboard_type: type | None = None
        self.settings_clipboard_data: any | None = None


    def setup(self):
        Krita.instance().notifier().windowCreated.connect(self.onWindowCreated)
        Krita.instance().notifier().configurationChanged.connect(self.onConfigurationChanged)


        self.intervalTimer = QTimer(self)
        self.intervalTimer.timeout.connect(GlobalEvents.EMIT_SIGNAL_TIMER_TICKED)
        self.intervalTimer.start(TOUCHIFY_TIMER_MAIN_INTERVAL)
    
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

    def getSettingsClipboard(self, requested_type: type):
        if self.settings_clipboard_type == requested_type:
            return self.settings_clipboard_data
        else: return None

    def setSettingsClipboard(self, item_type: type, item_data: any):
        self.settings_clipboard_type = item_type
        self.settings_clipboard_data = item_data


Krita.instance().addExtension(TouchifyExtension(Krita.instance()))
Krita.instance().addDockWidgetFactory(DockWidgetFactory(TOUCHIFY_ID_DOCKER_TOOLSHELFDOCKER, DockWidgetFactoryBase.DockPosition.DockRight, ToolshelfDockWidget))
Krita.instance().addDockWidgetFactory(DockWidgetFactory(TOUCHIFY_ID_DOCKER_TOOLBOX, DockWidgetFactoryBase.DockPosition.DockRight, ToolboxDocker))
