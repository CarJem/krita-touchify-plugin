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

        self.grid = QHBoxLayout(self)
        self.grid.setContentsMargins(0,0,0,0)
        self.grid.setSpacing(0)
        self.initLayout()

        stylesheet = f"""QScrollArea {{ background: transparent; }}
        QScrollArea > QWidget > ToolshelfContainer {{ background: transparent; }}
        """

        self.scrollArea = QScrollArea(self)
        self.scrollArea.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.scrollArea.setContentsMargins(0,0,0,0)
        self.scrollArea.setViewportMargins(0,0,0,0)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scrollArea.setStyleSheet(stylesheet)
        self.grid.addWidget(self.scrollArea)

        self.mainWidget = ToolshelfWidget(self, self.toolshelf_data)
        self.mainWidget.sizeChanged.connect(self.requestViewUpdate)
        self.scrollArea.setWidget(self.mainWidget)

    def hasPanelStack(self):
        if hasattr(self, "panelStack"):
            if self.mainWidget:
                return True
        return False
    
    def requestViewUpdate(self):
        size = self.generateSize()
        self.updateSize(size[0], size[1])

    def shutdownWidget(self):
        self.mainWidget.shutdownWidget()
        self.scrollArea.takeWidget()
        self.mainWidget.deleteLater()
        self.mainWidget = None
        super().shutdownWidget()
    
    def closeEvent(self, event):
        self.mainWidget.shutdownWidget()
        self.scrollArea.takeWidget()
        self.mainWidget.deleteLater()
        self.mainWidget = None
        super().closeEvent(event)
   
    def generateSize(self):
        if self.mainWidget != None:
            dialog_width = self.scrollArea.viewportSizeHint().width()
            dialog_height = self.scrollArea.viewportSizeHint().height()
            return [int(dialog_width + 14), int(dialog_height + 14)]
        else:
            dialog_width = self.sizeHint().width()
            dialog_height = self.sizeHint().height()
            return [int(dialog_width), int(dialog_height)]

    def triggerPopup(self, parent: QWidget | None):
        super().triggerPopup(parent)
