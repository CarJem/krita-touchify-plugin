
from touchify.src.Plugin import TouchifyPlugin
from touchify.__env__ import *
from touchify.src.api_krita import KritaAPI
from touchify.src.api_krita.wrappers.docker_factory import DockWidgetFactoryAPI
from touchify.src.components.toolshelf.ShelfDockWidget import *
from touchify.src.components.toolbox.ToolboxDocker import ToolboxDocker
from touchify.src.components.toolshelf.ShelfDockWidgetPad import *

def makeDynamicShelfWidget(value: int, widgetPad: bool):
    class A(ShelfDockWidget):
        def __init__(self):
            super().__init__(value)

    class B(ShelfWidgetPad):
        def __init__(self):
            super().__init__(value)

    return B if widgetPad else A


KritaAPI.add_extension(TouchifyPlugin)
KritaAPI.add_dock_widget_factory(TOUCHIFY_DOCKERID_TOOLSHELFDOCKER, DockWidgetFactoryAPI.DockPosition.DockLeft, ShelfDockWidget)
KritaAPI.add_dock_widget_factory(TOUCHIFY_DOCKERID_DOCKER_TOOLBOX, DockWidgetFactoryAPI.DockPosition.DockRight, ToolboxDocker)

for idx in range(0, 9):
    actual_id = idx + 1
    KritaAPI.add_dock_widget_factory(TOUCHIFY_DOCKERID_TOOLSHELFDOCKER + "_" + str(actual_id), DockWidgetFactoryAPI.DockPosition.DockTornOff, makeDynamicShelfWidget(actual_id, False))
    KritaAPI.add_dock_widget_factory(TOUCHIFY_DOCKERID_WIDGETPAD + "_" + str(actual_id), DockWidgetFactoryAPI.DockPosition.DockTornOff, makeDynamicShelfWidget(actual_id, True))

    
    