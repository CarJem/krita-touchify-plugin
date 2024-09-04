# This Python file uses the following encoding: utf-8
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from krita import *

import json
from os import path

from .....variables import *

from .....ext.extensions_krita import KritaExtensions
from .....ext.KritaSettings import KritaSettings

from .....stylesheet import Stylesheet

from .ToolboxCategory import ToolboxCategory
from .ToolboxScrollArea import ToolboxScrollArea
from .ToolboxStyle import ToolboxStyle
from .ToolboxMenu import ToolboxMenu
from .ToolboxButton import ToolboxButton
from .....settings.TouchifyConfig import TouchifyConfig
from .....cfg.CfgToolboxSettings import CfgToolboxSettings
from .....cfg.toolbox.CfgToolbox import CfgToolbox
from .....cfg.toolbox.CfgToolboxItem import CfgToolboxItem
from .....cfg.toolbox.CfgToolboxSubItem import CfgToolboxSubItem
from .....cfg.toolbox.CfgToolboxCategory import CfgToolboxCategory


TOOLBOX_ITEMS: dict[str, str] = {
        "KisToolTransform": "KisToolTransform",
        "KritaTransform/KisToolMove": "KritaTransform/KisToolMove",
        "KisToolCrop": "KisToolCrop",
        "InteractionTool": "InteractionTool",
        "SvgTextTool": "SvgTextTool",
        "PathTool": "PathTool",
        "KarbonCalligraphyTool": "KarbonCalligraphyTool",
        "KritaShape/KisToolBrush": "KritaShape/KisToolBrush",
        "KritaShape/KisToolDyna": "KritaShape/KisToolDyna",
        "KritaShape/KisToolMultiBrush": "KritaShape/KisToolMultiBrush",
        "KritaShape/KisToolSmartPatch": "KritaShape/KisToolSmartPatch",
        "KisToolPencil": "KisToolPencil",
        "KritaFill/KisToolFill": "KritaFill/KisToolFill",
        "KritaSelected/KisToolColorSampler": "KritaSelected/KisToolColorPicker",
        "KritaShape/KisToolLazyBrush": "KritaShape/KisToolLazyBrush",
        "KritaFill/KisToolGradient": "KritaFill/KisToolGradient",
        "KritaShape/KisToolRectangle": "KritaShape/KisToolRectangle",
        "KritaShape/KisToolLine": "KritaShape/KisToolLine",
        "KritaShape/KisToolEllipse": "KritaShape/KisToolEllipse",
        "KisToolPolygon": "KisToolPolygon",
        "KisToolPolyline": "KisToolPolyline",
        "KisToolPath": "KisToolPath",
        "KisToolEncloseAndFill": "KisToolEncloseAndFill",
        "KisToolSelectRectangular": "KisToolSelectRectangular",
        "KisToolSelectElliptical": "KisToolSelectElliptical",
        "KisToolSelectPolygonal": "KisToolSelectPolygonal",
        "KisToolSelectPath": "KisToolSelectPath",
        "KisToolSelectOutline": "KisToolSelectOutline",
        "KisToolSelectContiguous": "KisToolSelectContiguous",
        "KisToolSelectSimilar": "KisToolSelectSimilar",
        "KisToolSelectMagnetic": "KisToolSelectMagnetic",
        "ToolReferenceImages": "ToolReferenceImages",
        "KisAssistantTool": "KisAssistantTool",
        "KritaShape/KisToolMeasure": "KritaShape/KisToolMeasure",
        "PanTool": "PanTool",
        "ZoomTool": "ZoomTool"
}

