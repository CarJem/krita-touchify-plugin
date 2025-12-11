# This Python file uses the following encoding: utf-8
from uuid import uuid4
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from krita import *



from touchify.src.api_krita.wrappers.window import WindowAPI
from touchify.__env__ import *
from touchify.src.components.toolbox.ToolboxLayout import ToolboxEmptySpace
from touchify.src.components.toolbox.ToolboxOptionsDialog import ToolboxOptionsDialog
from touchify.src.config.toolbox.ToolboxData import ToolboxData
from touchify.src.managers.shared.events import GlobalEvents
from touchify.__env__ import *

from touchify.src.components.toolbox.ToolboxLoader import ToolboxLoader
from touchify.src.components.toolbox.ToolboxWidget import ToolboxWidget
from touchify.src.components.toolbox.ToolboxMenu import ToolboxMenu
from touchify.src.components.toolbox.ToolboxScrollArea import ToolboxScrollArea
from touchify.src.config.toolbox.ToolboxDataCategory import ToolboxDataCategory
from touchify.src.config.toolbox.ToolboxDataItem import ToolboxDataItem
from touchify.src.managers.shared.settings import TouchifySettings
import touchify.src.extensions.pyqt_extensions as PyQtExtensions

from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
    from touchify.src.PluginManagers import TouchifyManagers
    from ...PluginWindow import TouchifyWindow

    

DOCKER_TITLE=f"{TOUCHIFY_TITLES_CORE_DOCKERS_PREFIX} Toolbox"

