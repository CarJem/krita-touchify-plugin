
from jemlib.api_krita import KritaAPI
from jemlib.api_krita.wrappers.docker_factory import DockWidgetFactoryAPI
from jemlib.api_touchify.env import TouchifyEnv
from krita import DockWidget
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *



class SubViewDocker(DockWidget):

    DOCKER_TITLE=f"{TouchifyEnv.Title.ADDON_DOCKERS_PREFIX} Sub View"

    resizeByDefaultRequested=pyqtSignal()

    def __init__(self): 
        super().__init__()
        self.setWindowTitle(SubViewDocker.DOCKER_TITLE)

        from touchify_sub_view.SubViewWidget import SubViewWidget
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
        if self.imageView:
            self.imageView.onThemeChanged()

KritaAPI.add_dock_widget_factory(TouchifyEnv.DockerID.SUB_VIEW, DockWidgetFactoryAPI.DockPosition.DockTornOff, SubViewDocker)