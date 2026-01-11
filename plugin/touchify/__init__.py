
from touchify.src.Plugin import TouchifyPlugin
from jemlib.api_touchify.env import *
from jemlib.api_krita import KritaAPI
from jemlib.api_krita.wrappers.docker_factory import DockWidgetFactoryAPI

from touchify.src.components.toolshelf.ToolshelfDockerWidget import ToolshelfDockerWidget, DynamicToolshelfDockerWidget
from touchify.src.components.toolbox.ToolboxDocker import ToolboxDocker
from touchify.src.components.toolshelf.ToolshelfDockerWidgetPad import DynamicToolshelfDockerWidgetPad

KritaAPI.add_extension(TouchifyPlugin)
KritaAPI.add_dock_widget_factory(TouchifyEnv.DockerID.TOOLSHELFDOCKER, DockWidgetFactoryAPI.DockPosition.DockLeft, ToolshelfDockerWidget)
KritaAPI.add_dock_widget_factory(TouchifyEnv.DockerID.TOOLBOX, DockWidgetFactoryAPI.DockPosition.DockRight, ToolboxDocker)

for idx in range(0, 9):
    actual_id = idx + 1
    KritaAPI.add_dock_widget_factory(TouchifyEnv.DockerID.TOOLSHELFDOCKER + "_" + str(actual_id), DockWidgetFactoryAPI.DockPosition.DockTornOff, DynamicToolshelfDockerWidget(actual_id))
    KritaAPI.add_dock_widget_factory(TouchifyEnv.DockerID.WIDGETPAD + "_" + str(actual_id), DockWidgetFactoryAPI.DockPosition.DockTornOff, DynamicToolshelfDockerWidgetPad(actual_id))



    
    