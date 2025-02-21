
from touchify.src.Plugin import TouchifyPlugin
from touchify.__env__ import *
from touchify.src.api_krita import KritaAPI
from touchify.src.api_krita.wrappers.docker_factory import DockWidgetFactoryAPI
from touchify.src.components.toolshelf.ToolshelfDockWidget import ToolshelfDockWidget
from touchify.src.components.toolbox.ToolboxDocker import ToolboxDocker

KritaAPI.add_extension(TouchifyPlugin)
KritaAPI.add_dock_widget_factory(TOUCHIFY_DOCKERID_TOOLSHELFDOCKER, DockWidgetFactoryAPI.DockPosition.DockRight, ToolshelfDockWidget)
KritaAPI.add_dock_widget_factory(TOUCHIFY_DOCKERID_DOCKER_TOOLBOX, DockWidgetFactoryAPI.DockPosition.DockRight, ToolboxDocker)