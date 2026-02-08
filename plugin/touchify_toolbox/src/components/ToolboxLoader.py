from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from jemlib.api_touchify.env import *
from krita import *

from typing import TYPE_CHECKING

from jemlib.api_krita import KritaAPI
from touchify_toolbox.src.components.ToolboxButton import ToolboxButton
from touchify_toolbox.src.components.ToolboxSubtoolMenu import ToolboxSubtoolMenu
from touchify_toolbox.src.components.ToolboxStyles import ToolboxStyles
from touchify_toolbox.src.config.ToolboxData import ToolboxData
from touchify_toolbox.src.config.ToolboxDataItem import ToolboxDataItem
from touchify_toolbox.src.config.ToolboxDataSubitem import ToolboxDataSubitem
from touchify.src.config.triggers.Trigger import Trigger
from jemlib.managers.IconRepository import IconRepository


if TYPE_CHECKING:
    from touchify_toolbox.src.components.ToolboxDocker import ToolboxDocker

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
        btn: ToolboxButton = ac.parent()
        btn.onToolboxButtonSwap(ac)

    def Signal_OnMenu(self):
        subMenu: ToolboxSubtoolMenu = self.sender() # link the toolbutton menu to this function
        if subMenu.isEmpty(): self.Build_Menu(subMenu) # prevents the menu from continuously adding actions every click

    def Signal_OnClickMenu(self, source: ToolboxButton):
        if not source: return
        subMenu: ToolboxSubtoolMenu = source.menu() # link the toolbutton menu to this function
        if subMenu.isEmpty(): self.Build_Menu(subMenu) # prevents the menu from continuously adding actions every click
        source.menu().show()

    def Build_Action(self, tool: ToolboxDataItem):
        trigger = Trigger()
        trigger.variant = Trigger.Variants.Action
        trigger.action_id = tool.name

        is_toolbox_menu = len(tool.items) >= 1

        btn: ToolboxButton = self.rootWidget.managers.mgr_actions.Create_Button(self.rootWidget.toolbox, trigger, classType=ToolboxButton)
        if btn:
            tool_names: list[str] = [item.name for item in tool.items]
            tool_names.append(tool.name)
            btn.setupBlenderButton(is_toolbox_menu, tool.open_on_click, tool_names)
            btn.setWindowOpacity(self._opacityLevel)

            if tool.icon != "": 
                btn.setIcon(IconRepository.iconLoader(tool.icon))
                btn.action_use_icon = False


            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            btn.setIconSize(QSize(self._iconSize, self._iconSize))
            ToolboxStyles.setButtonStyleSheet(btn, self.rootWidget.style_data)

            if is_toolbox_menu:
                subMenu = ToolboxSubtoolMenu(btn, tool)
                btn.setMenu(subMenu) # this will be the submenu for each main tool

                
                if tool.open_on_click:
                    btn.menuRequested.connect(lambda: self.Signal_OnClickMenu(btn))
                else:
                    btn.menu().aboutToShow.connect(self.Signal_OnMenu)
            return btn
        return None

    def Build_Menu(self, subMenu: ToolboxSubtoolMenu):
        self.Build_MenuAction(subMenu, subMenu.tool.name, subMenu.tool.icon)
        for toolItem in subMenu.items: # iterate through all the tools in the category
            toolItem: ToolboxDataSubitem
            self.Build_MenuAction(subMenu, toolItem.name, toolItem.icon)

        for action in subMenu.actions(): # show tool icons in submenu
            action.setIconVisibleInMenu(True)

    def Build_MenuAction(self, subMenu: ToolboxSubtoolMenu, actionName: str, iconName: str):
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
            customIcon = IconRepository.iconLoader(iconName)
            if customIcon: return QIcon(customIcon)
        elif act: return QIcon(act.icon())
        else: return QIcon()

