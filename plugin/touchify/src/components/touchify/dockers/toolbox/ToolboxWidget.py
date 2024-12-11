# This Python file uses the following encoding: utf-8
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from krita import *


from touchify.src.variables import *

from touchify.src.ext.KritaSettings import KritaSettings


from touchify.src.components.touchify.dockers.toolbox.ToolboxCategory import ToolboxCategory
from touchify.src.components.touchify.dockers.toolbox.ToolboxScrollArea import ToolboxScrollArea
from touchify.src.components.touchify.dockers.toolbox.ToolboxStyle import ToolboxStyle
from touchify.src.components.touchify.dockers.toolbox.ToolboxMenu import ToolboxMenu
from touchify.src.components.touchify.dockers.toolbox.ToolboxButton import ToolboxButton
from touchify.src.settings import TouchifySettings
from touchify.src.cfg.toolbox.ToolboxData import ToolboxData
from touchify.src.cfg.toolbox.ToolboxDataItem import ToolboxDataItem
from touchify.src.cfg.toolbox.ToolboxDataSubitem import ToolboxDataSubitem
from touchify.src.cfg.toolbox.ToolboxDataCategory import ToolboxDataCategory
from touchify.src.components.pyqt.widgets.QResizableWidget import QResizableWidget
from touchify.src.resources import ResourceManager

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .....window import TouchifyWindow


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

