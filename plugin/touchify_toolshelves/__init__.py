
from jemlib.api_touchify.env import *
from jemlib.api_krita import KritaAPI


if KritaAPI.read_setting("python", f"enable_{__name__}", "false").lower() == "true":
    from jemlib.api_krita.wrappers.docker_factory import DockWidgetFactoryAPI
    from touchify_toolshelves.Extension import TouchifyToolshelfExtension
    from touchify_toolshelves.src.components.ToolshelfDockerWidget import ToolshelfDockerWidget, DynamicToolshelfDockerWidget
    from touchify.src.settings.TouchifyPreferences import TouchifyPreferences
    from touchify_toolshelves.src.managers.WidgetPadManager import WidgetPadManager

    prefs = TouchifyPreferences(); prefs.load()
    KritaAPI.add_extension(TouchifyToolshelfExtension)
    KritaAPI.add_dock_widget_factory(TouchifyEnv.DockerID.TOOLSHELFDOCKER, DockWidgetFactoryAPI.DockPosition.DockLeft, ToolshelfDockerWidget)

    for idx in range(0, prefs.dockers.number_of_toolshelves):
        actual_id = idx + 1
        docker_name = TouchifyEnv.DockerID.TOOLSHELFDOCKER + "_" + str(actual_id)
        docker_class = DynamicToolshelfDockerWidget(actual_id)
        KritaAPI.add_dock_widget_factory(docker_name, DockWidgetFactoryAPI.DockPosition.DockTornOff, docker_class)
    
    if TouchifyToolshelfExtension.isDockWidgetMode(): WidgetPadManager.Dockers_Load(prefs.dockers.number_of_widgetpads)

    