class ToolboxDocker(QDockWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        #self.floating = False
        self.setWindowTitle(DOCKER_TITLE) # window title also acts as the Docker title in Settings > Dockers
        self.setContentsMargins(0,0,0,0)

        #label = QLabel(" ") # label conceals the 'exit' buttons and Docker title
        #label.setFrameShape(QFrame.StyledPanel)
        #label.setFrameShadow(QFrame.Raised)
        #label.setFrameStyle(QFrame.Panel | QFrame.Raised)
        #label.setMinimumWidth(16)

        self.settingsMenu = QMenu(self)

        self.api_window: WindowAPI = None
        self.managers: "TouchifyManagers" = None
        self.containerLoader = ToolboxLoader(self)
        self._toolboxItems: list[QWidgetAction] = []
        self.isDynamicOrientation = False
        self.isNotLoading = True
        self.dlgConfigEditor: ToolboxOptionsDialog = None

        self._toolbox = ToolboxWidget()
        self._toolbox.sigContextMenuRequested.connect(self.onContext)
        self.scrollArea = ToolboxScrollArea(self, self._toolbox)
        self.scrollArea.setContentsMargins(0,0,0,0)
        self.scrollArea.setViewportMargins(0,0,0,0)
        self.scrollArea.setWidgetResizable(True)
        self.setWidget(self.scrollArea)

        self.updateStyleSheet()

        GlobalEvents.instance().SIGNAL_TOUCHIFY_CONFIG_UPDATED.connect(self.onConfigUpdated)
        GlobalEvents.instance().SIGNAL_TOUCHIFY_TOOLBOX_PRESET_CHANGED.connect(self.onConfigUpdated)
        
    def __setupDialog(self, options: Any):
        if self.dlgConfigEditor != None:
            if PyQtExtensions.CommonHelpers.isDeleted(self.dlgConfigEditor) == False:
                return None
        
        self.dlgConfigEditor = ToolboxOptionsDialog(self.api_window, options)
        return self.dlgConfigEditor
    
    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)
        if self.isFloating() and self.isNotLoading and self.isDynamicOrientation:
            if (self.width() > self.height()):
                self.setOrientation(Qt.Orientation.Horizontal)
            else:
                self.setOrientation(Qt.Orientation.Vertical)

    def sync(self):
        self.isNotLoading = False

        self._toolbox.reset()
        self._toolboxItems.clear()
        self._toolboxItems = []

        layout_config = TouchifySettings.instance().getActiveToolbox()
        self.containerLoader.Sync(layout_config)
        current_priority = 0
        


        self.settingsMenu.clear()
        self.settingsMenu = self.containerLoader.Build_Context()

        orientation = Qt.Orientation.Vertical
        match layout_config.orientation_mode:
            case ToolboxData.OrientationMode.Dynamic:
                self.isDynamicOrientation = True
            case ToolboxData.OrientationMode.Vertical:
                self.isDynamicOrientation = False
                orientation = Qt.Orientation.Vertical
            case ToolboxData.OrientationMode.Horizontal:
                self.isDynamicOrientation = False
                orientation = Qt.Orientation.Horizontal

        max_column_count = layout_config.column_count
        for cat in layout_config.categories:
            cat: ToolboxDataCategory
            if cat.column_count > max_column_count:
                max_column_count = cat.column_count
        
        
        for cat in layout_config.categories:
            cat: ToolboxDataCategory
            item_count = 0
            for act in cat.items:    
                act: ToolboxDataItem
                btn = self.containerLoader.Build_Action(act)
                if btn:
                    self._toolbox.addButton(btn, cat.id, current_priority, str(uuid4()))
                    self._toolboxItems.append(btn)
                    current_priority += 1
                    item_count += 1

            if max_column_count > item_count:
                for idx in range(item_count, max_column_count):
                    btn = ToolboxEmptySpace()
                    self._toolbox.addButton(btn, cat.id, current_priority, str(uuid4()))
                    self._toolboxItems.append(btn)
                    current_priority += 1


        self._toolbox.setIconSize(layout_config.icon_size)
        self._toolbox.setDesiredRowCount(max_column_count)
        self._toolbox.setButtonsVisible([])
        self._toolbox.applyIconSize()
        self.setOrientation(orientation)
        self.updateStyleSheet()

        self.isNotLoading = True
    

    def onContext(self, pos: QPoint):
        self.settingsMenu.exec_(pos)

    def onActionMenu(self):
        subMenu: ToolboxMenu = self.sender() # link the toolbutton menu to this function
        if subMenu.isEmpty(): # prevents the menu from continuously adding actions every click
            self.buildMenu(subMenu)

    def onSettings(self):
        layout_config = TouchifySettings.instance().getActiveToolbox()
        dlg = self.__setupDialog(layout_config)
        if dlg.exec_():
            result: ToolboxData = dlg.editableConfig
            cached_state = TouchifySettings.instance().getActiveToolbox()
            cached_state.update(result)
            TouchifySettings.instance().getConfig().save()
            TouchifySettings.instance().reloadToolbox()
        

    def updatePalette(self):
        pass

    def updateStyleSheet(self):
        layout_config = TouchifySettings.instance().getActiveToolbox()

        highlight_hex = qApp.palette().color(QPalette.ColorRole.Highlight).name().split("#")[1]
        background_hex = qApp.palette().color(QPalette.ColorRole.Base).name().split("#")[1]
        alternate_hex = qApp.palette().color(QPalette.ColorRole.AlternateBase).name().split("#")[1]
        inactive_text_color_hex = qApp.palette().color(QPalette.ColorRole.ToolTipText).name().split("#")[1]
        active_text_color_hex = qApp.palette().color(QPalette.ColorRole.WindowText).name().split("#")[1]

        background_opacity = layout_config.background_opacity
        alternative_opacity = layout_config.button_opacity

        if background_opacity > 255: background_opacity = 255
        if background_opacity < 0: background_opacity = 0

        if alternative_opacity > 255: alternative_opacity = 255
        if alternative_opacity < 0: alternative_opacity = 0


        bg_opacity_hex = hex(background_opacity)[2:]
        alt_opacity_hex = hex(alternative_opacity)[2:]


        if self.scrollArea.orientation() == Qt.Orientation.Horizontal:
            frame_style = f"""
                QFrame {{ 
                    background-color: #{bg_opacity_hex}{background_hex};
                    border-radius: 4px;
                    padding: 0px;
                }}
            """
            #TODO: Add a Variant of this that Uses Seperators?
            #   border-right: 1px solid #{inactive_text_color_hex};
            #   border-radius: 0px;
        else:
            frame_style = f"""
                QFrame {{ 
                    background-color: #{bg_opacity_hex}{background_hex};
                    border-radius: 4px;
                    padding: 0px;
                }}
            """
            #TODO: Add a Variant of this that Uses Seperators?
            #   border-bottom: 1px solid #{inactive_text_color_hex};
            #   border-radius: 0px;
        
    
        self.setStyleSheet(f"""
            {frame_style}

            QScrollArea {{ background: transparent; }}
            QScrollArea > QWidget > QWidget {{ background: transparent; }}
            QScrollArea > QWidget > QScrollBar {{ background: palette(base); }}
            
            TouchifyActionButton {{
                background-color: #{alt_opacity_hex}{background_hex};
                border: 1px solid transparent;
                border-radius: 4px;
            }}
            
            TouchifyActionButton[toggled="true"] {{
                background-color: #{alt_opacity_hex}{highlight_hex};
            }}

            TouchifyActionButton[menu_toggled="true"] {{
                border: 1px solid #{alt_opacity_hex}{highlight_hex};
            }}
            
            TouchifyActionButton:hover {{
                background-color: #{alt_opacity_hex}{highlight_hex};
            }}
            
            TouchifyActionButton:pressed {{
                background-color: #{alt_opacity_hex}{alternate_hex};
            }}
        """)

    def setOrientation(self, orientation: Qt.Orientation):
        self.scrollArea.setOrientation(orientation)
        self.updateStyleSheet()

    def onConfigUpdated(self):
        self.sync()

    def setup(self, instance: "TouchifyWindow"):
        self.api_window = instance.api_window
        self.managers = instance.managers
        self.sync()

    def canvasChanged(self, canvas):
        pass