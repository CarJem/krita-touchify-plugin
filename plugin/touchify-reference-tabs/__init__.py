from krita import DockWidget, Canvas


from PyQt5.QtGui import *

from touchify.src.api_krita import KritaAPI
from touchify.src.api_krita.wrappers.docker_factory import DockWidgetFactoryAPI
from .DockerWidget import DockerWidget
from .extensions.native_actions import NativeActions


class ReferenceTabsDocker(DockWidget):

    def __init__(self):
        super().__init__()

        widget = DockerWidget(self)

        self.setWindowTitle("Touchify Addon: Reference Tabs")
        self.setWidget(widget)

    # This override is required.
    def canvasChanged(self, canvas: Canvas):
        NativeActions.OnEvent_CanvasChanged(canvas)

KritaAPI.add_dock_widget_factory("Touchify/ReferenceTabsDocker", DockWidgetFactoryAPI.DockPosition.DockRight, ReferenceTabsDocker)

