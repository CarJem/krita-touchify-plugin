from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QPushButton, QSizePolicy
from krita import *
from PyQt5.QtWidgets import *


from .ToolshelfMenu import ToolshelfMenu
from .ToolshelfTabList import ToolshelfTabList

from .....cfg.toolshelf.CfgToolshelfHeaderOptions import CfgToolshelfHeaderOptions
from .....cfg.toolshelf.CfgToolshelf import CfgToolshelf

from .....variables import *
from .....stylesheet import Stylesheet
from .....resources import ResourceManager

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .ToolshelfWidget import ToolshelfWidget

class ToolshelfHeader(QWidget):
    def __init__(self, parent_toolshelf: "ToolshelfWidget", cfg: CfgToolshelf, registry_index: int, orientation: Qt.Orientation):
        super(ToolshelfHeader, self).__init__(parent_toolshelf)

        self.parent_toolshelf: ToolshelfWidget = parent_toolshelf
        self.registry_index = registry_index
        self.is_menu_preloaded = False
        self.orientation = orientation
        self.cfg = cfg

        self.button_size = self.cfg.header_options.header_size
        self.icon_size = self.button_size - 4

        self.setObjectName("toolshelf-header")

        self.setContentsMargins(0,0,0,0)

        self.ourLayout = QGridLayout(self)
        self.ourLayout.setSpacing(0)
        self.ourLayout.setContentsMargins(0,0,0,0)
        self.setLayout(self.ourLayout)


        self.optionsMenu = ToolshelfMenu(self, self.cfg, self.registry_index)
        self.optionsMenu.aboutToHide.connect(self.onHideSettings)

        self.tabs = ToolshelfTabList(self, self.orientation)

        self.mainButton = QPushButton(self)
        self.mainButton.setIcon(ResourceManager.iconLoader("material:circle"))
        self.mainButton.setIconSize(QSize(self.icon_size, self.icon_size))
        self.mainButton.setFixedHeight(self.button_size)
        self.mainButton.setFixedWidth(self.button_size)
        self.mainButton.setObjectName("menu-widget")
        self.mainButton.clicked.connect(self.openSettings)

        self.backButton = QPushButton(self)
        self.backButton.setIcon(Krita.instance().action('move_layer_up').icon())
        self.backButton.setIconSize(QSize(self.icon_size, self.icon_size))
        self.backButton.clicked.connect(self.openRootPage)
        self.backButton.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.backButton.setObjectName("back-widget")
        

        self.fillerWidget = QWidget(self)
        self.fillerWidget.setObjectName("filler-widget")

        self.pinButton = QPushButton(self)
        self.pinButton.setIcon(Krita.instance().icon('krita_tool_reference_images'))
        self.pinButton.setIconSize(QSize(self.icon_size, self.icon_size))
        self.pinButton.setObjectName("pin-widget")
        self.pinButton.setCheckable(True)
        self.pinButton.setFixedHeight(self.button_size)
        self.pinButton.setFixedWidth(self.button_size)
        self.pinButton.clicked.connect(self.togglePinned)


        if self.orientation == Qt.Orientation.Horizontal:
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            self.backButton.setFixedHeight(self.button_size)
            self.ourLayout.addWidget(self.mainButton, 0, 0)
            self.ourLayout.addWidget(self.backButton, 0, 1)
            self.ourLayout.addWidget(self.fillerWidget, 0, 1)
            self.ourLayout.addWidget(self.pinButton, 0, 2)
            self.ourLayout.addWidget(self.tabs, 1, 0, 1, 3)
        else:
            self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
            self.backButton.setFixedWidth(self.button_size)
            self.ourLayout.addWidget(self.mainButton, 0, 0)
            self.ourLayout.addWidget(self.pinButton, 1, 0)
            self.ourLayout.addWidget(self.fillerWidget, 2, 0)
            self.ourLayout.addWidget(self.backButton, 2, 0)
            self.ourLayout.addWidget(self.tabs, 0, 1, 3, 1)
            

        qApp.paletteChanged.connect(self.updateStyleSheet)
        self.updateStyleSheet()


    #region Actions

    def openSettings(self):
        if self.registry_index != -1:
            self.mainButton.setMenu(self.optionsMenu)
            if self.is_menu_preloaded == False:
                self.optionsMenu.setup()
                self.is_menu_preloaded = True
            self.mainButton.showMenu()
    
    def openRootPage(self):
        if self.parent_toolshelf:
            self.parent_toolshelf.goHome()
    
    def openPage(self, id: str):
        if self.parent_toolshelf:
            self.parent_toolshelf.pages.changePanel(id)

    def togglePinned(self):
        if self.parent_toolshelf:
            self.parent_toolshelf.togglePinned()

    def updateStyleSheet(self):
        self.setStyleSheet(Stylesheet.instance().touchify_toolshelf_header)

    #endregion

    #region Getters / Setters

    def setPinned(self, value: bool):
        if self.pinButton:
            self.pinButton.setChecked(True if value else False)

    #endregion

    #region Signal Recievers

    def onPageChanged(self, current_panel_id: str):
        if self.cfg.header_options.stack_preview == CfgToolshelfHeaderOptions.StackPreview.Default:
            if current_panel_id != "ROOT":
                self.backButton.show()
                self.fillerWidget.hide()
            else:
                self.backButton.hide()
                self.fillerWidget.show()
        else:
            self.backButton.hide()
            self.fillerWidget.show()

        self.tabs.onPageChanged(current_panel_id)

    def onHideSettings(self):
        self.mainButton.setMenu(None)

    #endregion