class ToolboxWidget(QResizableWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.sourceWindow: Window = None

        self.OPACITY_LEVEL = 0.65

        self.__preload__themeChanged = False
        self.__preload__checkChanged = False

        self.loadConfig()
        
        self.horizontalMode: bool = KritaSettings.readSettingBool(TOUCHIFY_ID_DOCKER_TOOLBOX, "IsHorizontal", False)
        self.categories: list[ToolboxCategory] = []
        self.lastActiveTool = ""
        self.registeredToolBtns: list[ToolboxButton] = []
        self.horizontalModeAction: QAction = None


        self.setLayout(QVBoxLayout(self))
        self.setContentsMargins(0,0,0,0)
        self.updateStyleSheet()

        self.buttonGroup = QButtonGroup(self)
        self.buttonGroup.setExclusive(True)

        self.scrollArea = ToolboxScrollArea(self)
        self.scrollArea.setContentsMargins(0,0,0,0)
        self.scrollArea.setViewportMargins(0,0,0,0)
        self.scrollArea.setWidgetResizable(True)
        self.layout().addWidget(self.scrollArea)

        self.settingsBtn = QToolButton(self)
        self.settingsBtn.setIcon(Krita.instance().icon("configure"))
        self.settingsBtn.setIconSize(QSize(16,16))
        self.settingsBtn.setContentsMargins(0,0,0,0)
        self.settingsBtn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.settingsBtn.clicked.connect(self.settingsBtn.showMenu)

        self.settingsMenu = QMenu(self)
        self.settingsBtn.setMenu(self.settingsMenu)
        
        self.viewportLayout = QBoxLayout(QBoxLayout.Direction.Down, self)
        self.viewportLayout.setContentsMargins(0,0,0,0)
        self.viewportLayout.addWidget(self.settingsBtn)

        self.viewportWidget = QWidget(self)
        self.viewportWidget.setContentsMargins(0,0,0,0)
        self.viewportWidget.setLayout(self.viewportLayout)
        self.scrollArea.setWidget(self.viewportWidget)


    def setup(self, instance: "TouchifyWindow"):
        self.sourceWindow = instance.windowSource
        self.reload()
    

    def updatePalette(self):
        self.settingsBtn.setIcon(Krita.instance().icon("configure"))
        self.reload()


    def updateStyleSheet(self):
        highlight_hex = qApp.palette().color(QPalette.ColorRole.Highlight).name().split("#")[1]
        background_hex = qApp.palette().color(QPalette.ColorRole.Window).name().split("#")[1]
        alternate_hex = qApp.palette().color(QPalette.ColorRole.AlternateBase).name().split("#")[1]
        inactive_text_color_hex = qApp.palette().color(QPalette.ColorRole.ToolTipText).name().split("#")[1]
        active_text_color_hex = qApp.palette().color(QPalette.ColorRole.WindowText).name().split("#")[1]


        

        background_opacity = self.layout_config.background_opacity
        alternative_opacity = self.layout_config.button_opacity

        if background_opacity > 255: background_opacity = 255
        if background_opacity < 0: background_opacity = 0

        if alternative_opacity > 255: alternative_opacity = 255
        if alternative_opacity < 0: alternative_opacity = 0


        bg_opacity_hex = hex(background_opacity)[2:]
        alt_opacity_hex = hex(alternative_opacity)[2:]
    
        self.setStyleSheet(f"""
            QFrame#toolbox_frame {{ 
                background-color: #{bg_opacity_hex}{background_hex};
                border: none;
                border-radius: 4px;
                padding: 4px;
            }}
            
            QScrollArea {{ background: transparent; }}
            QScrollArea > QWidget > QWidget {{ background: transparent; }}
            QScrollArea > QWidget > QScrollBar {{ background: palette(base); }}
            
            QAbstractButton {{
                background-color: #{alt_opacity_hex}{background_hex};
                border: none;
                border-radius: 4px;
            }}
            
            QAbstractButton:checked {{
                background-color: #{alt_opacity_hex}{highlight_hex};
            }}
            
            QAbstractButton:hover {{
                background-color: #{alt_opacity_hex}{highlight_hex};
            }}
            
            QAbstractButton:pressed {{
                background-color: #{alt_opacity_hex}{alternate_hex};
            }}
        """)


    def sizeHint(self):
        actualSizeMod = super().sizeHint()

        opt = QStyleOption()
        opt.initFrom(self)
        padding = self.style().pixelMetric(QStyle.PM_TabBarScrollButtonWidth, opt, self)

        if self.horizontalMode:
            actualSizeMod.setWidth(actualSizeMod.width() + padding)
        else:
            actualSizeMod.setHeight(actualSizeMod.height() + padding)
        return actualSizeMod

    def getActiveToolButton(self):
        try:
            active_window = self.sourceWindow         
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

    def updateCheckedStates(self):
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

    def setOrientation(self, orientation: Qt.Orientation):
        if self.scrollArea and isinstance(self.scrollArea, ToolboxScrollArea):
            scrollArea: ToolboxScrollArea = self.scrollArea
            scrollArea.setOrientation(orientation)

    #endregion


    #region Layouts

    def preload(self):
        isPreloaded = self.__preload__themeChanged and self.__preload__checkChanged
        if isPreloaded:
            return

        try:
            active_window = self.sourceWindow
            if active_window != None:   
                if self.__preload__themeChanged == False:
                    active_window.qwindow().themeChanged.connect(self.updatePalette)
                    self.__preload__themeChanged = True

                if self.__preload__checkChanged == False:
                    mobj = next((w for w in active_window.qwindow().findChildren(QWidget) if w.metaObject().className() == 'KoToolBox'), None)
                    wobj = mobj.findChild(QButtonGroup)
                    wobj.idToggled.connect(self.updateCheckedStates)
                    self.__preload__checkChanged = True  
        except:
            pass
        


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
            self.viewportLayout.removeWidget(cat)

        self.registeredToolBtns = []
        self.categories = []
    
    def load(self):
        self.preload()
        self.loadConfig()
        self.buildSettingsMenu()
        self.buildCategories()   
        self.updateStyleSheet()

    def loadConfig(self):
        self.selected_preset_id = TouchifySettings.instance().getActiveToolboxId()
        self.layout_config = TouchifySettings.instance().getActiveToolbox()

    def buildSettingsMenu(self):
        if self.horizontalModeAction != None:
            self.settingsMenu.removeAction(self.horizontalModeAction)


        self.settingsMenu.clear()
        menus: dict[str, QMenu] = {}
        registry = TouchifySettings.instance().getRegistry(ToolboxData)
        if registry != None:
            for key, preset in registry.items():
                if not key.id in menus:
                    menus[key.id] = self.settingsMenu.addMenu(key.name)
                preset: ToolboxData
                action = QAction(preset.preset_name, self.settingsMenu)
                action.setCheckable(True)
                if self.selected_preset_id == key.actual_key:
                    action.setChecked(True)
                action.setData(key.actual_key)
                action.triggered.connect(self.changePreset)
                menus[key.id].addAction(action)
            
            self.settingsMenu.addSeparator()



        if self.horizontalModeAction == None:
            self.horizontalModeAction = QAction("Horizontal Mode", self.settingsMenu)
            self.horizontalModeAction.triggered.connect(self.toggleHorizontalMode)
            self.horizontalModeAction.setCheckable(True)

        self.horizontalModeAction.setChecked(self.horizontalMode)

        self.settingsMenu.addAction(self.horizontalModeAction)

    def buildCategories(self):
        x = 0
        y = 0

        col_max = self.layout_config.column_count
        icon_size = int(self.layout_config.icon_size * TouchifySettings.instance().preferences().Interface_ToolboxIconScale)

        toolbox_item_alignment = Qt.AlignmentFlag.AlignTop if self.horizontalMode else Qt.AlignmentFlag.AlignLeft

        if self.horizontalMode:
            self.viewportLayout.setDirection(QBoxLayout.Direction.LeftToRight)
            self.viewportLayout.setAlignment(self.settingsBtn, Qt.AlignmentFlag.AlignLeft)
            self.settingsBtn.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
            self.setOrientation(Qt.Orientation.Horizontal)
        else:
            self.viewportLayout.setDirection(QBoxLayout.Direction.Down)
            self.viewportLayout.setAlignment(self.settingsBtn, Qt.AlignmentFlag.AlignTop)
            self.settingsBtn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            self.setOrientation(Qt.Orientation.Vertical)


        for categoryData in self.layout_config.categories: # Set up button logic
            categoryData: ToolboxDataCategory
            specific_col_max = col_max
            if categoryData.column_count >= 1:
                specific_col_max = categoryData.column_count
            category = ToolboxCategory(self, categoryData.id)
            category.setWindowOpacity(self.OPACITY_LEVEL)
            for tool in categoryData.items:
                btn = self.buildCategoryAction(tool, icon_size)
                btn.setParent(category)
                if btn:
                    if self.horizontalMode: category.addTool(btn, x, y, toolbox_item_alignment)
                    else: category.addTool(btn, y, x, toolbox_item_alignment)

                    x = x + 1
                    if x >= specific_col_max: 
                        x = 0
                        y = y + 1
                        
            self.categories.append(category)
            self.viewportLayout.addWidget(category, 0, toolbox_item_alignment)
            x = 0
            y = y + 1
        self.updateCheckedStates()

    def buildCategoryAction(self, tool: ToolboxDataItem, icon_size: int):
        ac = Krita.instance().action(tool.name)
        if ac:
            actionText = ac.toolTip()
            btn: ToolboxButton = ToolboxButton(tool.name)
            btn.setWindowOpacity(self.OPACITY_LEVEL)
            btn.setObjectName(tool.name)
            btn.setText(actionText)
            btn.setIcon(self.buildActionIcon(tool.name, tool.icon))
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            btn.setIconSize(QSize(icon_size, icon_size))
            btn.setToolTip(actionText)
            btn.setStyle(ToolboxStyle("fusion", self.layout_config.submenu_delay))

            if len(tool.items) >= 1:
                btn.released.connect(self.activateTool) # Activate when released
            else:
                btn.pressed.connect(self.activateTool) # Activate when pressed

            if tool.name in TOOLBOX_ITEMS:
                self.buttonGroup.addButton(btn)
                btn.setCheckable(True)
                btn.setAutoRaise(True)
                self.registeredToolBtns.append(btn)

            if len(tool.items) >= 1:
                subMenu = ToolboxMenu(btn, tool)
                btn.setMenu(subMenu) # this will be the submenu for each main tool

                btn.menu().aboutToShow.connect(self.activateMenu) # Show submenu when clicked
                if tool.open_on_click == True:
                    btn.menu().aboutToShow.connect(self.activateMenu)
            return btn
        return None

    def buildMenu(self, subMenu: ToolboxMenu):
        self.buildMenuAction(subMenu, subMenu.tool.name, subMenu.tool.icon)
        for toolItem in subMenu.items: # iterate through all the tools in the category
            toolItem: ToolboxDataSubitem
            self.buildMenuAction(subMenu, toolItem.name, toolItem.icon)

        for action in subMenu.actions(): # show tool icons in submenu
            action.setIconVisibleInMenu(True)

    def buildMenuAction(self, subMenu: ToolboxMenu, actionName: str, iconName: str):
        act = Krita.instance().action(actionName)
        if act:
            toolIcon = self.buildActionIcon(actionName, iconName)
            toolText = act.toolTip()
            toolName = actionName
            toolAction = QAction(toolIcon, toolText, subMenu) # set up initial toolAction

            # we need to call Krita's shortcut for the toolAction:
            try:
                Krita.instance().action(toolName).shortcut()

                toolShortcut = Krita.instance().action(toolName).shortcut().toString() # find the global shortcut

                toolAction.setShortcut(toolShortcut)

            except:
                pass

            toolAction.setObjectName(toolName)
            toolAction.setParent(subMenu.parentBtn) # set toolbutton as parent
            toolAction.triggered.connect(self.swapToolButton) # activate menu tool on click
            toolAction.triggered.connect(self.activateTool) # activate menu tool on click
            subMenu.addAction(toolAction) # add the button for this tool in the menu

    def buildActionIcon(self, actionName: str, iconName: str):
        act = Krita.instance().action(actionName)

        if iconName and iconName != "":
            customIcon = ResourceManager.iconLoader(iconName)
            if customIcon: return QIcon(customIcon)
        elif act: return QIcon(act.icon())
        else: return QIcon()



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
        ac = Krita.instance().action(actionName) # Search this name in Krita's action list

        #print(actionName, ac)
        if ac:
            ac.trigger() # trigger the action in Krita

        else:
            pass
    
    def changePreset(self):
        ac: QAction = self.sender()
        if isinstance(ac, QAction):
            id: str = ac.data()
            if isinstance(id, str):
                TouchifySettings.instance().setActiveToolbox(id)
                self.reload()
    
    def setHorizontalMode(self, state: bool):
        self.horizontalMode = state
        KritaSettings.writeSettingBool(TOUCHIFY_ID_DOCKER_TOOLBOX, "IsHorizontal", self.horizontalMode)
        self.reload()

    def toggleHorizontalMode(self):
        self.horizontalMode = not self.horizontalMode
        KritaSettings.writeSettingBool(TOUCHIFY_ID_DOCKER_TOOLBOX, "IsHorizontal", self.horizontalMode)
        self.reload()
    #endregion

    def canvasChanged(self, canvas):
        pass