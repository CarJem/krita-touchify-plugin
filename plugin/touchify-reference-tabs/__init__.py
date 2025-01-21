from krita import Krita, DockWidget, DockWidgetFactory, DockWidgetFactoryBase, Canvas


from PyQt5.QtGui import *
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

Krita.instance().addDockWidgetFactory(DockWidgetFactory("Touchify/ReferenceTabsDocker", DockWidgetFactoryBase.DockPosition.DockRight, ReferenceTabsDocker))

