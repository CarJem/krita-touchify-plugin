
from touchify.src.Plugin import TouchifyPlugin
from touchify.__env__ import *
from jemlib.api_krita import KritaAPI
from jemlib.api_krita.wrappers.docker_factory import DockWidgetFactoryAPI
from touchify.src.components.sub_view.SubViewDocker import SubViewDocker
from touchify.src.components.toolshelf.ToolshelfDockerWidget import ToolshelfDockerWidget, DynamicToolshelfDockerWidget
from touchify.src.components.toolbox.ToolboxDocker import ToolboxDocker
from touchify.src.components.toolshelf.ToolshelfDockerWidgetPad import DynamicToolshelfDockerWidgetPad


KritaAPI.add_extension(TouchifyPlugin)
KritaAPI.add_dock_widget_factory(Env.DockerID.TOOLSHELFDOCKER, DockWidgetFactoryAPI.DockPosition.DockLeft, ToolshelfDockerWidget)
KritaAPI.add_dock_widget_factory(Env.DockerID.TOOLBOX, DockWidgetFactoryAPI.DockPosition.DockRight, ToolboxDocker)
KritaAPI.add_dock_widget_factory(Env.DockerID.SUB_VIEW, DockWidgetFactoryAPI.DockPosition.DockTornOff, SubViewDocker)


for idx in range(0, 9):
    actual_id = idx + 1
    KritaAPI.add_dock_widget_factory(Env.DockerID.TOOLSHELFDOCKER + "_" + str(actual_id), DockWidgetFactoryAPI.DockPosition.DockTornOff, DynamicToolshelfDockerWidget(actual_id))
    KritaAPI.add_dock_widget_factory(Env.DockerID.WIDGETPAD + "_" + str(actual_id), DockWidgetFactoryAPI.DockPosition.DockTornOff, DynamicToolshelfDockerWidgetPad(actual_id))



    
    