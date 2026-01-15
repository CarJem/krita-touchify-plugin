from typing import TYPE_CHECKING
from PyQt5 import *
from PyQt5.QtWidgets import *
from jemlib.alib_vaporjem import Logger
from krita import *

from jemlib.api_krita.wrappers.window import WindowAPI

from touchify.src.components.toolshelf.ToolshelfDockerWidgetPad import ToolshelfDockerWidgetPad
from jemlib.alib_vaporjem.extensions.krita_extensions import KritaExtensions
from touchify.src.managers.ToolOptionsManager import ToolOptionsManager
from touchify.src.managers.CanvasManager import CanvasManager
from touchify.src.managers.DeveloperManager import DeveloperManager
from jemlib.api_touchify.env import *
from touchify.src.managers.DockerManager import DockerManager
from touchify.src.managers.ActionManager import ActionManager


from touchify.src.managers.ShortcutManager import ShortcutsManager
from touchify.src.managers.TweakManager import TweakManager


from touchify.src.components.toolshelf.ToolshelfDockerWidget import ToolshelfDockerWidget
from touchify.src.components.toolbox.ToolboxDocker import ToolboxDocker
from touchify.src.managers.WidgetPadManager import WidgetPadManager
from touchify_quick_actions.QuickActionsDocker import QuickActionsDocker

if TYPE_CHECKING:
    from .Plugin import TouchifyWindow

class TouchifyManagers:
    def __init__(self, window: "TouchifyWindow"):
        self.__window__ = window

        self.__managedDockers: list[QDockWidget] = []

        self.mgr_tweaker = TweakManager(window)
        self.mgr_shortcuts = ShortcutsManager(window)
        self.mgr_canvas = CanvasManager(window, self)
        self.mgr_dev = DeveloperManager(window)
        self.mgr_actions = ActionManager(window, self)
        self.mgr_widgetpad = WidgetPadManager(window, self)
        self.mgr_tooloptions = ToolOptionsManager(window, self)

    def api_window(self):
        return self.__window__.api_window

    def Load(self, window: "TouchifyWindow"):
        self.mgr_dockers = DockerManager(window.api_window)
        self.mgr_actions.Window_Load(window.api_window)
        self.mgr_shortcuts.Window_Load()
        self.mgr_tweaker.Window_Load()
        self.mgr_canvas.Window_Load(window.api_window)
        self.mgr_widgetpad.Window_Load(window)
        self.mgr_tooloptions.Window_Load(window)

    def Reload(self):
        Logger.logDebug("Touchify", "TouchifyManagers", "Reload", "started")
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
        dockers_menu_action = KritaExtensions.getDockerMenu(window.api_window)
        if dockers_menu_action == None: return

        touchify_title_prefix = TouchifyEnv.Title.CORE_DOCKERS_PREFIX
        addon_title_prefix = TouchifyEnv.Title.ADDON_DOCKERS_PREFIX
        touchify_clone_prefix = TouchifyEnv.Title.CLONE_DOCKERS_PREFIX

        addon_id_prefix = "Touchify/"
        addon_setup_method = "TOUCHIFY_ADDON_SETUP"
        
        addons_list: list[QAction] = []
        core_list: list[QAction] = []
        toolshelves_list: list[QAction] = []
        widgetpads_list: list[QAction] = []

        for docker_action in dockers_menu_action.menu().actions():
            docker_text = docker_action.text()

            if docker_text.startswith(addon_title_prefix): 
                docker_action.setText(docker_text.removeprefix(addon_title_prefix))
                addons_list.append(docker_action)  
            elif docker_text.startswith(touchify_title_prefix):
                docker_action.setText(docker_text.removeprefix(touchify_title_prefix))
                core_list.append(docker_action)
            elif docker_text.startswith(touchify_clone_prefix):
                if docker_text.startswith(ToolshelfDockerWidget.CLONE_DOCKER_TITLE):
                    docker_action.setText(docker_text.removeprefix(touchify_clone_prefix))
                    toolshelves_list.append(docker_action)
                elif docker_text.startswith(ToolshelfDockerWidgetPad.CLONE_DOCKER_TITLE):
                    docker_action.setText(docker_text.removeprefix(touchify_clone_prefix))
                    widgetpads_list.append(docker_action)
                
        dockers_menu_action.menu().addSection("Touchify Core")
        for act in core_list: dockers_menu_action.menu().addAction(act)

        dockers_menu_action.menu().addSection("Touchify Addons")
        for act in addons_list: dockers_menu_action.menu().addAction(act)

        dockers_menu_action.menu().addSection("Toolshelves")
        for act in toolshelves_list: dockers_menu_action.menu().addAction(act)

        dockers_menu_action.menu().addSection("Widget Pads")
        for act in widgetpads_list: dockers_menu_action.menu().addAction(act)

        for docker in window.api_window.dockers:
            window_title = docker.windowTitle()
            docker_id = docker.objectName()

            if window_title.startswith(addon_title_prefix):
                window_title = window_title.removeprefix(addon_title_prefix)
                docker.setWindowTitle(window_title)
            elif window_title.startswith(touchify_title_prefix):
                window_title = window_title.removeprefix(touchify_title_prefix)
                docker.setWindowTitle(window_title)
            elif window_title.startswith(touchify_clone_prefix):
                window_title = window_title.removeprefix(touchify_clone_prefix)
                docker.setWindowTitle(window_title)

            if docker_id.startswith(TouchifyEnv.DockerID.TOOLSHELFDOCKER):
                toolshelfDocker: ToolshelfDockerWidget = docker
                toolshelfDocker.setup(window)
                self.__managedDockers.append(toolshelfDocker)
            elif docker_id.startswith(TouchifyEnv.DockerID.WIDGETPAD):
                widgetPadDocker: ToolshelfDockerWidgetPad = docker
                widgetPadDocker.setup(window)
                self.__managedDockers.append(widgetPadDocker)
            elif docker_id == TouchifyEnv.DockerID.TOOLBOX:
                toolboxDocker: ToolboxDocker = docker
                toolboxDocker.setup(window)
                self.__managedDockers.append(toolboxDocker)
            elif docker_id == TouchifyEnv.DockerID.QUICK_ACTIONS:
                quickActionsDocker: QuickActionsDocker = docker
                quickActionsDocker.setup(window)
                self.__managedDockers.append(quickActionsDocker)
            else:
                if not docker_id.startswith(addon_id_prefix): pass
                elif not hasattr(docker, addon_setup_method): pass
                elif not callable(getattr(docker, addon_setup_method, False)): pass
                else: 
                    getattr(docker, addon_setup_method)(window)
                    self.__managedDockers.append(docker)

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
