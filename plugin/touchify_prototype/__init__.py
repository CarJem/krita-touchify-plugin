import sys
import os.path as path
PLUGIN_PYTHON_DIR = path.dirname(path.abspath(__file__))

sys.path.insert(0, path.join(PLUGIN_PYTHON_DIR, 'third_deps'))


from touchify_prototype.src.api_krita import KritaAPI
from touchify_prototype.src.api_krita.wrappers.docker_factory import DockWidgetFactoryAPI
from touchify_prototype.src.components.PrototypeDockWidget import PrototypeDockWidget


KritaAPI.add_dock_widget_factory("TouchifyPrototype", DockWidgetFactoryAPI.DockPosition.DockLeft, PrototypeDockWidget)