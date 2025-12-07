
from touchify.src.Plugin import TouchifyPlugin
from touchify.__env__ import *
from touchify.src.api_krita import KritaAPI
from touchify.src.api_krita.wrappers.docker_factory import DockWidgetFactoryAPI
from touchify.src.components.toolshelf.ShelfDockWidget import *
from touchify.src.components.toolbox.ToolboxDocker import ToolboxDocker
from touchify.src.components.toolshelf.ShelfDockWidgets import ShelfDockWidgetsExt, ShelfDockWidgetsFlt

KritaAPI.add_extension(TouchifyPlugin)
KritaAPI.add_dock_widget_factory(TOUCHIFY_DOCKERID_TOOLSHELFDOCKER, DockWidgetFactoryAPI.DockPosition.DockLeft, ShelfDockWidget)
KritaAPI.add_dock_widget_factory(TOUCHIFY_DOCKERID_DOCKER_TOOLBOX, DockWidgetFactoryAPI.DockPosition.DockRight, ToolboxDocker)

for idx in range(0, len(ShelfDockWidgetsExt)):
    KritaAPI.add_dock_widget_factory(TOUCHIFY_DOCKERID_TOOLSHELFDOCKER_EXT + "_" + str(idx + 1), DockWidgetFactoryAPI.DockPosition.DockTornOff, ShelfDockWidgetsExt[idx])

for idx in range(0, len(ShelfDockWidgetsFlt)):
    KritaAPI.add_dock_widget_factory(TOUCHIFY_DOCKERID_TOOLSHELFDOCKER_EXT_FLT + "_" + str(idx + 1), DockWidgetFactoryAPI.DockPosition.DockTornOff, ShelfDockWidgetsFlt[idx])
