from jemlib.api_touchify.env import *
from jemlib.api_krita import KritaAPI
from jemlib.api_krita.wrappers.docker_factory import DockWidgetFactoryAPI
from touchify_toolbox.src.components.ToolboxDocker import ToolboxDocker
KritaAPI.add_dock_widget_factory(TouchifyEnv.DockerID.TOOLBOX, DockWidgetFactoryAPI.DockPosition.DockRight, ToolboxDocker)



    
    