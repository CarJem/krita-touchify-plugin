from typing import TYPE_CHECKING
from PyQt5 import *
from PyQt5.QtWidgets import *
from krita import *

from touchify.src.api_krita.wrappers.window import WindowAPI
from touchify.src.components.toolshelf_legacy.ToolshelfDockWidget import ToolshelfDockWidget, ToolshelfDockWidgetAlt
from touchify.src.extensions.krita_extensions import KritaExtensions
from touchify.src.managers.normal.canvas import CanvasManager
from touchify.src.managers.normal.developer import DeveloperManager
from touchify.__env__ import *
from touchify.src.managers.normal.dockers import DockerManager
from touchify.src.managers.normal.action_manager import ActionManager


from touchify.src.managers.normal.shortcuts import ShortcutsManager
from touchify.src.managers.normal.tweaks import TweakManager


from touchify.src.components.toolshelf.ShelfDockWidget import ShelfDockWidget, ShelfDockWidgetAlt
from touchify.src.components.toolbox.ToolboxDocker import ToolboxDocker

if TYPE_CHECKING:
    from .Plugin import TouchifyWindow

class TouchifyManagers:
    def __init__(self, window: "TouchifyWindow"):
        self.__window__ = window

        self.mgr_tweaker = TweakManager(window)
        self.mgr_shortcuts = ShortcutsManager(window)
        self.mgr_canvas = CanvasManager(window, self)
        self.mgr_dev = DeveloperManager(window)
        self.mgr_actions = ActionManager(window, self)

    def api_window(self):
        return self.__window__.api_window

    def Load(self, window: "TouchifyWindow"):
        self.mgr_dockers = DockerManager(window)
        self.mgr_actions.Window_Load(window.api_window)
        self.mgr_shortcuts.Window_Load()
        self.mgr_tweaker.Window_Load()
        self.mgr_canvas.Window_Load(window.api_window)

    def Addons(self, window: "TouchifyWindow"):
        dockers_menu_action = KritaExtensions.getDockerMenu(window.api_window)
        if dockers_menu_action == None: return

        touchify_title_prefix = "Touchify Core: "
        addon_title_prefix = "Touchify Addon: "

        addon_id_prefix = "Touchify/"
        addon_setup_method = "TOUCHIFY_ADDON_SETUP"
        
        addons_list: list[QAction] = []
        core_list: list[QAction] = []

        for docker_action in dockers_menu_action.menu().actions():
            docker_text = docker_action.text()

            if docker_text.startswith(addon_title_prefix): 
                docker_action.setText(docker_text.removeprefix(addon_title_prefix))
                addons_list.append(docker_action)
                
            if docker_text.startswith(touchify_title_prefix):
                docker_action.setText(docker_text.removeprefix(touchify_title_prefix))
                core_list.append(docker_action)
                
        dockers_menu_action.menu().addSection("Touchify Core")
        for act in core_list: dockers_menu_action.menu().addAction(act)

        dockers_menu_action.menu().addSection("Touchify Addons")
        for act in addons_list: dockers_menu_action.menu().addAction(act)

        for docker in window.api_window.dockers:
            window_title = docker.windowTitle()
            docker_id = docker.objectName()

            if window_title.startswith(addon_title_prefix):
                docker.setWindowTitle(window_title.removeprefix(addon_title_prefix))

            if window_title.startswith(touchify_title_prefix):
                docker.setWindowTitle(window_title.removeprefix(touchify_title_prefix))

            if docker_id == TOUCHIFY_DOCKERID_TOOLSHELFDOCKER_ALT:
                toolshelfAltDocker: ShelfDockWidget = docker
                toolshelfAltDocker.setup(window)
            elif docker_id == TOUCHIFY_DOCKERID_TOOLSHELFDOCKER:
                toolshelfDocker: ShelfDockWidgetAlt = docker
                toolshelfDocker.setup(window)
            elif docker_id == TOUCHIFY_DOCKERID_TOOLSHELFDOCKER_ALT_LEGACY:
                toolshelfAltDocker: ToolshelfDockWidget = docker
                toolshelfAltDocker.setup(window)
            elif docker_id == TOUCHIFY_DOCKERID_TOOLSHELFDOCKER_LEGACY:
                toolshelfDocker: ToolshelfDockWidgetAlt = docker
                toolshelfDocker.setup(window)
            elif docker_id == TOUCHIFY_DOCKERID_DOCKER_TOOLBOX:
                toolboxDocker: ToolboxDocker = docker
                toolboxDocker.setup(window)
            else:
                if not docker_id.startswith(addon_id_prefix): pass
                elif not hasattr(docker, addon_setup_method): pass
                elif not callable(getattr(docker, addon_setup_method, False)): pass
                else: getattr(docker, addon_setup_method)(window)

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
