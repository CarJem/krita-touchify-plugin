from typing import TYPE_CHECKING, Any
from PyQt5 import *
from PyQt5.QtWidgets import *
from jemlib.alib_vaporjem import Logger
from krita import *

from jemlib.api_krita.wrappers.window import WindowAPI
from jemlib.alib_vaporjem.extensions.krita_extensions import KritaExtensions
from touchify.src.managers.ToolOptionsManager import ToolOptionsManager
from touchify.src.managers.CanvasManager import CanvasManager
from touchify.src.managers.DeveloperManager import DeveloperManager
from jemlib.api_touchify.env import *
from touchify.src.managers.DockerManager import DockerManager
from touchify.src.managers.ActionManager import ActionManager


from touchify.src.managers.ShortcutManager import ShortcutsManager
from touchify.src.managers.TweakManager import TweakManager




if TYPE_CHECKING:
    from .Plugin import TouchifyWindow




class TouchifyManagers:
    def __init__(self, window: "TouchifyWindow"):
        self.__window__ = window

        self.__externalManagers: dict[str, any] = {}
        self.__managedDockers: list[QDockWidget] = []

        self.mgr_tweaker = TweakManager(window)
        self.mgr_shortcuts = ShortcutsManager(window)
        self.mgr_canvas = CanvasManager(window, self)
        self.mgr_dev = DeveloperManager(window)
        self.mgr_actions = ActionManager(window, self)
        self.mgr_tooloptions = ToolOptionsManager(window, self)

    def api_window(self):
        return self.__window__.api_window

    def Load(self, window: "TouchifyWindow"):
        self.mgr_dockers = DockerManager(window.api_window)
        self.mgr_actions.Window_Load(window.api_window)
        self.mgr_shortcuts.Window_Load()
        self.mgr_tweaker.Window_Load()
        self.mgr_canvas.Window_Load(window.api_window)
        self.mgr_tooloptions.Window_Load(window)
        

    def Reload(self):
        Logger.logDebug("Touchify", "TouchifyManagers", "Reload", "started")
        self.mgr_tweaker.Window_Reload()
        self.mgr_actions.Window_Reload()
        for docker in self.__managedDockers:
            if not hasattr(docker, "onTouchifyReload"): pass
            elif not callable(getattr(docker, "onTouchifyReload", False)): pass
            else: 
                Logger.logDebug("Touchify", "TouchifyManagers", "Reload", f"calling_docker_reload_fn: {docker.objectName()}")
                getattr(docker, "onTouchifyReload")()

    def ReloadTheme(self):
        for docker in self.__managedDockers:
            if not hasattr(docker, "onThemeChanged"): pass
            elif not callable(getattr(docker, "onThemeChanged", False)): pass
            else: getattr(docker, "onThemeChanged")()

    def Addons(self, window: "TouchifyWindow"):

        def tryAddPluginToList(action: QAction, text: str, prefix: str, items: list[QAction]):
            if text.startswith(prefix): 
                action.setText(text.removeprefix(prefix))
                items.append(action)  
                return True
            else:
                return False
            
        def trySetPluginTitle(docker: QDockWidget, window_title: str, prefix: str):
            if window_title.startswith(prefix):
                window_title = window_title.removeprefix(prefix)
                docker.setWindowTitle(window_title)
                return True
            else:
                return False
            
        def trySetupPlugin(docker_id: str, docker: QDockWidget, current_window: "TouchifyWindow", condition: bool, items: list[QDockWidget]):
            try:
                if condition:
                    docker.setup(current_window)
                    items.append(docker)
                    return True
                else:
                    return False
            except Exception as ex:
                Logger.logError("Touchify", "TouchifyManagers", "Addons", f"failed to setup plugin for \"{docker_id}\": {ex}")
                return False
        
        def trySetupGenericPlugin(docker_id: str, docker: QDockWidget, current_window: "TouchifyWindow", items: list[QDockWidget]):
            addon_setup_method = "TOUCHIFY_ADDON_SETUP"
            try:
                if not hasattr(docker, addon_setup_method): 
                    return False
                elif not callable(getattr(docker, addon_setup_method, False)): 
                    return False
                else: 
                    getattr(docker, addon_setup_method)(current_window)
                    items.append(docker)
                    return True
            except Exception as ex:
                Logger.logError("Touchify", "TouchifyManagers", "Addons", f"failed to setup generic plugin for \"{docker_id}\": {ex}")
                return False

        def addSectionAndAddItems(title: str, source: QAction, items: list[QAction]):
            if len(items) != 0:
                source.menu().addSection(title)
                for act in items: source.menu().addAction(act)

        dockers_menu_action = KritaExtensions.getDockerMenu(window.api_window)
        if dockers_menu_action == None: return

        touchify_title_prefix = TouchifyEnv.Title.CORE_DOCKERS_PREFIX
        touchify_addon_title_prefix = TouchifyEnv.Title.ADDON_DOCKERS_PREFIX
        touchify_toolshelf_prefix = TouchifyEnv.Title.TOOLSHELF_DOCKERS_PREFIX
        touchify_widgetpad_prefix = TouchifyEnv.Title.WIDGETPAD_DOCKERS_PREFIX

        addons_list: list[QAction] = []
        core_list: list[QAction] = []
        toolshelves_list: list[QAction] = []
        widgetpads_list: list[QAction] = []

        for docker_action in dockers_menu_action.menu().actions():
            docker_text = docker_action.text()
            if tryAddPluginToList(docker_action, docker_text, touchify_addon_title_prefix, addons_list): pass
            elif tryAddPluginToList(docker_action, docker_text, touchify_title_prefix, core_list): pass
            elif tryAddPluginToList(docker_action, docker_text, touchify_toolshelf_prefix, toolshelves_list): pass
            elif tryAddPluginToList(docker_action, docker_text, touchify_widgetpad_prefix, widgetpads_list): pass
                
        addSectionAndAddItems("Touchify Core", dockers_menu_action, core_list)
        addSectionAndAddItems("Touchify Addons", dockers_menu_action, addons_list)
        addSectionAndAddItems("Toolshelves", dockers_menu_action, toolshelves_list)
        addSectionAndAddItems("Widget Pads", dockers_menu_action, widgetpads_list)

        for docker in window.api_window.dockers:
            window_title = docker.windowTitle()
            docker_id = docker.objectName()

            if trySetPluginTitle(docker, window_title, touchify_title_prefix): pass
            elif trySetPluginTitle(docker, window_title, touchify_addon_title_prefix): pass
            elif trySetPluginTitle(docker, window_title, touchify_toolshelf_prefix): pass
            elif trySetPluginTitle(docker, window_title, touchify_widgetpad_prefix): pass

            if trySetupPlugin(docker_id, docker, window, docker_id.startswith(TouchifyEnv.DockerID.TOOLSHELFDOCKER), self.__managedDockers): pass
            elif trySetupPlugin(docker_id, docker, window, docker_id.startswith(TouchifyEnv.DockerID.WIDGETPAD), self.__managedDockers): pass
            elif trySetupPlugin(docker_id, docker, window, docker_id == TouchifyEnv.DockerID.TOOLBOX, self.__managedDockers): pass
            elif trySetupPlugin(docker_id, docker, window, docker_id == TouchifyEnv.DockerID.QUICK_ACTIONS, self.__managedDockers): pass
            elif trySetupGenericPlugin(docker_id, docker, window, self.__managedDockers): pass

    def Plugins(self, window: "TouchifyWindow"):

        def trySetupGenericPlugin(extension: Extension, current_window: "TouchifyWindow"):
            addon_setup_method = "TOUCHIFY_ADDON_SETUP"
            try:
                if not hasattr(extension, addon_setup_method): 
                    return False
                elif not callable(getattr(extension, addon_setup_method, False)): 
                    return False
                else: 
                    getattr(extension, addon_setup_method)(self, current_window)
                    return True
            except Exception as ex:
                Logger.logError("Touchify", "TouchifyManagers", "Plugins", f"failed to setup generic plugin for \"{extension.objectName()}\": {ex}")
                return False

        for i in Krita.instance().extensions(): trySetupGenericPlugin(i, window)

    def Actions(self, window: WindowAPI):
        self.mgr_shortcuts.Actions_Init(window, "tools/touchify", "settings")
        self.mgr_actions.Actions_Init(window, "tools/touchify")  
        self.mgr_dev.Actions_Init(window, "settings")
        self.mgr_tweaker.Actions_Init(window, "settings")
        self.mgr_canvas.Actions_Init(window, "settings")

    def ActionWidgets(self, window: "TouchifyWindow"):
        self.mgr_shortcuts.Actions_Post()
        self.mgr_tweaker.Actions_Post()
        self.mgr_canvas.Actions_Post()
        self.mgr_actions.Actions_Post(window.action_plugin_tools_menu)
        self.mgr_dev.Actions_Post(window.action_plugin_tools_menu)

    def External_Load(self, id: str, mgr: Any, window: "TouchifyWindow") -> Any | None:
        if id in self.__externalManagers:
            return self.__externalManagers[id]
        try:
            result = mgr(window, self)
            result.Window_Load(window)
            self.__externalManagers[id] = result
            return result
        except Exception as ex:
            Logger.logError("Touchify", "TouchifyManagers", "Inject", f"failed to setup external manager for \"{id}\": {ex}")
            return False

    def External_Get(self, id: str):
        if id in self.__externalManagers:
            return self.__externalManagers[id]
        else:
            return None
