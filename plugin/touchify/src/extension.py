from PyQt5 import *
from PyQt5.QtWidgets import *
from krita import *

from touchify.src.variables import *

from touchify.src.settings import TouchifyConfig


from touchify.src.ext.KritaSettings import KritaSettings

from touchify.src.components.touchify.dockers.toolshelf.ToolshelfDocker import ToolshelfDocker
from touchify.src.components.touchify.dockers.toolbox.ToolboxDocker import ToolboxDocker

from touchify.src.window import TouchifyWindow

class TouchifyExtension(Extension):

    instances: dict[str, TouchifyWindow] = {}
    instance_generate: bool = False
    instance_generated: TouchifyWindow = None

    intervalTimerTicked = pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)
        self.DEV_HOOK_FIND_PLUGIN = "TOUCHIFY"

        self.settings_clipboard_type: type | None = None
        self.settings_clipboard_data: any | None = None


    def setup(self):
        Krita.instance().notifier().windowCreated.connect(self.onWindowCreated)
        TouchifyConfig.instance().notifyConnect(self.onConfigUpdated)
        Krita.instance().notifier().configurationChanged.connect(self.onKritaConfigUpdated)
        KritaSettings.notifyConnect(self.onKritaConfigUpdated)

        self.intervalTimer = QTimer(self)
        self.intervalTimer.timeout.connect(self.onTimerTick)
        self.intervalTimer.start(TOUCHIFY_TIMER_MAIN_INTERVAL)

    def onTimerTick(self):
        self.intervalTimerTicked.emit()
        for id in self.instances:    
            self.instances[id].onActionTick()

    def onKritaConfigUpdated(self):
        for id in self.instances:
            self.instances[id].onKritaConfigUpdated()

    def onConfigUpdated(self):
        for id in self.instances:
            self.instances[id].onConfigUpdated()

    def getNewWindow(self):
        window = Krita.instance().activeWindow()
        window_hash = str(window.qwindow().windowHandle().__hash__())
        if window_hash not in self.instances:
            return window
    
    def onWindowDestroyed(self, windowId: str):
        item: TouchifyWindow = self.instances[windowId]
        item.unload()
        item.deleteLater()
        del self.instances[windowId]

    def onWindowCreated(self):
        if self.instance_generate:
            new_window = self.getNewWindow()
            new_window_id = str(new_window.qwindow().windowHandle().__hash__())
            new_window.windowClosed.connect(lambda: self.onWindowDestroyed(new_window_id))
            self.instances[new_window_id] = self.instance_generated
            self.instances[new_window_id].onWindowCreated(new_window)
            self.instance_generate = False

    def createActions(self, window: Window):
        self.instance_generate = True
        self.instance_generated = TouchifyWindow(self)
        self.instance_generated.createActions(window)

    def getSettingsClipboard(self, requested_type: type):
        print(f"Requested Clipboard Type:{str(requested_type)}")
        print(f"Current Clipboard Type:{str(self.settings_clipboard_type)}")
        if self.settings_clipboard_type == requested_type:
            return self.settings_clipboard_data
        else: return None

    def setSettingsClipboard(self, item_type: type, item_data: any):
        print(f"New Clipboard Type:{str(item_type)}")
        print(f"New Clipboard Data:{str(item_data)}")
        self.settings_clipboard_type = item_type
        self.settings_clipboard_data = item_data


Krita.instance().addExtension(TouchifyExtension(Krita.instance()))
Krita.instance().addDockWidgetFactory(DockWidgetFactory(TOUCHIFY_ID_DOCKER_TOOLSHELFDOCKER, DockWidgetFactoryBase.DockPosition.DockRight, ToolshelfDocker))
Krita.instance().addDockWidgetFactory(DockWidgetFactory(TOUCHIFY_ID_DOCKER_TOOLBOX, DockWidgetFactoryBase.DockPosition.DockRight, ToolboxDocker))
