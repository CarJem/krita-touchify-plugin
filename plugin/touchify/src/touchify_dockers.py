
from krita import DockWidgetFactory, DockWidgetFactoryBase, Krita
from .dockers.ColorOptionsDocker import ColorOptionsDocker
from .dockers.BrushOptionsDocker import BrushOptionsDocker

Krita.instance().addDockWidgetFactory(DockWidgetFactory("ColorOptionsDocker", DockWidgetFactoryBase.DockRight, ColorOptionsDocker))
Krita.instance().addDockWidgetFactory(DockWidgetFactory("BrushOptionsDocker", DockWidgetFactoryBase.DockRight, BrushOptionsDocker))