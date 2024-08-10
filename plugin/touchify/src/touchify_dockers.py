
from krita import DockWidgetFactory, DockWidgetFactoryBase, Krita
from .components.touchify.dockers.ColorOptionsDocker import ColorOptionsDocker
from .components.touchify.dockers.BrushOptionsDocker import BrushOptionsDocker
from .components.touchify.dockers.TouchifyToolshelfDocker import TouchifyToolshelfDocker

Krita.instance().addDockWidgetFactory(DockWidgetFactory("ColorOptionsDocker", DockWidgetFactoryBase.DockRight, ColorOptionsDocker))
Krita.instance().addDockWidgetFactory(DockWidgetFactory("BrushOptionsDocker", DockWidgetFactoryBase.DockRight, BrushOptionsDocker))
Krita.instance().addDockWidgetFactory(DockWidgetFactory("TouchifyToolshelfDocker", DockWidgetFactoryBase.DockRight, TouchifyToolshelfDocker))