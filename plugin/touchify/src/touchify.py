from uuid import UUID, uuid4
import uuid
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import *

from . import stylesheet
from PyQt5.QtWidgets import QMessageBox
from .variables import *


from .settings import *
from .features.touchify_tweaks import *
from .features.docker_toggles import *
from .features.docker_groups import *
from .features.popup_buttons import *
from .features.workspace_toggles import *
from .features.redesign_components import *
from .features.touchify_hotkeys import *
from .instance import *



from krita import *

class Touchify(Extension):

    instances: dict[str, TouchifyInstance] = {}
    instance_generate: bool = False
    instance_generated: TouchifyInstance = None

    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("touchify_extension")

    def setup(self):
        Krita.instance().notifier().windowCreated.connect(self.onWindowCreated)
        ConfigManager.instance().notifyConnect(self.onConfigUpdated)
        KritaSettings.notifyConnect(self.onKritaConfigUpdated)

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
            print(f"New Window Hash: {window_hash}")
            return window
    
    def onWindowDestroyed(self, windowId: str):
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
        self.instance_generated = TouchifyInstance()
        self.instance_generated.createActions(window)

Krita.instance().addExtension(Touchify(Krita.instance()))