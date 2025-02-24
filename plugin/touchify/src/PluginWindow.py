from typing import TYPE_CHECKING
from PyQt5 import *
from PyQt5.QtWidgets import *
from krita import *

from touchify.src.api_krita.wrappers.window import WindowAPI
from touchify.src.extensions.krita_extensions import KritaExtensions
from touchify.src.managers.normal.canvas import CanvasManager
from touchify.src.managers.normal.developer import DeveloperManager
from touchify.__env__ import *
from touchify.src.managers.normal.dockers import DockerManager
from touchify.src.managers.normal.action_manager import ActionManager

from touchify.src.PluginOptions import PluginOptions

from touchify.src.managers.normal.shortcuts import ShortcutsManager
from touchify.src.managers.normal.tweaks import TweakManager

import touchify.src.extensions.pyqt_extensions as PyQtExtensions

from touchify.src.components.toolshelf.ToolshelfDockWidget import ToolshelfDockWidget
from touchify.src.components.toolbox.ToolboxDocker import ToolboxDocker

WINDOW_ID: int = 0
if TYPE_CHECKING:
    from .Plugin import TouchifyPlugin

class TouchifyWindow(QObject):
    
    class Managers:
        def __init__(self, manager: "TouchifyWindow"):
            self.mgr_tweaker = TweakManager(manager)
            self.mgr_shortcuts = ShortcutsManager(manager)
            self.mgr_canvas = CanvasManager(manager)
            self.mgr_dev = DeveloperManager(manager)
            self.mgr_actions = ActionManager(manager)

        def Load(self, manager: "TouchifyWindow"):
            self.mgr_dockers = DockerManager(manager)
            self.mgr_actions.Window_Load(manager.api_window)
            self.mgr_shortcuts.Window_Load()
            self.mgr_tweaker.Window_Load()
            self.mgr_canvas.Window_Load(manager.api_window)

        def Addons(self, manager: "TouchifyWindow"):
            dockers_menu_action = KritaExtensions.getDockerMenu(manager.api_window)
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

            for docker in manager.api_window.dockers:
                window_title = docker.windowTitle()
                docker_id = docker.objectName()

                if window_title.startswith(addon_title_prefix):
                    docker.setWindowTitle(window_title.removeprefix(addon_title_prefix))

                if window_title.startswith(touchify_title_prefix):
                    docker.setWindowTitle(window_title.removeprefix(touchify_title_prefix))

                if docker_id == TOUCHIFY_DOCKERID_TOOLSHELFDOCKER:
                    toolshelfDocker: ToolshelfDockWidget = docker
                    toolshelfDocker.setup(manager)
                elif docker_id == TOUCHIFY_DOCKERID_DOCKER_TOOLBOX:
                    toolboxDocker: ToolboxDocker = docker
                    toolboxDocker.setup(manager)
                else:
                    if not docker_id.startswith(addon_id_prefix): pass
                    elif not hasattr(docker, addon_setup_method): pass
                    elif not callable(getattr(docker, addon_setup_method, False)): pass
                    else: getattr(docker, addon_setup_method)(manager)

        def Actions(self, window: WindowAPI):
            self.mgr_shortcuts.Actions_Init(window, "tools/touchify", "settings")
            self.mgr_actions.Actions_Init(window, "tools/touchify")  
            self.mgr_dev.Actions_Init(window, "settings")
            self.mgr_tweaker.Actions_Init(window, "settings")
            self.mgr_canvas.Actions_Init(window, "settings")

        def ActionWidgets(self, manager: "TouchifyWindow"):
            self.mgr_shortcuts.Actions_Post()
            self.mgr_tweaker.Actions_Post()
            self.mgr_canvas.Actions_Post()
            self.mgr_actions.Actions_Post(manager.action_plugin_tools_menu)
            self.mgr_dev.Actions_Post(manager.action_plugin_tools_menu)

    def __init__(self, parent: QObject):
        super().__init__(parent)

        global WINDOW_ID; self.INSTANCE_ID = WINDOW_ID; WINDOW_ID += 1
        self.managers = self.Managers(self)
        self.dlg_settings: PluginOptions | None = None

    def Load(self, window: WindowAPI):
        self.api_window = window
        self.setParent(self.api_window.qwindow)
        self.managers.Load(self)

        self.action_plugin_instance = QAction(f"Instance: #{self.INSTANCE_ID}", self.action_plugin_tools_menu)
        self.action_plugin_instance.setEnabled(False)
        self.action_plugin_instance.setSeparator(True)
        self.action_plugin_tools_menu.addAction(self.action_plugin_instance)
        self.managers.ActionWidgets(self)

        self.managers.Addons(self)

    def LoadActions(self, window: WindowAPI):
        self.action_plugin_settings = window.create_action(TOUCHIFY_ACTIONID_CONFIGURE, "Configure Touchify...", "settings")
        self.action_plugin_settings.triggered.connect(self.OpenSettings)

        self.action_plugin_tools_menu = QMenu(None, window.qwindow)
        self.action_plugin_tools = window.create_action("touchify", "Touchify", "tools")
        self.action_plugin_tools.setMenu(self.action_plugin_tools_menu)

        self.managers.Actions(window)
 
    def Unload(self):
        pass

    def OpenSettings(self):
        if self.dlg_settings != None:
            if PyQtExtensions.CommonHelpers.isDeleted(self.dlg_settings) == False:
                return
          
        self.dlg_settings = PluginOptions(self.api_window)
        self.dlg_settings.show()