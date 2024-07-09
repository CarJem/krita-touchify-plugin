

from krita import DockWidgetFactory, DockWidgetFactoryBase, Krita
from .dockers.ColorOptionsDocker import ColorOptionsDocker
from .dockers.BrushOptionsDocker import BrushOptionsDocker

Application.addDockWidgetFactory(DockWidgetFactory("ColorOptionsDocker", DockWidgetFactoryBase.DockRight, ColorOptionsDocker))
Application.addDockWidgetFactory(DockWidgetFactory("BrushOptionsDocker", DockWidgetFactoryBase.DockRight, BrushOptionsDocker))