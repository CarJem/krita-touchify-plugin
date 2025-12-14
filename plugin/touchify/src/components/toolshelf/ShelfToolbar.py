from functools import partial
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QPushButton, QSizePolicy
from krita import *
from PyQt5.QtWidgets import *


from touchify.src.api_krita import KritaAPI


from touchify.src.components.toolshelf.ShelfToolbarMenu import ShelfToolbarMenu
from touchify.src.config.toolshelf.ToolshelfAreaSettings import ToolshelfAreaSettings
from touchify.src.config.toolshelf.ToolshelfArea import ToolshelfArea
from touchify.src.settings.TouchifySettings import TouchifySettings
from touchify.__env__ import *
from touchify.src.managers.ResourceManager import ResourceManager

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .ShelfWidget import ShelfWidget



class ShelfToolbar(QWidget):
    def __init__(self, parent_toolshelf: "ShelfWidget"):
        super(ShelfToolbar, self).__init__(parent_toolshelf)

        self.shelf: ShelfWidget = parent_toolshelf
        
        self.setObjectName("toolshelf-header")
        self.setContentsMargins(0,0,0,0)

        self.ourLayout = QGridLayout(self)
        self.ourLayout.setSpacing(0)
        self.ourLayout.setContentsMargins(0,0,0,0)
        self.setLayout(self.ourLayout)

        self.optionsMenu = ShelfToolbarMenu(self, self.shelf.currentPresetId(), self.shelf.is_nested, self.shelf.is_restricted)
        self.optionsMenu.aboutToHide.connect(self.onHideSettings)
        self.optionsMenu.sigEditModeToggled.connect(self.shelf.onEditModeChanged)
        self.optionsMenu.sigAddShelfItemRequested.connect(self.shelf.addShelfItem)
        self.optionsMenu.sigSettingsRequested.connect(self.shelf.editLayout)
        self.optionsMenu.sigAddPageRequested.connect(self.shelf.insertPage)
        self.optionsMenu.sigEditPageRequested.connect(self.shelf.editPage)
        self.optionsMenu.sigDeletePageRequested.connect(self.shelf.deletePage)
        self.optionsMenu.sigPresetsChangedRequested.connect(self.shelf.changePreset)
        self.optionsMenu.sigEditPresetRequested.connect(self.shelf.editPreset)
        self.optionsMenu.sigSavePresetAsRequested.connect(self.shelf.savePresetAs)
        self.optionsMenu.sigSavePresetRequested.connect(self.shelf.savePreset)
        self.optionsMenu.sigDeletePresetRequested.connect(self.shelf.deletePreset)
        self.optionsMenu.sigResetRequested.connect(partial(self.shelf.resetLayout, False))

        self.mainButton = QPushButton(self)
        self.mainButton.setIcon(ResourceManager.iconLoader("material:circle"))
        self.mainButton.setObjectName("menu-widget")
        self.mainButton.clicked.connect(self.showToolbarMenu)

        self.backButton = QPushButton(self)
        self.backButton.setIcon(KritaAPI.get_action('move_layer_up').icon())

        self.backButton.clicked.connect(self.openRootPage)
        self.backButton.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.backButton.setObjectName("back-widget")
        
        self.fillerWidget = QWidget(self)
        self.fillerWidget.setObjectName("filler-widget")

        self.pinButton = QPushButton(self)
        self.pinButton.setIcon(KritaAPI.get_icon('krita_tool_reference_images'))
        self.pinButton.setObjectName("pin-widget")
        self.pinButton.setCheckable(True)
        self.pinButton.clicked.connect(self.togglePinned)

        qApp.paletteChanged.connect(self.updateStyleSheet)
        self.updateStyleSheet()

    def reload(self, state: ToolshelfArea, currentPresetId: str):
        button_size = int(state.options.header_size * TouchifySettings.preferences().Interface_ToolshelfHeaderScale)
        icon_size = button_size - 4
        match state.options.position:
            case "top":
                orientation = Qt.Orientation.Horizontal
            case "left":
                orientation = Qt.Orientation.Vertical
            case "right":
                orientation = Qt.Orientation.Vertical
            case _:
                orientation = Qt.Orientation.Horizontal

        try: self.ourLayout.removeWidget(self.mainButton)
        except: pass
        try: self.ourLayout.removeWidget(self.backButton)
        except: pass
        try: self.ourLayout.removeWidget(self.fillerWidget)
        except: pass
        try: self.ourLayout.removeWidget(self.pinButton)
        except: pass
    
        self.mainButton.setIconSize(QSize(icon_size, icon_size))
        self.mainButton.setFixedHeight(button_size)
        self.mainButton.setFixedWidth(button_size)

        self.backButton.setIconSize(QSize(icon_size, icon_size))
        self.pinButton.setIconSize(QSize(icon_size, icon_size))

        self.pinButton.setFixedHeight(button_size)
        self.pinButton.setFixedWidth(button_size)

        if orientation == Qt.Orientation.Horizontal:
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            self.backButton.setFixedHeight(button_size)
            self.ourLayout.addWidget(self.mainButton, 0, 0)
            self.ourLayout.addWidget(self.backButton, 0, 1)
            self.ourLayout.addWidget(self.fillerWidget, 0, 1)
            self.ourLayout.addWidget(self.pinButton, 0, 2)
        else:
            self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
            self.backButton.setFixedWidth(button_size)
            self.ourLayout.addWidget(self.mainButton, 0, 0)
            self.ourLayout.addWidget(self.pinButton, 1, 0)
            self.ourLayout.addWidget(self.fillerWidget, 2, 0)
            self.ourLayout.addWidget(self.backButton, 2, 0)

        #self.mainButton.setVisible(not state.options.show_menu_button)
        self.pinButton.setVisible(state.options.enable_pinning)

        self.optionsMenu.reload(currentPresetId)


    #region Actions

    def showToolbarMenu(self):
        if self.shelf.is_restricted:
            return
        
        self.mainButton.setMenu(self.optionsMenu)
        self.mainButton.showMenu()
    
    def openRootPage(self):
        self.shelf.goToHomePage()
    
    def openPage(self, id: str):
        pass

    def togglePinned(self):
        pass

    def updateStyleSheet(self):
        stylesheet = f"""
            QWidget#toolshelf-header {{
                background-color: palette(alternate-base);
                border: none;
            }}

            QWidget#toolshelf-tablist-row {{
                background-color: palette(alternate-base);
                border: none;
            }}

            QPushButton, QToolButton {{
                background-color: palette(alternate-base);
                border: none;
            }}

            QPushButton:hover, QToolButton:hover {{
                background-color: palette(highlight);
            }}

            QPushButton:checked, QToolButton:checked {{
                background-color: palette(highlight);
            }}
            
            QPushButton:pressed, QToolButton:pressed {{
                background-color: palette(alternate-base);
            }}

            QPushButton#back-widget {{
                border-top-left-radius: 0px;
                border-bottom-left-radius: 0px;
                border: none;
            }}

            QPushButton#pin-widget {{
                border-top-right-radius: 0px;
                border-bottom-right-radius: 0px;
                border: none;
            }}

            QPushButton::menu-indicator, QToolButton::menu-indicator {{ 
                image: none; 
            }}

            QPushButton#menu-widget {{
                border-top-right-radius: 0px;
                border-bottom-right-radius: 0px;
                border: none;
            }}

            QWidget#filler-widget {{
                background-color: palette(alternate-base);
                border: none;
                border-top-left-radius: 0px;
                border-bottom-left-radius: 0px;
            }}
        """
        self.setStyleSheet(stylesheet)

    #endregion

    #region Getters / Setters

    def setPinned(self, value: bool):
        if self.pinButton:
            self.pinButton.setChecked(True if value else False)

    #endregion

    #region Signal Recievers

    def onHideSettings(self):
        self.mainButton.setMenu(None)

    def onPageChanged(self, index: int):
        self.optionsMenu.onPageChanged(index)
        if self.shelf.containerOptions.stack_preview == ToolshelfAreaSettings.StackPreview.Default:
            if index != -1:
                self.backButton.show()
                self.fillerWidget.hide()
            else:
                self.backButton.hide()
                self.fillerWidget.show()
        else:
            self.backButton.hide()
            self.fillerWidget.show()

    #endregion