class TouchifyToolboxDocker(QDockWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.floating = False
        self.setWindowTitle('Touchify Toolbox') # window title also acts as the Docker title in Settings > Dockers

        label = QLabel(" ") # label conceals the 'exit' buttons and Docker title
        label.setFrameShape(QFrame.StyledPanel)
        label.setFrameShadow(QFrame.Raised)
        label.setFrameStyle(QFrame.Panel | QFrame.Raised)
        label.setMinimumWidth(16)

        self.toolboxWidget = ToolboxWidget()
        self.toolboxScroll = ToolboxScrollArea(self.toolboxWidget, self)
        self.toolboxWidget.setScrollArea(self.toolboxScroll)
        self.toolboxScroll.setViewportMargins(0,0,0,0)

        self.setWidget(self.toolboxScroll)


class ToolboxWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.krita = Krita.instance()
        self.sourceWindow: QWindow | None = None
        self.preLoaded = False


        self.scrollArea: ToolboxScrollArea | None = None


        self.setContentsMargins(0,0,0,0)
        self.loadConfig()
        TouchifyConfig.instance().notifyConnect(self.reload)
        
        self.categories: list[ToolboxCategory] = []

        self.lastActiveTool = ""
        self.registeredToolBtns: list[ToolboxButton] = []

        self.buttonGroup = QButtonGroup(self)
        self.buttonGroup.setExclusive(True)

        self.gridLayout = QBoxLayout(QBoxLayout.Direction.Down, self)
        self.setLayout(self.gridLayout)
        

        self.settingsBtn = QToolButton(self)
        self.settingsBtn.setIcon(self.krita.icon("configure"))
        self.settingsBtn.setIconSize(QSize(16,16))
        self.settingsBtn.setContentsMargins(0,0,0,0)
        self.settingsBtn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.settingsMenu = QMenu(self)
        self.settingsBtn.setMenu(self.settingsMenu)
        self.gridLayout.addWidget(self.settingsBtn)

        self.krita.notifier().windowCreated.connect(self.reload)

    def sizeHint(self):
        actualSizeMod = super().sizeHint()

        opt = QStyleOption()
        opt.initFrom(self)
        padding = self.style().pixelMetric(QStyle.PM_TabBarScrollButtonWidth, opt, self)

        actualSizeMod.setWidth(actualSizeMod.width() + padding)
        actualSizeMod.setHeight(actualSizeMod.height() + padding)
        return actualSizeMod
            
    def registerToolButtonChanged(self):
        try:
            active_window = self.krita.activeWindow()           
            if active_window != None:   
                mobj = next((w for w in active_window.qwindow().findChildren(QWidget) if w.metaObject().className() == 'KoToolBox'), None)
                wobj = mobj.findChild(QButtonGroup)
                wobj.idToggled.connect(self.updateState)
                return True
        except:
            return False
        return False

    def getActiveToolButton(self):
        try:
            active_window = self.krita.activeWindow()           
            if active_window != None:   
                mobj = next((w for w in active_window.qwindow().findChildren(QWidget) if w.metaObject().className() == 'KoToolBox'), None)
                for q_obj in mobj.findChildren(QToolButton):
                    if q_obj.metaObject().className() == "KoToolBoxButton":
                        if q_obj.isChecked():
                            name = q_obj.objectName()
                            name = name.replace("\n", "")
                            return name
        except:
            pass
        return ""

    def updateState(self):
        activeTool = self.getActiveToolButton()

        if activeTool != "":
            for btn in self.registeredToolBtns:
                actualName = btn.actionName
                if btn.actionName in TOOLBOX_ITEMS:
                    actualName = TOOLBOX_ITEMS[actualName]
  
                if btn.actionName == activeTool:
                    btn.setChecked(True)
                else:
                    btn.setChecked(False)
            self.lastActiveTool = activeTool

    #region Setters

    def setScrollArea(self, scrollArea: ToolboxScrollArea):
        self.scrollArea = scrollArea

    def setOrientation(self, orientation: Qt.Orientation):
        if self.scrollArea and isinstance(self.scrollArea, ToolboxScrollArea):
            scrollArea: ToolboxScrollArea = self.scrollArea
            scrollArea.setOrientation(orientation)

    #endregion


    #region Layouts


    def reload(self):
        self.unload()
        self.load()

    def unload(self):
        for cat in self.categories:
            btnList: list[ToolboxButton] = cat.buttons
            for btn in btnList:
                cat.removeTool(btn)
                if btn.actionName in TOOLBOX_ITEMS:
                    self.buttonGroup.removeButton(btn)
                btn.hide()
                btn.close()
            self.gridLayout.removeWidget(cat)

        self.registeredToolBtns = []
        self.categories = []
    
    def load(self):
        if self.preLoaded == False:
            if self.registerToolButtonChanged():
                self.preLoaded = True

        self.loadConfig()
        self.buildSettingsMenu()
        self.buildCategories()   

    def loadConfig(self):
        self.settings: CfgToolboxSettings = TouchifyConfig.instance().getConfig().toolbox_settings

        self.config: CfgToolbox = CfgToolbox().loadDefaults()
        self.selectedPresetIndex = KritaSettings.readSettingInt(TOUCHIFY_ID_DOCKER_TOOLBOX, "SelectedPreset", 0)

        if 0 <= self.selectedPresetIndex < len(self.settings.presets):
            self.config: CfgToolbox = self.settings.presets[self.selectedPresetIndex]
        elif len(self.settings.presets) >= 1:
            self.selectedPresetIndex = 0
            self.config: CfgToolbox = self.settings.presets[self.selectedPresetIndex]
        else:
            self.selectedPresetIndex = 0
            newItem = CfgToolbox()
            newItem.loadDefaults()
            self.config = newItem
        
        KritaSettings.writeSettingInt(TOUCHIFY_ID_DOCKER_TOOLBOX, "SelectedPreset", self.selectedPresetIndex)

    def buildSettingsMenu(self):
        self.settingsMenu.clear()

        index = 0
        for preset in self.settings.presets:
            preset: CfgToolbox
            action = QAction(preset.presetName, self.settingsMenu)
            action.setCheckable(True)
            if self.selectedPresetIndex == index:
                action.setChecked(True)
            action.setData(index)
            action.triggered.connect(self.changePreset)
            index += 1
            self.settingsMenu.addAction(action)

    def buildCategories(self):
        x = 0
        y = 0

        col_max = self.config.column_count
        icon_size = self.config.icon_size
        horizontal_mode = self.config.horizontal_mode

        toolbox_item_alignment = Qt.AlignmentFlag.AlignTop if horizontal_mode else Qt.AlignmentFlag.AlignLeft

        if horizontal_mode:
            self.gridLayout.setDirection(QBoxLayout.Direction.LeftToRight)
            self.settingsBtn.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
            self.setOrientation(Qt.Orientation.Horizontal)
        else:
            self.gridLayout.setDirection(QBoxLayout.Direction.Down)
            self.settingsBtn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
            self.setOrientation(Qt.Orientation.Vertical)

        for categoryData in self.config.categories: # Set up button logic
            categoryData: CfgToolboxCategory
            specific_col_max = col_max
            if categoryData.column_count >= 1:
                specific_col_max = categoryData.column_count
            category = ToolboxCategory(self, categoryData.id)
            for tool in categoryData.items:
                btn = self.buildCategoryAction(tool, icon_size)
                if btn:
                    if horizontal_mode: category.addTool(btn, x, y, toolbox_item_alignment)
                    else: category.addTool(btn, y, x, toolbox_item_alignment)

                    x = x + 1
                    if x >= specific_col_max: 
                        x = 0
                        y = y + 1
                        
            self.categories.append(category)
            self.gridLayout.addWidget(category, 0, toolbox_item_alignment)
            x = 0
            y = y + 1
        self.updateState()

    def buildCategoryAction(self, tool: CfgToolboxItem, icon_size: int):
        ac = self.krita.action(tool.name)
        if ac:
            actionText = KritaExtensions.formatActionText(ac.text())
            btn: ToolboxButton = ToolboxButton(tool.name)
            btn.setObjectName(tool.name)
            btn.setText(actionText)
            btn.setIcon(ac.icon())
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            btn.setIconSize(QSize(icon_size, icon_size))
            btn.setToolTip(actionText)
            btn.setStyle(ToolboxStyle("fusion", self.config.menuDelay))
            btn.pressed.connect(self.activateTool) # Activate when clicked

            if tool.name in TOOLBOX_ITEMS:
                self.buttonGroup.addButton(btn)
                btn.setCheckable(True)
                btn.setAutoRaise(True)
                self.registeredToolBtns.append(btn)

            if len(tool.items) >= 1:
                subMenu = ToolboxMenu(btn, tool)
                btn.setMenu(subMenu) # this will be the submenu for each main tool

                btn.menu().aboutToShow.connect(self.activateMenu) # Show submenu when clicked
                if self.config.submenuButton == True:
                    btn.menu().aboutToShow.connect(self.activateMenu)
            return btn
        return None

    def buildMenu(self, subMenu: ToolboxMenu):
        self.buildMenuAction(subMenu, subMenu.tool.name)
        for toolItem in subMenu.items: # iterate through all the tools in the category
            toolItem: CfgToolboxSubItem
            self.buildMenuAction(subMenu, toolItem.name)

        for action in subMenu.actions(): # show tool icons in submenu
            action.setIconVisibleInMenu(True)

    def buildMenuAction(self, subMenu: ToolboxMenu, actionName: str):
        act = self.krita.action(actionName)
        if act:
            toolIcon = QIcon(act.icon())
            toolText = KritaExtensions.formatActionText(act.text())
            toolName = actionName
            toolAction = QAction(toolIcon, toolText, subMenu) # set up initial toolAction

            # we need to call Krita's shortcut for the toolAction:
            try:
                self.krita.action(toolName).shortcut()

                toolShortcut = self.krita.action(toolName).shortcut().toString() # find the global shortcut

                toolAction.setShortcut(toolShortcut)

            except:
                pass

            toolAction.setObjectName(toolName)
            toolAction.setParent(subMenu.parentBtn) # set toolbutton as parent
            toolAction.triggered.connect(self.swapToolButton) # activate menu tool on click
            toolAction.triggered.connect(self.activateTool) # activate menu tool on click
            subMenu.addAction(toolAction) # add the button for this tool in the menu

    #endregion

    #region Triggers
    def activateMenu(self):
        subMenu: ToolboxMenu = self.sender() # link the toolbutton menu to this function
        if subMenu.isEmpty(): # prevents the menu from continuously adding actions every click
            self.buildMenu(subMenu)

    def swapToolButton(self):
        ac: QAction = self.sender()
        btn: ToolboxButton = ac.parent()

        btn.actionName = ac.objectName()
        btn.setObjectName(ac.objectName())
        btn.setText(ac.text())
        btn.setIcon(ac.icon())

    def activateTool(self):
        actionName = self.sender().objectName() # get ToolButton name
        ac = self.krita.action(actionName) # Search this name in Krita's action list

        print(actionName, ac)
        if ac:
            ac.trigger() # trigger the action in Krita

        else:
            pass
    
    def changePreset(self):
        ac: QAction = self.sender()
        if isinstance(ac, QAction):
            index: int = ac.data()
            if isinstance(index, int):
                KritaSettings.writeSettingInt(TOUCHIFY_ID_DOCKER_TOOLBOX, "SelectedPreset", index)
                self.reload()
    #endregion

    def canvasChanged(self, canvas):
        pass