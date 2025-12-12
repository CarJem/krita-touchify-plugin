
from touchify.src.Plugin import TouchifyPlugin
from touchify.__env__ import *
from touchify.src.api_krita import KritaAPI
from touchify.src.api_krita.wrappers.docker_factory import DockWidgetFactoryAPI
from touchify.src.components.toolshelf.ShelfDockWidget import ShelfDockWidget
from touchify.src.components.toolbox.ToolboxDocker import ToolboxDocker
from touchify.src.components.toolshelf.ShelfDockWidgetPad import ShelfWidgetPad

def DynamicShelfDockWidget(value: int):
    class DynamicShelfDockWidget(ShelfDockWidget):
        def __init__(self):
            super().__init__(value)
    
    return DynamicShelfDockWidget

def DynamicShelfWidgetPad(value: int):
    class DynamicShelfWidgetPad(ShelfWidgetPad):
        def __init__(self):
            super().__init__(value)

    return DynamicShelfWidgetPad


KritaAPI.add_extension(TouchifyPlugin)
KritaAPI.add_dock_widget_factory(Env.DockerID.TOOLSHELFDOCKER, DockWidgetFactoryAPI.DockPosition.DockLeft, ShelfDockWidget)
KritaAPI.add_dock_widget_factory(Env.DockerID.TOOLBOX, DockWidgetFactoryAPI.DockPosition.DockRight, ToolboxDocker)


for idx in range(0, 9):
    actual_id = idx + 1
    KritaAPI.add_dock_widget_factory(Env.DockerID.TOOLSHELFDOCKER + "_" + str(actual_id), DockWidgetFactoryAPI.DockPosition.DockTornOff, DynamicShelfDockWidget(actual_id))
    KritaAPI.add_dock_widget_factory(Env.DockerID.WIDGETPAD + "_" + str(actual_id), DockWidgetFactoryAPI.DockPosition.DockTornOff, DynamicShelfWidgetPad(actual_id))



    
    