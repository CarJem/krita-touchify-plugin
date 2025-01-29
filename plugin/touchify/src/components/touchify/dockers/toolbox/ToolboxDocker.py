# This Python file uses the following encoding: utf-8
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from krita import *


from touchify.src.managers.shared.events import GlobalEvents
from touchify.variables import *
from touchify.src.components.touchify.dockers.toolbox.ToolboxWidget import ToolboxWidget

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .....window import TouchifyWindow

DOCKER_TITLE="Touchify Core: Toolbox"

class ToolboxDocker(QDockWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.floating = False
        self.setWindowTitle(DOCKER_TITLE) # window title also acts as the Docker title in Settings > Dockers
        self.setContentsMargins(0,0,0,0)

        label = QLabel(" ") # label conceals the 'exit' buttons and Docker title
        label.setFrameShape(QFrame.StyledPanel)
        label.setFrameShadow(QFrame.Raised)
        label.setFrameStyle(QFrame.Panel | QFrame.Raised)
        label.setMinimumWidth(16)

        self.toolboxWidget = ToolboxWidget(self)
        self.setWidget(self.toolboxWidget)

        GlobalEvents.instance().SIGNAL_TOUCHIFY_CONFIG_UPDATED.connect(self.onConfigUpdated)
        GlobalEvents.instance().SIGNAL_TOUCHIFY_TOOLBOX_PRESET_CHANGED.connect(self.onConfigUpdated)

    def onConfigUpdated(self):
        self.toolboxWidget.reload()

    def setup(self, instance: "TouchifyWindow"):
        self.toolboxWidget.setup(instance)