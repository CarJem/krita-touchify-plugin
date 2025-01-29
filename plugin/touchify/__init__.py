from krita import Krita, DockWidgetFactoryBase, DockWidgetFactory
from touchify.Plugin import TouchifyPlugin
from touchify.__env__ import *
from touchify.src.components.touchify.dockers.toolshelf.ToolshelfDockWidget import ToolshelfDockWidget
from touchify.src.components.touchify.dockers.toolbox.ToolboxDocker import ToolboxDocker

Krita.instance().addExtension(TouchifyPlugin(Krita.instance()))
Krita.instance().addDockWidgetFactory(DockWidgetFactory(TOUCHIFY_DOCKERID_TOOLSHELFDOCKER, DockWidgetFactoryBase.DockPosition.DockRight, ToolshelfDockWidget))
Krita.instance().addDockWidgetFactory(DockWidgetFactory(TOUCHIFY_DOCKERID_DOCKER_TOOLBOX, DockWidgetFactoryBase.DockPosition.DockRight, ToolboxDocker))