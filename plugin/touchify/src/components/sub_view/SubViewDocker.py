
from krita import DockWidget
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from typing import TYPE_CHECKING


from touchify.__env__ import *

if TYPE_CHECKING:
    from ...PluginWindow import TouchifyWindow
    from touchify.src.PluginManagers import TouchifyManagers

class SubViewDocker(DockWidget):

    DOCKER_TITLE=f"{Env.Title.CORE_DOCKERS_PREFIX} Sub View"

    resizeByDefaultRequested=pyqtSignal()

    def __init__(self): 
        super().__init__()
        self.app_window: "TouchifyWindow" = None
        self.managers: "TouchifyManagers" = None
        self.setWindowTitle(SubViewDocker.DOCKER_TITLE)

    def setup(self, app_window: "TouchifyWindow"):
        self.app_window = app_window
        self.managers = app_window.managers

        from touchify.src.components.sub_view.SubViewWidget import SubViewWidget
        self.imageView = SubViewWidget(self)
        self.setWidget(self.imageView)
    
    def resizeEvent(self, a0):
        return super().resizeEvent(a0)
        
    def showEvent(self, event):
        super().showEvent(event)

    def closeEvent(self, event):
        return super().closeEvent(event)

    # notifies when views are added or removed
    # 'pass' means do not do anything
    def canvasChanged(self, canvas):
        pass

    def onThemeChanged(self):
        pass