from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from touchify.src.components.touchify.dockers.toolshelf.ToolshelfWidget import ToolshelfWidget

from touchify.src.cfg.action.CfgTouchifyActionPopup import CfgTouchifyActionPopup
from touchify.src.settings import *
from touchify.src.resources import *
from touchify.src.components.touchify.popups.PopupDialog import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from touchify.src.docker_manager import DockerManager
    from touchify.src.action_manager import ActionManager

from krita import *


class PopupDialog_Toolshelf(PopupDialog):



    def __init__(self, parent: QWidget, args: CfgTouchifyActionPopup, action_manager: "ActionManager", docker_manager: "DockerManager"):     
        super().__init__(parent, args)

        self.docker_manager: "DockerManager" = docker_manager
        self.actions_manager: "ActionManager" = action_manager
        self.toolshelf_data = args.toolshelf_data

        self.window_allow_resize = self.toolshelf_data.header_options.default_to_resize_mode

        self.grid = QVBoxLayout(self)
        self.grid.setContentsMargins(0,0,0,0)
        self.grid.setSpacing(0)
        self.initLayout()

        self.mainWidget = ToolshelfWidget(self, self.toolshelf_data)
        self.mainWidget.sizeChanged.connect(self.requestViewUpdate)
        self.grid.addWidget(self.mainWidget)
        self.createActions()

    def allowResizingChanged(self):
        self.window_allow_resize = self.action_toggleResize.isChecked()
        self.requestViewUpdate()

    def createActions(self):
        self.action_toggleResize = QAction(self)
        self.action_toggleResize.setText("Allow resizing")
        self.action_toggleResize.setCheckable(True)
        self.action_toggleResize.setChecked(self.window_allow_resize)
        self.action_toggleResize.setEnabled(self.windowMode == CfgTouchifyActionPopup.WindowType.Window)
        self.action_toggleResize.changed.connect(self.allowResizingChanged)

    def hasPanelStack(self):
        if hasattr(self, "panelStack"):
            if self.mainWidget:
                return True
        return False
    
    def requestViewUpdate(self):
        size = self.generateSize()
        self.updateSize(size[0], size[1])

    def shutdownWidget(self):
        if self.mainWidget:
            self.mainWidget.shutdownWidget()
            self.mainWidget.deleteLater()
            self.mainWidget = None
        super().shutdownWidget()
    
    def closeEvent(self, event):
        super().closeEvent(event)
   
    def generateSize(self):
        if self.windowMode == CfgTouchifyActionPopup.WindowType.Popup and self.mainWidget:
            dialog_width = self.mainWidget.sizeHint().width()
            dialog_height = self.mainWidget.sizeHint().height()
        else:
            dialog_width = self.minimumSizeHint().width()
            dialog_height = self.minimumSizeHint().height()

        return [int(dialog_width), int(dialog_height)]


    def triggerPopup(self, parent: QWidget | None):
        super().triggerPopup(parent)
