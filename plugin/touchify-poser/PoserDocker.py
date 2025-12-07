
from krita import *
from PyQt5.QtCore import *

from touchify.src.api_krita import KritaAPI
from touchify.src.api_krita.wrappers.docker_factory import DockWidgetFactoryAPI

from touchify.__env__ import *

DOCKER_TITLE = 'Touchify Addon: Poser'
DOCKER_ID="Touchify/Poser"

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from touchify.src.PluginWindow import TouchifyWindow

class PoserDocker(DockWidget):

    def __init__(self): 
        super().__init__()
        self.setWindowTitle(DOCKER_TITLE)        

    
        #browser = QWebEngineView(self)
        #browser.setUrl("https://app.justsketch.me/")
        #self.setWidget(browser)

        #GlobalEvents.instance().SIGNAL_TOUCHIFY_CONFIG_UPDATED.connect(self.addonUpdateStyle)
        self.addonUpdateStyle()

    def TOUCHIFY_ADDON_SETUP(self, instance: "TouchifyWindow"):
        pass

    def addonUpdateStyle(self):
        pass

    def showEvent(self, event):
        super().showEvent(event)

    def closeEvent(self, event):
        super().closeEvent(event)

    # notifies when views are added or removed
    # 'pass' means do not do anything
    def canvasChanged(self, canvas):
        pass

KritaAPI.add_dock_widget_factory(DOCKER_ID, DockWidgetFactoryAPI.DockPosition.DockRight, PoserDocker)

