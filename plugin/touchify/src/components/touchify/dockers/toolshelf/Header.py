from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QPushButton, QSizePolicy
from krita import *
from PyQt5.QtWidgets import *


from touchify.src.components.touchify.dockers.toolshelf.Menu import Menu

from touchify.src.cfg.toolshelf.CfgToolshelfHeaderOptions import CfgToolshelfHeaderOptions
from touchify.src.cfg.toolshelf.CfgToolshelf import CfgToolshelf

from touchify.src.settings import TouchifyConfig
from touchify.src.variables import *
from touchify.src.stylesheet import Stylesheet
from touchify.src.resources import ResourceManager

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .ToolshelfWidget import ToolshelfWidget



class Header(QWidget):

    def __init__(self, parent_toolshelf: "ToolshelfWidget", cfg: CfgToolshelf, registry_index: int, orientation: Qt.Orientation):
        super(Header, self).__init__(parent_toolshelf)

        self.parent_toolshelf: ToolshelfWidget = parent_toolshelf
        self.registry_index = registry_index
        self.is_menu_preloaded = False
        self.orientation = orientation
        self.cfg = cfg

        self.button_size = int(self.cfg.header_options.header_size * TouchifyConfig.instance().preferences().Interface_ToolshelfHeaderScale)
        self.icon_size = self.button_size - 4

        self.setObjectName("toolshelf-header")

        self.setContentsMargins(0,0,0,0)

        self.ourLayout = QGridLayout(self)
        self.ourLayout.setSpacing(0)
        self.ourLayout.setContentsMargins(0,0,0,0)
        self.setLayout(self.ourLayout)


        self.optionsMenu = Menu(self, self.cfg, self.registry_index)
        self.optionsMenu.aboutToHide.connect(self.onHideSettings)

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
        else:
            self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
            self.backButton.setFixedWidth(self.button_size)
            self.ourLayout.addWidget(self.mainButton, 0, 0)
            self.ourLayout.addWidget(self.pinButton, 1, 0)
            self.ourLayout.addWidget(self.fillerWidget, 2, 0)
            self.ourLayout.addWidget(self.backButton, 2, 0)

        if not self.cfg.header_options.show_menu_button:
            self.mainButton.setVisible(False)

        if not self.cfg.header_options.show_pin_button:
            self.pinButton.setVisible(False)

            

        qApp.paletteChanged.connect(self.updateStyleSheet)
        self.updateStyleSheet()


    #region Actions

    def openSettings(self):
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

    def onHideSettings(self):
        self.mainButton.setMenu(None)

    #endregion



