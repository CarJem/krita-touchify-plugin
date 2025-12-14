from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from touchify.__env__ import *
from krita import *

from typing import TYPE_CHECKING

from touchify.src.api_krita import KritaAPI
from touchify.src.components.toolbox.ToolboxMenu import ToolboxMenu
from touchify.src.components.toolbox.ToolboxStyles import ToolboxStyles
from touchify.src.components.widgets.triggers.TriggerButton import TriggerButton
from touchify.src.config.toolbox.ToolboxData import ToolboxData
from touchify.src.config.toolbox.ToolboxDataItem import ToolboxDataItem
from touchify.src.config.toolbox.ToolboxDataSubitem import ToolboxDataSubitem
from touchify.src.config.triggers.Trigger import Trigger
from touchify.src.managers.ResourceManager import ResourceManager
from touchify.src.settings.TouchifySettings import TouchifySettings


if TYPE_CHECKING:
    from touchify.src.components.toolbox.ToolboxDocker import ToolboxDocker

class ToolboxLoader(QObject):
    def __init__(self, parent: "ToolboxDocker"):
        super().__init__(parent)
        self.rootWidget = parent

        self._iconSize = 16
        self._submenu_delay = 200
        self._opacityLevel = 0.65
        self._cfg = ToolboxData()

    def Sync(self, cfg: ToolboxData):
        self._iconSize = cfg.icon_size
        self._submenu_delay = cfg.submenu_delay
        self._cfg = cfg
        #self._opacityLevel = cfg.opacity_level

    def Signal_OnSwap(self):
        ac: QAction = self.sender()
        btn: TriggerButton = ac.parent()
        btn.onToolboxButtonSwap(ac)

    def Signal_OnMenu(self):
        subMenu: ToolboxMenu = self.sender() # link the toolbutton menu to this function
        if subMenu.isEmpty(): self.Build_Menu(subMenu) # prevents the menu from continuously adding actions every click

    def Signal_OnPreset(self):
        ac: QAction = self.sender()
        if isinstance(ac, QAction):
            id: str = ac.data()
            if isinstance(id, str):
                self.rootWidget.settingsManager.setCurrentToolbox(id)
                self.rootWidget.sync()

    def Signal_OnSettings(self):
        self.rootWidget.onSettings()
        

    def Build_Context(self):

        menu = QMenu(self.rootWidget)

        presetsMenu = menu.addMenu("Presets")
        presetMenuList: dict[str, QMenu] = {}
        selected_preset_id = self.rootWidget.settingsManager.getCurrentToolboxId()
        registry = TouchifySettings.registry(ToolboxData)
        if registry != None:
            for key, preset in registry.items():
                if not key.id in presetMenuList:
                    presetMenuList[key.id] = presetsMenu.addMenu(key.name)
                preset: ToolboxData
                action = QAction(preset.preset_name, presetsMenu)
                action.setCheckable(True)
                if selected_preset_id == key.actual_key:
                    action.setChecked(True)
                action.setData(key.actual_key)
                action.triggered.connect(self.Signal_OnPreset)
                presetMenuList[key.id].addAction(action)
            
            presetsMenu.addSeparator()
        

        menu.addSeparator()
        
        settingsButton = menu.addAction("Toolbox Settings...")
        settingsButton.triggered.connect(self.Signal_OnSettings)
        return menu

    def Build_Action(self, tool: ToolboxDataItem):
        trigger = Trigger()
        trigger.variant = Trigger.Variants.Action
        trigger.action_id = tool.name

        is_toolbox_menu = len(tool.items) >= 1

        btn: TriggerButton = self.rootWidget.managers.mgr_actions.Create_Button(self.rootWidget._toolbox, trigger)
        if btn:
            tool_names: list[str] = [item.name for item in tool.items]
            tool_names.append(tool.name)
            btn.setupBlenderButton(is_toolbox_menu, tool_names)
            btn.setWindowOpacity(self._opacityLevel)

            if tool.icon != "": 
                btn.setIcon(ResourceManager.iconLoader(tool.icon))
                btn.action_use_icon = False


            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            btn.setIconSize(QSize(self._iconSize, self._iconSize))
            ToolboxStyles.setButtonStyleSheet(btn, self.rootWidget.style_data)

            if is_toolbox_menu:
                subMenu = ToolboxMenu(btn, tool)
                btn.setMenu(subMenu) # this will be the submenu for each main tool

                btn.menu().aboutToShow.connect(self.Signal_OnMenu) # Show submenu when clicked
                if tool.open_on_click == True:
                    btn.menu().aboutToShow.connect(self.Signal_OnMenu)
            return btn
        return None

    def Build_Menu(self, subMenu: ToolboxMenu):
        self.Build_MenuAction(subMenu, subMenu.tool.name, subMenu.tool.icon)
        for toolItem in subMenu.items: # iterate through all the tools in the category
            toolItem: ToolboxDataSubitem
            self.Build_MenuAction(subMenu, toolItem.name, toolItem.icon)

        for action in subMenu.actions(): # show tool icons in submenu
            action.setIconVisibleInMenu(True)

    def Build_MenuAction(self, subMenu: ToolboxMenu, actionName: str, iconName: str):
        act = KritaAPI.get_action(actionName)
        if act:
            toolIcon = self.Build_ActionIcon(actionName, iconName)
            toolText = act.toolTip()
            toolName = actionName
            toolAction = QAction(toolIcon, toolText, subMenu) # set up initial toolAction

            # we need to call Krita's shortcut for the toolAction:
            try:
                KritaAPI.get_action(toolName).shortcut()

                toolShortcut = KritaAPI.get_action(toolName).shortcut().toString() # find the global shortcut

                toolAction.setShortcut(toolShortcut)

            except:
                pass

            toolAction.setObjectName(toolName)
            toolAction.setParent(subMenu.parentBtn) # set toolbutton as parent
            toolAction.triggered.connect(self.Signal_OnSwap) # activate menu tool on click
            toolAction.triggered.connect(act.trigger) # activate menu tool on click
            subMenu.addAction(toolAction) # add the button for this tool in the menu

    def Build_ActionIcon(self, actionName: str, iconName: str):
        act = KritaAPI.get_action(actionName)

        if iconName and iconName != "":
            customIcon = ResourceManager.iconLoader(iconName)
            if customIcon: return QIcon(customIcon)
        elif act: return QIcon(act.icon())
        else: return QIcon()

