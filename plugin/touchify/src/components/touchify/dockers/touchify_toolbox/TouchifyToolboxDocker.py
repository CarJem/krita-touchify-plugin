# This Python file uses the following encoding: utf-8
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from krita import *

import json
from os import path


from .ToolboxCategory import ToolboxCategory
from .ToolboxStyle import ToolboxStyle
from .ToolboxMenu import ToolboxMenu
from .ToolboxButton import ToolboxButton
from .....settings.TouchifyConfig import TouchifyConfig
from .....cfg.CfgToolbox import CfgToolbox
from .....cfg.CfgToolboxItem import CfgToolboxItem
from .....cfg.CfgToolboxSubItem import CfgToolboxSubItem
from .....cfg.CfgToolboxCategory import CfgToolboxCategory


TOOLBOX_ITEMS = [
    "KisToolTransform",
    "KritaTransform/KisToolMove",
    "KisToolCrop",
    "InteractionTool",
    "SvgTextTool",
    "PathTool",
    "KarbonCalligraphyTool",
    "KritaShape/KisToolBrush",
    "KritaShape/KisToolDyna",
    "KritaShape/KisToolMultiBrush",
    "KritaShape/KisToolSmartPatch",
    "KisToolPencil",
    "KritaFill/KisToolFill",
    "KritaSelected/KisToolColorPicker",
    "KritaShape/KisToolLazyBrush",
    "KritaFill/KisToolGradient",
    "KritaShape/KisToolRectangle",
    "KritaShape/KisToolLine",
    "KritaShape/KisToolEllipse",
    "KisToolPolygon",
    "KisToolPolyline",
    "KisToolPath",
    "KisToolEncloseAndFill",
    "KisToolSelectRectangular",
    "KisToolSelectElliptical",
    "KisToolSelectPolygonal",
    "KisToolSelectPath",
    "KisToolSelectOutline",
    "KisToolSelectContiguous",
    "KisToolSelectSimilar",
    "KisToolSelectMagnetic",
    "ToolReferenceImages",
    "KisAssistantTool",
    "KritaShape/KisToolMeasure",
    "PanTool",
    "ZoomTool"
]

class TouchifyToolboxDocker(QDockWidget):
    def __init__(self):
        super().__init__()

        self.floating = False
        self.setWindowTitle('Touchify Toolbox') # window title also acts as the Docker title in Settings > Dockers

        self.krita = Krita.instance()
        self.sourceWindow: QWindow | None = None

        self.config: CfgToolbox = TouchifyConfig.instance().getConfig().toolbox
        TouchifyConfig.instance().notifyConnect(self.buildActions)
        
        self.categories: dict[str, list[ToolboxButton]] = {}

        self.lastActiveTool = ""
        self.registeredToolBtns: list[ToolboxButton] = []

        self.sourceWidget = QWidget()
        label = QLabel(" ") # label conceals the 'exit' buttons and Docker title

        label.setFrameShape(QFrame.StyledPanel)
        label.setFrameShadow(QFrame.Raised)
        label.setFrameStyle(QFrame.Panel | QFrame.Raised)
        label.setMinimumWidth(16)

        self.tickTimer = QTimer(self)
        self.tickTimer.setInterval(250)
        self.tickTimer.timeout.connect(self.updateState)
        self.tickTimer.start()

        self.setWidget(self.sourceWidget)
        self.setTitleBarWidget(label)

        self.gridLayout = QGridLayout()

        self.sourceWidget.setLayout(self.gridLayout)
        self.krita.notifier().windowCreated.connect(self.buildActions)

    def getActiveToolButton(self):
        try:
            active_window = self.krita.activeWindow()           
            if active_window != None:   
                mobj = next((w for w in active_window.qwindow().findChildren(QWidget) if w.metaObject().className() == 'KoToolBox'), None)
                for q_obj in mobj.findChildren(QToolButton):
                    if q_obj.metaObject().className() == "KoToolBoxButton":
                        if q_obj.isChecked():
                            return q_obj.objectName()
        except:
            pass
        return ""



    def updateState(self):
        activeTool = self.getActiveToolButton()

        if activeTool != "":
            for btn in self.registeredToolBtns:
                if btn.actionName == activeTool:
                    btn.setChecked(True)
                else:
                    btn.setChecked(False)
            self.lastActiveTool = activeTool

    #region Layouts

    def buildActions(self):
        self.config: CfgToolbox = TouchifyConfig.instance().getConfig().toolbox

        for cat in self.categories:
            btnList: list[ToolboxButton] = self.categories[cat]
            for btn in btnList:
                act: QAction = self.krita.action(btn.actionName)
                self.gridLayout.removeWidget(btn)
                btn.hide()
                btn.close()

        self.registeredToolBtns = []

        x = 0
        y = 0

        col_max = self.config.column_count
        icon_size = self.config.icon_size
        horizontal_mode = self.config.horizontal_mode

        for category in self.config.categories: # Set up button logic
            category: CfgToolboxCategory
            self.categories[category.id] = []

            for tool in category.items:
                tool: CfgToolboxItem
                ac = self.krita.action(tool.name)
                if ac:
                    btn: ToolboxButton = ToolboxButton(tool.name)
                    btn.setObjectName(tool.name)
                    btn.setText(ac.text())
                    btn.setIcon(ac.icon())
                    btn.setIconSize(QSize(icon_size, icon_size))
                    btn.setToolTip(ac.text())
                    btn.setStyle(ToolboxStyle("fusion", self.config.menuDelay))
                    btn.pressed.connect(self.activateTool) # Activate when clicked

                    if tool.name in TOOLBOX_ITEMS:
                        btn.setCheckable(True)
                        btn.setAutoRaise(True)
                        self.registeredToolBtns.append(btn)


                    self.categories[category.id].append(btn)
                    if horizontal_mode:
                        self.gridLayout.addWidget(btn, x, y)
                    else:
                        self.gridLayout.addWidget(btn, y, x)

                    if len(tool.items) >= 1:
                        subMenu = ToolboxMenu(btn, tool)
                        btn.setMenu(subMenu) # this will be the submenu for each main tool

                        btn.menu().aboutToShow.connect(self.activateMenu) # Show submenu when clicked
                        if self.config.submenuButton == True:
                            btn.menu().aboutToShow.connect(self.activateMenu)

                    x = x + 1
                    if x >= col_max: 
                        x = 0
                        y = y + 1
            x = 0
            y = y + 1

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
            toolText = act.text()
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
    #endregion

    def canvasChanged(self, canvas):
        pass